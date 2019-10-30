# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import time
import random
import math
from typing import List
from collections import Counter, defaultdict
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
            self, eventhub_client, consumer_group_name, owner_id,
            partition_manager, ownership_timeout, partition_id,
    ):
        self.cached_parition_ids = []  # type: List[str]
        self.eventhub_client = eventhub_client
        self.fully_qualified_namespace = eventhub_client._address.hostname
        self.eventhub_name = eventhub_client.eh_name
        self.consumer_group_name = consumer_group_name
        self.owner_id = owner_id
        self.partition_manager = partition_manager
        self.ownership_timeout = ownership_timeout
        self.partition_id = partition_id
        self._initializing = True

    def claim_ownership(self):
        """Claims ownership for this EventProcessor
        """
        if not self.cached_parition_ids:
            self._retrieve_partition_ids()

        if self.partition_id is not None:
            if self.partition_id in self.cached_parition_ids:
                return [self.partition_id]
            else:
                raise ValueError(
                    "Wrong partition id:{}. The eventhub has partitions: {}.".
                        format(self.partition_id, self.cached_parition_ids))

        if self.partition_manager is None:
            return self.cached_parition_ids

        else:
            ownership_list = self.partition_manager.list_ownership(
                self.fully_qualified_namespace, self.eventhub_name, self.consumer_group_name
            )
            to_claim = self._balance_ownership(ownership_list, self.cached_parition_ids)
            claimed_list = self.partition_manager.claim_ownership(to_claim) if to_claim else None
            return [x["partition_id"] for x in claimed_list]

    def _retrieve_partition_ids(self):
        """List all partition ids of the event hub that the EventProcessor is working on.
        """
        self.cached_parition_ids = self.eventhub_client.get_partition_ids()

    def _balance_ownership(self, ownership_list, all_partition_ids):
        """Balances and claims ownership of partitions for this EventProcessor.
        """

        now = time.time()
        ownership_dict = {x["partition_id"]: x for x in ownership_list}  # put the list to dict for fast lookup
        not_owned_partition_ids = [pid for pid in all_partition_ids if pid not in ownership_dict]
        timed_out_partitions = [x for x in ownership_list
                                if x["last_modified_time"] + self.ownership_timeout < now]
        if self._initializing:  # greedily claim all available partitions when an EventProcessor is started.
            to_claim = timed_out_partitions
            for pid in not_owned_partition_ids:
                to_claim.append(
                    {
                        "fully_qualified_namespace": self.fully_qualified_namespace,
                        "partition_id": pid,
                        "eventhub_name": self.eventhub_name,
                        "consumer_group_name": self.consumer_group_name,
                        "owner_id": self.owner_id
                    }
                )
            self._initializing = False
            if to_claim:  # if no expired or unclaimed partitions, go ahead with balancing
                return to_claim

        timed_out_partition_ids = [ownership["partition_id"] for ownership in timed_out_partitions]
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
        # end of calculating expected count per owner

        to_claim = active_ownership_self
        if len(active_ownership_self) < expected_count_per_owner:
            # Either claims an inactive partition, or steals from other owners
            if claimable_partition_ids:  # claim an inactive partition if there is
                random_partition_id = random.choice(claimable_partition_ids)
                random_chosen_to_claim = ownership_dict.get(
                    random_partition_id,
                    {"fully_qualified_namespace": self.fully_qualified_namespace,
                     "partition_id": random_partition_id,
                     "eventhub_name": self.eventhub_name,
                     "consumer_group_name": self.consumer_group_name,
                     }
                )
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

    def get_checkpoints(self):
        if self.partition_manager:
            checkpoints = self.partition_manager.list_checkpoints(
                self.fully_qualified_namespace, self.eventhub_name, self.consumer_group_name)
            return {x["partition_id"]: x for x in checkpoints}
        else:
            return {}
