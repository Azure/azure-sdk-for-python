# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import time
import random
import math
from collections import Counter
from azure.eventhub.aio import EventHubClient


class OwnershipManager(object):
    """Increases or decreases the number of partitions owned by an EventProcessor
    so the number of owned partitions are balanced among multiple EventProcessors

    An EventProcessor calls claim_ownership() of this class every x seconds,
    where x is set by keyword argument "polling_interval" in EventProcessor,
    to claim the ownership of partitions, create tasks for the claimed ownership, and cancel tasks that no longer belong
    to the claimed ownership.

    """
    def __init__(self, event_processor, eventhub_client: EventHubClient, ownership_timeout: int):
        self.all_parition_ids = []
        self.eventhub_client = eventhub_client
        self.eventhub_name = eventhub_client.eh_name
        self.consumer_group_name = event_processor._consumer_group_name
        self.owner_id = event_processor._id
        self.partition_manager = event_processor._partition_manager
        self.ownership_timeout = ownership_timeout

    async def claim_ownership(self):
        """Claims ownership for this EventProcessor
        1. Retrieves all partition ids of an event hub from azure event hub service
        2. Retrieves current ownership list via this EventProcessor's PartitionManager.
        3. Balances number of ownership. Refer to _balance_ownership() for details.
        4. Claims the ownership for the balanced number of partitions.

        :return: List[Dict[Any]]
        """
        if not self.all_parition_ids:
            await self._retrieve_partition_ids()
        to_claim = await self._balance_ownership()
        claimed_list = await self._claim_ownership(to_claim)
        return claimed_list

    async def _retrieve_partition_ids(self):
        """List all partition ids of the event hub that the EventProcessor is working on.

        :return: List[str]
        """
        self.all_parition_ids = await self.eventhub_client.get_partition_ids()

    async def _balance_ownership(self):
        """Balances and claims ownership of partitions for this EventProcessor.
        The balancing algorithm is:
        1. Find partitions with inactive ownership and partitions that haven never been claimed before
        2. Find the number of active owners, including this EventProcessor, for all partitions.
        3. Calculate the average count of partitions that an owner should own.
        (number of partitions // number of active owners)
        4. Calculate the largest allowed count of partitions that an owner can own.
        math.ceil(number of partitions / number of active owners). This should be equal or 1 greater than the average count
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
        ownership_list = await self.partition_manager.list_ownership(self.eventhub_client.eh_name, self.consumer_group_name)
        ownership_dict = dict((x["partition_id"], x) for x in ownership_list)  # put the list to dict for fast lookup

        claimable_partition_ids = []  # partitions with inactive ownership and partitions that have never been claimed yet
        active_ownership_self = []  # active ownership of this EventProcessor
        active_ownership_count_group_by_owner = Counter()
        for partition_id in self.all_parition_ids:
            ownership = ownership_dict.get(partition_id)
            if not ownership:  # no ownership found for this partition. So it is claimable
                claimable_partition_ids.append(partition_id)
            else:
                last_modified_time = ownership["last_modified_time"]
                owner_id = ownership["owner_id"]
                now = time.time()
                if now > self.ownership_timeout + last_modified_time:  # ownership timed out. So it is claimable
                    claimable_partition_ids.append(partition_id)
                else:  # the ownership is still active
                    if owner_id == self.owner_id:  # partition is actively owned by this running EventProcessor
                        active_ownership_self.append(ownership)
                    active_ownership_count_group_by_owner[owner_id] = active_ownership_count_group_by_owner.get(owner_id, 0) + 1  # all active owners

        # calculate expected count per owner
        all_partition_count = len(self.all_parition_ids)
        owners_count = len(active_ownership_count_group_by_owner) + (1 if self.owner_id not in active_ownership_count_group_by_owner else 0)
        expected_count_per_owner = all_partition_count // owners_count
        most_count_allowed_per_owner = math.ceil(all_partition_count / owners_count)
        # end of calculating expected count per owner

        to_claim = active_ownership_self
        if len(active_ownership_self) > most_count_allowed_per_owner:  # needs to abandon a partition
            to_claim.pop()  # abandon one partition if owned too many
            # TODO: Release a ownership immediately so other EventProcessors won't need to wait it to timeout
        elif len(active_ownership_self) < expected_count_per_owner:  # Either claims an inactive partition, or steals from other owners
            if claimable_partition_ids:  # claim an inactive partition if there is
                random_partition_id = random.choice(claimable_partition_ids)
                random_chosen_to_claim = ownership_dict.get(random_partition_id,
                                                            {"partition_id": random_partition_id,
                                                             "eventhub_name": self.eventhub_client.eh_name,
                                                             "consumer_group_name": self.consumer_group_name,
                                                             "owner_level": 0})  # TODO: consider removing owner_level
                random_chosen_to_claim["owner_id"] = self.owner_id
                to_claim.append(random_chosen_to_claim)
            else:  # steal from another owner that has the most count
                most_frequent_owner_id = active_ownership_count_group_by_owner.most_common(1)[0][0]
                # randomly choose a partition to steal from the most_frequent_owner
                to_steal_partition = random.choice(list(filter(lambda x: x["owner_id"] == most_frequent_owner_id,
                                                   ownership_list)))
                to_steal_partition["owner_id"] = self.owner_id
                to_claim.append(to_steal_partition)
        return to_claim

    async def _claim_ownership(self, ownership_list):
        if ownership_list:
            claimed_list = await self.partition_manager.claim_ownership(ownership_list)
            return claimed_list
        else:
            return None
