# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Iterable, Dict, Any
import logging
from collections import defaultdict
import asyncio
from azure.core.exceptions import ResourceModifiedError, ResourceExistsError
from azure.storage.blob.aio import ContainerClient

logger = logging.getLogger(__name__)
UPLOAD_DATA = ""


class BlobPartitionManager(object):
    def __init__(self, container_client: ContainerClient):
        self._container_client = container_client
        self._cached_ownership_dict = defaultdict(dict)
        self._lock = asyncio.Lock()

    async def list_ownership(self, eventhub_name: str, consumer_group_name: str) -> Iterable[Dict[str, Any]]:
        async with self._lock:
            blobs = self._container_client.list_blobs(include=['metadata'])
            # result = []
            async for b in blobs:
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
        async with self._lock:
            for ownership in ownership_list:
                metadata = {"owner_id": ownership["owner_id"]}
                if "offset" in ownership:
                    metadata["offset"] = ownership["offset"]
                if "sequence_number" in ownership:
                    metadata["sequence_number"] = ownership["sequence_number"]
                partition_id = ownership["partition_id"]
                try:
                    etag = ownership.get("etag")
                    if etag:
                        etag_match = {"if_match": '"'+etag+'"'}
                    else:
                        etag_match = {"if_none_match": '"*"'}
                    blob_client = await self._container_client.upload_blob(
                        name=partition_id, data=UPLOAD_DATA, overwrite=True, metadata=metadata, **etag_match
                    )
                    uploaded_blob_properties = await blob_client.get_blob_properties()
                    ownership["etag"] = uploaded_blob_properties.etag
                    ownership["last_modified_time"] = uploaded_blob_properties.last_modified.timestamp()
                    self._cached_ownership_dict[partition_id] = ownership
                except (ResourceModifiedError, ResourceExistsError):
                    logger.info("Partition %r was claimed by another EventProcessor", partition_id)
                except Exception as err:
                    logger.warning("Claim error occurred: %r", err)
                result.append(ownership)
        return result

    async def update_checkpoint(self, eventhub_name, consumer_group_name, partition_id, owner_id,
                                offset, sequence_number) -> None:

        metadata = {
            "owner_id": owner_id,
            "offset": offset,
            "sequence_number": str(sequence_number)
        }
        async with self._lock:
            try:
                blob_client = await self._container_client.upload_blob(
                    name=partition_id, data=UPLOAD_DATA, metadata=metadata, overwrite=True)
                uploaded_blob_properties = await blob_client.get_blob_properties()
                cached_ownership = self._cached_ownership_dict[partition_id]
                cached_ownership["etag"] = uploaded_blob_properties.etag
                cached_ownership["last_modified_time"] = uploaded_blob_properties.last_modified.timestamp()
            except (ResourceModifiedError, ResourceExistsError):
                logger.info("Partition %r was claimed by another EventProcessor", partition_id)
            except Exception as err:
                logger.warning("Checkpoint error occurred: %r", err)
                raise
