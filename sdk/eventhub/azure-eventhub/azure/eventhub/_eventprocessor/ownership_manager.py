# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations
import math
import time
import random
from collections import Counter, defaultdict
from typing import List, Iterable, Optional, Dict, Any, Union, TYPE_CHECKING

from .common import LoadBalancingStrategy

if TYPE_CHECKING:
    from .checkpoint_store import CheckpointStore
    from .._consumer_client import EventHubConsumerClient
    from .._producer_client import EventHubProducerClient


class OwnershipManager:  # pylint:disable=too-many-instance-attributes
    """Increases or decreases the number of partitions owned by an EventProcessor
    so the number of owned partitions are balanced among multiple EventProcessors

    An EventProcessor calls claim_ownership() of this class every x seconds,
    where x is set by keyword argument "load_balancing_interval" in EventProcessor,
    to claim the ownership of partitions, create tasks for the claimed ownership, and cancel tasks that no longer belong
    to the claimed ownership.

    """

    def __init__(
        self,
        eventhub_client: Union[EventHubConsumerClient, EventHubProducerClient],
        consumer_group: str,
        owner_id: str,
        checkpoint_store: Optional[CheckpointStore],
        ownership_timeout: float,
        load_balancing_strategy: LoadBalancingStrategy,
        partition_id: Optional[str],
    ):
        self.cached_parition_ids: List[str] = []
        self.owned_partitions: Iterable[Dict[str, Any]] = []
        self.eventhub_client = eventhub_client
        self.fully_qualified_namespace = eventhub_client._address.hostname
        self.eventhub_name = eventhub_client.eventhub_name
        self.consumer_group = consumer_group
        self.owner_id = owner_id
        self.checkpoint_store = checkpoint_store
        self.ownership_timeout = ownership_timeout
        self.load_balancing_strategy = load_balancing_strategy
        self.partition_id = partition_id

    def claim_ownership(self) -> List[str]:
        """Claims ownership for this EventProcessor

        :return: The list of partition ids that the EventProcessor claimed.
        :rtype: list[str]
        """
        if not self.cached_parition_ids:
            self._retrieve_partition_ids()

        if self.partition_id is not None:
            if self.partition_id in self.cached_parition_ids:
                return [self.partition_id]
            raise ValueError(
                "Wrong partition id:{}. The eventhub has partitions: {}.".format(
                    self.partition_id, self.cached_parition_ids
                )
            )

        if self.checkpoint_store is None:
            return self.cached_parition_ids

        ownership_list = self.checkpoint_store.list_ownership(
            self.fully_qualified_namespace, self.eventhub_name, self.consumer_group
        )
        to_claim = self._balance_ownership(ownership_list, self.cached_parition_ids)
        self.owned_partitions = self.checkpoint_store.claim_ownership(to_claim) if to_claim else []
        return [x["partition_id"] for x in self.owned_partitions]

    def release_ownership(self, partition_id: str) -> None:
        """Explicitly release ownership of a partition if we still have it.

        This is called when a consumer is shutdown, and is achieved by resetting the associated
        owner ID.

        :param partition_id: The partition id to release ownership.
        :type partition_id: str
        """
        if not self.checkpoint_store:
            return
        now = time.time()
        partition_ownership = [
            o
            for o in self.owned_partitions
            if o["partition_id"] == partition_id
            and o["owner_id"] == self.owner_id
            and o["last_modified_time"] + self.ownership_timeout > now
        ]
        if not partition_ownership:
            return
        partition_ownership[0]["owner_id"] = ""
        self.checkpoint_store.claim_ownership(partition_ownership)

    def _retrieve_partition_ids(self) -> None:
        """List all partition ids of the event hub that the EventProcessor is working on."""
        self.cached_parition_ids = self.eventhub_client.get_partition_ids()

    def _balance_ownership(  # pylint:disable=too-many-locals
        self, ownership_list: Iterable[Dict[str, Any]], all_partition_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """Balances and claims ownership of partitions for this EventProcessor.

        :param ownership_list: The list of current ownership.
        :type ownership_list: iterable[dict[str,any]]
        :param all_partition_ids: The list of all partition ids of the event hub that the EventProcessor is working on.
        :type all_partition_ids: list[str]
        :return: The balanced list of ownership that the EventProcessor claimed.
        :rtype: list[dict[str, any]]

        """
        now = time.time()
        ownership_dict = {x["partition_id"]: x for x in ownership_list}  # put the list to dict for fast lookup
        unclaimed_partition_ids = [pid for pid in all_partition_ids if pid not in ownership_dict]
        released_partitions = [
            x for x in ownership_list if x["last_modified_time"] + self.ownership_timeout < now or not x["owner_id"]
        ]
        released_partition_ids = [ownership["partition_id"] for ownership in released_partitions]
        claimable_partition_ids = unclaimed_partition_ids + released_partition_ids

        active_ownership = [o for o in ownership_list if o not in released_partitions]
        active_ownership_by_owner: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for ownership in active_ownership:
            active_ownership_by_owner[ownership["owner_id"]].append(ownership)
        active_ownership_self = active_ownership_by_owner[self.owner_id]

        # calculate expected and max count per owner
        all_partition_count = len(all_partition_ids)
        # owners_count is the number of active owners. If self.owner_id is not yet among the active owners,
        # then plus 1 to include self. This will make owners_count >= 1.
        owners_count = len(active_ownership_by_owner) + (0 if self.owner_id in active_ownership_by_owner else 1)
        expected_count_per_owner = all_partition_count // owners_count
        # Py2 math.ceil() returns float, a/b return int if not divisable.
        # Py3 math.ceil() returns int, a/b return float if not divisable.
        max_count_per_owner = int(math.ceil(all_partition_count * 1.0 / owners_count))
        # end of calculating expected count per owner

        to_claim = active_ownership_self
        if len(active_ownership_self) < max_count_per_owner:
            to_try_steal = True
            if self.load_balancing_strategy is LoadBalancingStrategy.GREEDY:
                # Greedily claim more partitions if there are claimable partitions
                to_greedy_claim_ids = random.sample(
                    claimable_partition_ids,
                    k=min(
                        max_count_per_owner - len(active_ownership_self),
                        len(claimable_partition_ids),
                    ),
                )
                if to_greedy_claim_ids:
                    for pid in to_greedy_claim_ids:
                        random_chosen_to_claim = ownership_dict.get(
                            pid,
                            {
                                "fully_qualified_namespace": self.fully_qualified_namespace,
                                "partition_id": pid,
                                "eventhub_name": self.eventhub_name,
                                "consumer_group": self.consumer_group,
                            },
                        )
                        random_chosen_to_claim["owner_id"] = self.owner_id
                        to_claim.append(random_chosen_to_claim)
                    to_try_steal = False  # already greedily got at least one
            else:  # self.load_balancing_strategy is LoadBalancingStrategy.BALANCED
                if claimable_partition_ids:  # claim an inactive partition if there is
                    random_partition_id = random.choice(claimable_partition_ids)
                    random_chosen_to_claim = ownership_dict.get(
                        random_partition_id,
                        {
                            "fully_qualified_namespace": self.fully_qualified_namespace,
                            "partition_id": random_partition_id,
                            "eventhub_name": self.eventhub_name,
                            "consumer_group": self.consumer_group,
                        },
                    )
                    random_chosen_to_claim["owner_id"] = self.owner_id
                    to_claim.append(random_chosen_to_claim)
                    to_try_steal = False  # already got one from claimable partition.
            if to_try_steal and len(active_ownership_self) < expected_count_per_owner:
                # steal from another owner that has the most count
                active_ownership_count_group_by_owner = Counter(
                    dict((x, len(y)) for x, y in active_ownership_by_owner.items())
                )
                most_frequent_owner_id = active_ownership_count_group_by_owner.most_common(1)[0][0]
                # randomly choose a partition to steal from the most_frequent_owner
                to_steal_partition = random.choice(active_ownership_by_owner[most_frequent_owner_id])
                to_steal_partition["owner_id"] = self.owner_id
                to_claim.append(to_steal_partition)
        return to_claim

    def get_checkpoints(self) -> Dict[str, Dict[str, Any]]:
        if self.checkpoint_store:
            checkpoints = self.checkpoint_store.list_checkpoints(
                self.fully_qualified_namespace, self.eventhub_name, self.consumer_group
            )
            return {x["partition_id"]: x for x in checkpoints}

        return {}
