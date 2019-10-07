# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Iterable, Dict, Any
import logging
from collections import defaultdict
import asyncio
from azure.eventhub.aio.eventprocessor import PartitionManager, OwnershipLostError  # type: ignore
from azure.core.exceptions import ResourceModifiedError, ResourceExistsError  # type: ignore
from azure.storage.blob.aio import ContainerClient, BlobClient  # type: ignore

logger = logging.getLogger(__name__)
UPLOAD_DATA = ""


class BlobPartitionManager(PartitionManager):
    """An PartitionManager that uses Azure Blob Storage to store the partition ownership and checkpoint data.

    This class implements methods list_ownership, claim_ownership, and update_checkpoint that are defined in class
    azure.eventhub.eventprocessor.PartitionManager of package azure-eventhub.

    """
    def __init__(self, container_client: ContainerClient):
        """Create a BlobPartitionManager

        :param container_client: The Azure Blob Storage Container client that is used to save checkpoint data to Azure
        Blob Storage Container.
        """
        self._container_client = container_client
        self._cached_blob_clients = defaultdict()  # type:Dict[str, BlobClient]
        self._cached_ownership_dict = defaultdict(dict)  # type: Dict[str, Dict[str, Any]]
        # lock each partition for list_ownership, claim_ownership and update_checkpoint etag doesn't get out of sync
        # when the three methods are running concurrently
        self._cached_ownership_locks = defaultdict(asyncio.Lock)  # type:Dict[str, asyncio.Lock]

    def _get_blob_client(self, blob_name):
        result = self._cached_blob_clients.get(blob_name)
        if not result:
            result = self._container_client.get_blob_client(blob_name)
            self._cached_blob_clients[blob_name] = result
        return result

    async def _upload_blob(self, ownership, metadata):
        etag = ownership.get("etag")
        if etag:
            etag_match = {"if_match": etag}
        else:
            etag_match = {"if_none_match": '*'}
        partition_id = ownership["partition_id"]
        uploaded_blob_properties = await self._get_blob_client(partition_id).upload_blob(
            data=UPLOAD_DATA, overwrite=True, metadata=metadata, **etag_match
        )
        ownership["etag"] = uploaded_blob_properties["etag"]
        ownership["last_modified_time"] = uploaded_blob_properties["last_modified"].timestamp()
        ownership.update(metadata)

    async def list_ownership(self, eventhub_name: str, consumer_group_name: str) -> Iterable[Dict[str, Any]]:
        try:
            blobs = self._container_client.list_blobs(include=['metadata'])
        except Exception as err:  # pylint:disable=broad-except
            logger.warning("An exception occurred during list_ownership for eventhub %r consumer group %r. "
                           "Exception is %r", eventhub_name, consumer_group_name, err)
            raise
        async for b in blobs:
            async with self._cached_ownership_locks[b.name]:
                if b.name not in self._cached_ownership_dict \
                        or b.last_modified.timestamp() > self._cached_ownership_dict[b.name].get("last_modified_time"):
                    metadata = b.metadata
                    ownership = {
                        "eventhub_name": eventhub_name,
                        "consumer_group_name": consumer_group_name,
                        "partition_id": b.name,
                        "owner_id": metadata["owner_id"],
                        "etag": b.etag,
                        "last_modified_time": b.last_modified.timestamp() if b.last_modified else None
                    }
                    ownership.update(metadata)
                    self._cached_ownership_dict[b.name] = ownership
        return self._cached_ownership_dict.values()

    async def claim_ownership(self, ownership_list: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
        result = []
        for ownership in ownership_list:
            partition_id = ownership["partition_id"]
            eventhub_name = ownership["eventhub_name"]
            consumer_group_name = ownership["consumer_group_name"]
            owner_id = ownership["owner_id"]

            async with self._cached_ownership_locks[partition_id]:
                metadata = {"owner_id": ownership["owner_id"]}
                if "offset" in ownership:
                    metadata["offset"] = ownership["offset"]
                if "sequence_number" in ownership:
                    metadata["sequence_number"] = ownership["sequence_number"]
                try:
                    await self._upload_blob(ownership, metadata)
                    self._cached_ownership_dict[partition_id] = ownership
                    result.append(ownership)
                except (ResourceModifiedError, ResourceExistsError):
                    logger.info(
                        "EventProcessor instance %r of eventhub %r consumer group %r lost ownership to partition %r",
                        owner_id, eventhub_name, consumer_group_name, partition_id)
                except Exception as err:  # pylint:disable=broad-except
                    logger.warning("An exception occurred when EventProcessor instance %r claim_ownership for "
                                   "eventhub %r consumer group %r partition %r. The ownership is now lost. Exception "
                                   "is %r", owner_id, eventhub_name, consumer_group_name, partition_id, err)
        return result

    async def update_checkpoint(self, eventhub_name, consumer_group_name, partition_id, owner_id,
                                offset, sequence_number) -> None:
        metadata = {
            "owner_id": owner_id,
            "offset": offset,
            "sequence_number": str(sequence_number)
        }
        cached_ownership = self._cached_ownership_dict[partition_id]
        async with self._cached_ownership_locks[partition_id]:
            try:
                await self._upload_blob(cached_ownership, metadata)
            except (ResourceModifiedError, ResourceExistsError):
                logger.info(
                    "EventProcessor instance %r of eventhub %r consumer group %r couldn't update_checkpoint to "
                    "partition %r because the ownership has been stolen",
                    owner_id, eventhub_name, consumer_group_name, partition_id)
                raise OwnershipLostError()
            except Exception as err:
                logger.warning(
                    "EventProcessor instance %r of eventhub %r consumer group %r couldn't update_checkpoint to "
                    "partition %r because of unexpected error. Exception is %r",
                    owner_id, eventhub_name, consumer_group_name, partition_id, err)
                raise  # EventProcessor will catch the exception and handle it
