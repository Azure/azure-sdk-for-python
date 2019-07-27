from typing import Iterable, Dict, Any
from abc import ABC, abstractmethod


class PartitionManager(ABC):
    """Subclass this class to implement the read/write access to storage service.

    Users may do their own subclass for checkpoint storage.
    """

    @abstractmethod
    async def list_ownership(self, eventhub_name: str, consumer_group_name: str) -> Iterable[Dict[str, Any]]:
        """

        :param eventhub_name:
        :param consumer_group_name:
        :return: Iterable of dictionaries containing the following partition ownership information:
                eventhub_name
                consumer_group_name
                instance_id
                partition_id
                owner_level
                offset
                sequence_number
                last_modified_time
                etag
        """
        pass

    @abstractmethod
    async def claim_ownership(self, partitions: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update_checkpoint(self, eventhub_name, consumer_group_name, partition_id, instance_id,
                                offset, sequence_number) -> None:
        pass

    @abstractmethod
    async def close(self):
        pass
