# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Iterable, Dict, Any, Optional
import logging
from collections import defaultdict
import asyncio
from azure.eventhub.exceptions import OwnershipLostError  # type: ignore
from azure.eventhub.aio import CheckpointStore  # type: ignore  # pylint: disable=no-name-in-module
from azure.core.exceptions import ResourceModifiedError, ResourceExistsError  # type: ignore
from ._vendor.storage.blob.aio import ContainerClient, BlobClient
from ._vendor.storage.blob._shared.base_client import parse_connection_str


logger = logging.getLogger(__name__)
UPLOAD_DATA = ""


class BlobCheckpointStore(CheckpointStore):
    """A CheckpointStore that uses Azure Blob Storage to store the partition ownership and checkpoint data.

    This class implements methods list_ownership, claim_ownership, update_checkpoint and list_checkpoints that are
    defined in class azure.eventhub.aio.CheckpointStore of package azure-eventhub.

    :param str blob_account_url:
        The URI to the storage account.
    :param container_name:
        The name of the container for the blobs.
    :type container_name: str
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string, an account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the URL already has a SAS token, specifying an explicit credential will take priority.
    :keyword str api_version:
            The Storage API version to use for requests. Default value is '2019-07-07'.
    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    """

    def __init__(self, blob_account_url, container_name, *, credential=None, **kwargs):
        # type(str, str, Optional[Any], Any) -> None
        self._container_client = kwargs.pop("container_client", None)
        if not self._container_client:
            api_version = kwargs.pop("api_version", None)
            if api_version:
                headers = kwargs.get("headers")
                if headers:
                    headers["x-ms-version"] = api_version
                else:
                    kwargs["headers"] = {"x-ms-version": api_version}
            self._container_client = ContainerClient(
                blob_account_url, container_name, credential=credential, **kwargs
            )
        self._cached_blob_clients = defaultdict()  # type: Dict[str, BlobClient]

    @classmethod
    def from_connection_string(
        cls, conn_str, container_name, *, credential=None, **kwargs
    ):
        # type: (str, str, Any, Optional[Any], Any) -> BlobCheckpointStore
        """Create BlobCheckpointStore from a storage connection string.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param container_name:
            The container name for the blobs.
        :type container_name: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
            Credentials provided here will take precedence over those in the connection string.
        :keyword str api_version:
            The Storage API version to use for requests. Default value is '2019-07-07'.
        :keyword str secondary_hostname:
            The hostname of the secondary endpoint.
        :returns: A blob checkpoint store.
        :rtype: ~azure.eventhub.extensions.checkpointstoreblobaio.BlobCheckpointStore
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'blob')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary

        return cls(account_url, container_name, credential=credential, **kwargs)

    async def __aenter__(self):
        await self._container_client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self._container_client.__aexit__(*args)

    def _get_blob_client(self, blob_name: str) -> BlobClient:
        result = self._cached_blob_clients.get(blob_name)
        if not result:
            result = self._container_client.get_blob_client(blob_name)
            self._cached_blob_clients[blob_name] = result
        return result

    async def _upload_ownership(
        self, ownership: Dict[str, Any], metadata: Dict[str, str]
    ) -> None:
        etag = ownership.get("etag")
        if etag:
            etag_match = {"if_match": etag}
        else:
            etag_match = {"if_none_match": "*"}
        blob_name = "{}/{}/{}/ownership/{}".format(
            ownership["fully_qualified_namespace"],
            ownership["eventhub_name"],
            ownership["consumer_group"],
            ownership["partition_id"],
        )
        blob_name = blob_name.lower()
        uploaded_blob_properties = await self._get_blob_client(blob_name).upload_blob(
            data=UPLOAD_DATA, overwrite=True, metadata=metadata, **etag_match
        )
        ownership["etag"] = uploaded_blob_properties["etag"]
        ownership["last_modified_time"] = uploaded_blob_properties[
            "last_modified"
        ].timestamp()
        ownership.update(metadata)

    async def list_ownership(
        self, fully_qualified_namespace: str, eventhub_name: str, consumer_group: str
    ) -> Iterable[Dict[str, Any]]:
        try:
            blob_prefix = "{}/{}/{}/ownership".format(
                fully_qualified_namespace, eventhub_name, consumer_group
            )
            blobs = self._container_client.list_blobs(
                name_starts_with=blob_prefix.lower(), include=["metadata"]
            )
            result = []
            async for blob in blobs:
                ownership = {
                    "fully_qualified_namespace": fully_qualified_namespace,
                    "eventhub_name": eventhub_name,
                    "consumer_group": consumer_group,
                    "partition_id": blob.name.split("/")[-1],
                    "owner_id": blob.metadata["ownerid"],
                    "etag": blob.etag,
                    "last_modified_time": blob.last_modified.timestamp()
                    if blob.last_modified
                    else None,
                }
                result.append(ownership)
            return result
        except Exception as error:  # pylint:disable=broad-except
            logger.warning(
                "An exception occurred during list_ownership for "
                "namespace %r eventhub %r consumer group %r. "
                "Exception is %r",
                fully_qualified_namespace,
                eventhub_name,
                consumer_group,
                error,
            )
            raise

    async def _claim_one_partition(self, ownership: Dict[str, Any]) -> Dict[str, Any]:
        partition_id = ownership["partition_id"]
        namespace = ownership["fully_qualified_namespace"]
        eventhub_name = ownership["eventhub_name"]
        consumer_group = ownership["consumer_group"]
        owner_id = ownership["owner_id"]
        metadata = {"ownerid": owner_id}
        try:
            await self._upload_ownership(ownership, metadata)
            return ownership
        except (ResourceModifiedError, ResourceExistsError):
            logger.info(
                "EventProcessor instance %r of namespace %r eventhub %r consumer group %r "
                "lost ownership to partition %r",
                owner_id,
                namespace,
                eventhub_name,
                consumer_group,
                partition_id,
            )
            raise OwnershipLostError()
        except Exception as error:  # pylint:disable=broad-except
            logger.warning(
                "An exception occurred when EventProcessor instance %r claim_ownership for "
                "namespace %r eventhub %r consumer group %r partition %r. "
                "The ownership is now lost. Exception "
                "is %r",
                owner_id,
                namespace,
                eventhub_name,
                consumer_group,
                partition_id,
                error,
            )
            return ownership  # Keep the ownership if an unexpected error happens

    async def claim_ownership(
        self, ownership_list: Iterable[Dict[str, Any]]
    ) -> Iterable[Dict[str, Any]]:
        results = await asyncio.gather(
            *[self._claim_one_partition(x) for x in ownership_list],
            return_exceptions=True
        )
        return [
            ownership for ownership in results if not isinstance(ownership, Exception)
        ]

    async def update_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        metadata = {
            "offset": str(checkpoint["offset"]),
            "sequencenumber": str(checkpoint["sequence_number"]),
        }
        blob_name = "{}/{}/{}/checkpoint/{}".format(
            checkpoint["fully_qualified_namespace"],
            checkpoint["eventhub_name"],
            checkpoint["consumer_group"],
            checkpoint["partition_id"],
        )
        blob_name = blob_name.lower()
        await self._get_blob_client(blob_name).upload_blob(
            data=UPLOAD_DATA, overwrite=True, metadata=metadata
        )

    async def list_checkpoints(
        self, fully_qualified_namespace, eventhub_name, consumer_group
    ):
        blob_prefix = "{}/{}/{}/checkpoint".format(
            fully_qualified_namespace, eventhub_name, consumer_group
        )
        blobs = self._container_client.list_blobs(
            name_starts_with=blob_prefix.lower(), include=["metadata"]
        )
        result = []
        async for blob in blobs:
            metadata = blob.metadata
            checkpoint = {
                "fully_qualified_namespace": fully_qualified_namespace,
                "eventhub_name": eventhub_name,
                "consumer_group": consumer_group,
                "partition_id": blob.name.split("/")[-1],
                "offset": str(metadata["offset"]),
                "sequence_number": int(metadata["sequencenumber"]),
            }
            result.append(checkpoint)
        return result

    async def close(self) -> None:
        """Close an open HTTP session and connection."""
        return await self.__aexit__()
