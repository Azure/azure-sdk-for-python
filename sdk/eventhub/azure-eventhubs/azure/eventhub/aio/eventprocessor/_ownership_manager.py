# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import time
import random
import math
from typing import List
from collections import Counter, defaultdict
from azure.eventhub.aio import EventHubClient
from .partition_manager import PartitionManager


class OwnershipManager(object):
    """Increases or decreases the number of partitions owned by an EventProcessor
    so the number of owned partitions are balanced among multiple EventProcessors

    An EventProcessor calls claim_ownership() of this class every x seconds,
    where x is set by keyword argument "polling_interval" in EventProcessor,
    to claim the ownership of partitions, create tasks for the claimed ownership, and cancel tasks that no longer belong
    to the claimed ownership.

    """
    def __init__(
            self, eventhub_client: EventHubClient, consumer_group_name: str, owner_id: str,
            partition_manager: PartitionManager, ownership_timeout: float
    ):
        self.cached_parition_ids = []  # type: List[str]
        self.eventhub_client = eventhub_client
        self.eventhub_name = eventhub_client.eh_name
        self.consumer_group_name = consumer_group_name
        self.owner_id = owner_id
        self.partition_manager = partition_manager
        self.ownership_timeout = ownership_timeout

    async def claim_ownership(self):
        """Claims ownership for this EventProcessor
        1. Retrieves all partition ids of an event hub from azure event hub service
        2. Retrieves current ownership list via this EventProcessor's PartitionManager.
        3. Balances number of ownership. Refer to _balance_ownership() for details.
        4. Claims the ownership for the balanced number of partitions.

        :return: List[Dict[Any]]
        """
        if not self.cached_parition_ids:
            await self._retrieve_partition_ids()
        to_claim = await self._balance_ownership(self.cached_parition_ids)
        claimed_list = await self.partition_manager.claim_ownership(to_claim) if to_claim else None
        return claimed_list

    async def _retrieve_partition_ids(self):
        """List all partition ids of the event hub that the EventProcessor is working on.

        :return: List[str]
        """
        self.cached_parition_ids = await self.eventhub_client.get_partition_ids()

    async def _balance_ownership(self, all_partition_ids):
        """Balances and claims ownership of partitions for this EventProcessor.
        The balancing algorithm is:
        1. Find partitions with inactive ownership and partitions that haven never been claimed before
        2. Find the number of active owners, including this EventProcessor, for all partitions.
        3. Calculate the average count of partitions that an owner should own.
        (number of partitions // number of active owners)
        4. Calculate the largest allowed count of partitions that an owner can own.
        math.ceil(number of partitions / number of active owners).
        This should be equal or 1 greater than the average count
        5. Adjust the number of partitions owned by this EventProcessor (owner)
            a. if this EventProcessor owns more than largest allowed count, abandon one partition
            b. if this EventProcessor owns less than average count, add one from the inactive or unclaimed partitions,
            or steal one from another owner that has the largest number of ownership among all owners (EventProcessors)
            c. Otherwise, no change to the ownership

        The balancing algorithm adjust one partition at a time to gradually build the balanced ownership.
        Ownership must be renewed to keep it active. So the returned result includes both existing ownership and
        the newly adjusted ownership.
        This method balances but doesn't claim ownership. The caller of this method tries to claim the result ownership
        list. But it may not successfully claim all of them because of concurrency. Other EventProcessors may happen to
        claim a partition at that time. Since balancing and claiming are run in infinite repeatedly,
        it achieves balancing among all EventProcessors after some time of running.

        :return: List[Dict[str, Any]], A list of ownership.
        """
        ownership_list = await self.partition_manager.list_ownership(
            self.eventhub_name, self.consumer_group_name
        )
        now = time.time()
        ownership_dict = {x["partition_id"]: x for x in ownership_list}  # put the list to dict for fast lookup
        not_owned_partition_ids = [pid for pid in all_partition_ids if pid not in ownership_dict]
        timed_out_partition_ids = [ownership["partition_id"] for ownership in ownership_list
                                   if ownership["last_modified_time"] + self.ownership_timeout < now]
        claimable_partition_ids = not_owned_partition_ids + timed_out_partition_ids
        active_ownership = [ownership for ownership in ownership_list
                            if ownership["last_modified_time"] + self.ownership_timeout >= now]
        active_ownership_by_owner = defaultdict(list)
        for ownership in active_ownership:
            active_ownership_by_owner[ownership["owner_id"]].append(ownership)
        active_ownership_self = active_ownership_by_owner[self.owner_id]

        # calculate expected count per owner
        all_partition_count = len(all_partition_ids)
        # owners_count is the number of active owners. If self.owner_id is not yet among the active owners,
        # then plus 1 to include self. This will make owners_count >= 1.
        owners_count = len(active_ownership_by_owner) + \
                       (0 if self.owner_id in active_ownership_by_owner else 1)
        expected_count_per_owner = all_partition_count // owners_count
        most_count_allowed_per_owner = math.ceil(all_partition_count / owners_count)
        # end of calculating expected count per owner

        to_claim = active_ownership_self
        if len(active_ownership_self) > most_count_allowed_per_owner:  # needs to abandon a partition
            to_claim.pop()  # abandon one partition if owned too many
        elif len(active_ownership_self) < expected_count_per_owner:
            # Either claims an inactive partition, or steals from other owners
            if claimable_partition_ids:  # claim an inactive partition if there is
                random_partition_id = random.choice(claimable_partition_ids)
                random_chosen_to_claim = ownership_dict.get(random_partition_id,
                                                            {"partition_id": random_partition_id,
                                                             "eventhub_name": self.eventhub_name,
                                                             "consumer_group_name": self.consumer_group_name
                                                             })
                random_chosen_to_claim["owner_id"] = self.owner_id
                to_claim.append(random_chosen_to_claim)
            else:  # steal from another owner that has the most count
                active_ownership_count_group_by_owner = Counter(
                    dict((x, len(y)) for x, y in active_ownership_by_owner.items()))
                most_frequent_owner_id = active_ownership_count_group_by_owner.most_common(1)[0][0]
                # randomly choose a partition to steal from the most_frequent_owner
                to_steal_partition = random.choice(active_ownership_by_owner[most_frequent_owner_id])
                to_steal_partition["owner_id"] = self.owner_id
                to_claim.append(to_steal_partition)
        return to_claim
