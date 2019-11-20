# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Dict
import logging
import time
import calendar
from datetime import datetime
from collections import defaultdict

from azure.eventhub import CheckpointStore, OwnershipLostError  # type: ignore # pylint:disable=no-name-in-module
from azure.core.exceptions import ResourceModifiedError, ResourceExistsError  # type: ignore
from azure.storage.blob import BlobClient  # type: ignore

logger = logging.getLogger(__name__)
UPLOAD_DATA = ""


class BlobCheckpointStore(CheckpointStore):
    """An CheckpointStore that uses Azure Blob Storage to store the partition ownership and checkpoint data.

    This class implements methods list_ownership, claim_ownership, update_checkpoint and list_checkpoints that are
    defined in class azure.eventhub.aio.CheckpointStore of package azure-eventhub.

    """
    def __init__(self, container_client):
        # type(ContainerClient) -> None
        """Create a BlobCheckpointStore

        :param container_client: The Azure Blob Storage Container client that is used to save checkpoint data to Azure
        Blob Storage Container.
        """
        self._container_client = container_client
        self._cached_blob_clients = defaultdict()  # type:Dict[str, BlobClient]

    @staticmethod
    def _utc_to_local(utc_dt):
        timestamp = calendar.timegm(utc_dt.timetuple())
        local_dt = datetime.fromtimestamp(timestamp)
        return local_dt.replace(microsecond=utc_dt.microsecond)

    @staticmethod
    def _to_timestamp(date):
        timestamp = None
        try:
            timestamp = date.timestamp()
        except AttributeError:  # python2.7 compatible
            timestamp = time.mktime(BlobCheckpointStore._utc_to_local(date).timetuple())\
                        + date.microsecond / 1e6
        return timestamp

    def _get_blob_client(self, blob_name):
        result = self._cached_blob_clients.get(blob_name)
        if not result:
            result = self._container_client.get_blob_client(blob_name)
            self._cached_blob_clients[blob_name] = result
        return result

    def _upload_ownership(self, ownership, metadata):
        etag = ownership.get("etag")
        if etag:
            etag_match = {"if_match": etag}
        else:
            etag_match = {"if_none_match": '*'}
        blob_name = "{}/{}/{}/ownership/{}".format(ownership["fully_qualified_namespace"], ownership["eventhub_name"],
                                     ownership["consumer_group"], ownership["partition_id"])
        uploaded_blob_properties = self._get_blob_client(blob_name).upload_blob(
            data=UPLOAD_DATA, overwrite=True, metadata=metadata, **etag_match
        )
        ownership["etag"] = uploaded_blob_properties["etag"]
        ownership["last_modified_time"] = self._to_timestamp(uploaded_blob_properties["last_modified"])
        ownership.update(metadata)

    def list_ownership(self, fully_qualified_namespace, eventhub_name, consumer_group):
        try:
            blobs = self._container_client.list_blobs(
                name_starts_with="{}/{}/{}/ownership".format(
                    fully_qualified_namespace, eventhub_name, consumer_group),
                include=['metadata'])
            result = []
            for b in blobs:
                ownership = {
                    "fully_qualified_namespace": fully_qualified_namespace,
                    "eventhub_name": eventhub_name,
                    "consumer_group": consumer_group,
                    "partition_id": b.name.split("/")[-1],
                    "owner_id": b.metadata["ownerId"],
                    "etag": b.etag,
                    "last_modified_time": self._to_timestamp(b.last_modified) if b.last_modified else None
                }
                result.append(ownership)
            return result
        except Exception as err:  # pylint:disable=broad-except
            logger.warning("An exception occurred during list_ownership for "
                           "namespace %r eventhub %r consumer group %r. "
                           "Exception is %r", fully_qualified_namespace, eventhub_name, consumer_group, err)
            raise

    def _claim_one_partition(self, ownership):
        partition_id = ownership["partition_id"]
        fully_qualified_namespace = ownership["fully_qualified_namespace"]
        eventhub_name = ownership["eventhub_name"]
        consumer_group = ownership["consumer_group"]
        owner_id = ownership["owner_id"]
        metadata = {"ownerId": owner_id}
        try:
            self._upload_ownership(ownership, metadata)
            return ownership
        except (ResourceModifiedError, ResourceExistsError):
            logger.info(
                "EventProcessor instance %r of namespace %r eventhub %r consumer group %r "
                "lost ownership to partition %r",
                owner_id, fully_qualified_namespace, eventhub_name, consumer_group, partition_id)
            raise OwnershipLostError()
        except Exception as err:  # pylint:disable=broad-except
            logger.warning("An exception occurred when EventProcessor instance %r claim_ownership for "
                           "namespace %r eventhub %r consumer group %r partition %r. "
                           "The ownership is now lost. Exception "
                           "is %r",
                           owner_id, fully_qualified_namespace, eventhub_name, consumer_group, partition_id, err)
            return ownership  # Keep the ownership if an unexpected error happens

    def claim_ownership(self, ownership_list):
        gathered_results = []
        for x in ownership_list:
            try:
                gathered_results.append(self._claim_one_partition(x))
            except OwnershipLostError:
                pass
        return gathered_results

    def update_checkpoint(self, fully_qualified_namespace, eventhub_name, consumer_group, partition_id,
                                offset, sequence_number):
        metadata = {
            "Offset": offset,
            "SequenceNumber": str(sequence_number),
        }
        blob_name = "{}/{}/{}/checkpoint/{}".format(fully_qualified_namespace, eventhub_name,
                                     consumer_group, partition_id)
        self._get_blob_client(blob_name).upload_blob(
            data=UPLOAD_DATA, overwrite=True, metadata=metadata
        )

    def list_checkpoints(self, fully_qualified_namespace, eventhub_name, consumer_group):
        blobs = self._container_client.list_blobs(
            name_starts_with="{}/{}/{}/checkpoint".format(
                fully_qualified_namespace, eventhub_name, consumer_group),
            include=['metadata'])
        result = []
        for b in blobs:
            metadata = b.metadata
            checkpoint = {
                "fully_qualified_namespace": fully_qualified_namespace,
                "eventhub_name": eventhub_name,
                "consumer_group": consumer_group,
                "partition_id": b.name.split("/")[-1],
                "offset": metadata["Offset"],
                "sequence_number": metadata["SequenceNumber"]
            }
            result.append(checkpoint)
        return result
