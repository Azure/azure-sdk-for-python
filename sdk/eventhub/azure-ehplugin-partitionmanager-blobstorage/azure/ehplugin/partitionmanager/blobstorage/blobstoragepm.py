# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Iterable, Dict, Any
import logging
from collections import defaultdict
import asyncio

from azure.eventhub.eventprocessor import PartitionManager
from azure.storage.blob.aio import ContainerClient

logger = logging.getLogger(__name__)
UPLOAD_DATA = ""


class BlobPartitionManager(PartitionManager):
    def __init__(self, container_client: ContainerClient):
        self._container_client = container_client
        # self._ownership_cache = {}
        # self._ownership_locks = defaultdict(asyncio.Lock)

    async def list_ownership(self, eventhub_name: str, consumer_group_name: str) -> Iterable[Dict[str, Any]]:
        blobs = self._container_client.list_blobs(include=['metadata'])
        result = []
        async for b in blobs:
            metadata = b.metadata
            ownership = {
                "eventhub_name": eventhub_name,
                "consumer_group_name": consumer_group_name,
                "partition_id": b.name,
                "etag": b.etag,
                "last_modified_time": b.last_modified.timestamp() if b.last_modified else None
            }
            ownership.update(metadata)
            result.append(ownership)
        return result

    async def claim_ownership(self, ownership_list: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
        result = []
        for ownership in ownership_list:
            metadata = {"owner_id": ownership["owner_id"]}
            if "offset" in ownership:
                metadata["offset"] = ownership["offset"]
            if "sequence_number" in ownership:
                metadata["sequence_number"] = ownership["sequence_number"]
            name = ownership["partition_id"]
            try:
                etag = ownership.get("etag")
                if etag:
                    etag_match = {"if_match": '"'+etag+'"'}
                else:
                    etag_match = {"if_none_match": '"*"'}
                blob_client = await self._container_client.upload_blob(
                    name=name, data=UPLOAD_DATA, overwrite=True, metadata=metadata, **etag_match
                )

                uploaded_blob_properties = await blob_client.get_blob_properties()
                ownership["etag"] = uploaded_blob_properties.etag
                ownership["last_modified_time"] = uploaded_blob_properties.last_modified
            except Exception as err:
                logger.info("Claim error occurred: %r", err)
                raise
            result.append(ownership)
        return result

    async def update_checkpoint(self, eventhub_name, consumer_group_name, partition_id, owner_id,
                                offset, sequence_number) -> None:

        metadata = {
            "owner_id": owner_id,
            "offset": offset,
            "sequence_number": sequence_number
        }
        try:
            blob_client = await self._container_client.upload_blob(name=partition_id, data=UPLOAD_DATA, overwrite=True)

        except Exception as err:
            logger.info("Checkpoint error occurred: %r", err)
            raise
