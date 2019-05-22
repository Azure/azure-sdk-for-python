# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List,
    TYPE_CHECKING
)

from .container_client import ContainerClient
from .blob_client import BlobClient
from .models import (
    ContainerProperties,
    StorageServiceProperties,
    ContainerPropertiesPaged
)
from ._generated.models import StorageErrorException
from .common import BlobType
from ._utils import (
    create_client,
    create_pipeline,
    create_configuration,
    get_access_conditions,
    process_storage_error,
    basic_error_map
)

if TYPE_CHECKING:
    from datetime import datetime
    from azure.core import Configuration
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.pipeline.policies import HTTPPolicy
    from .models import (
        AccountPermissions,
        ResourceTypes,
        BlobProperties,
        SnapshotProperties,
        Logging,
        Metrics,
        RetentionPolicy,
        StaticWebsite,
        CorsRule
    )


class BlobServiceClient(object):

    def __init__(
            self, url,  # type: str
            credentials=None,  # type: Optional[HTTPPolicy]
            configuration=None, # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        # TODO: Parse URL
        # TODO: Alternative constructors
        self.url = url
        self.account = None
        self._config, self._pipeline = create_pipeline(configuration, credentials, **kwargs)
        self._client = create_client(url, self._pipeline)

    @classmethod
    def from_connection_string(cls, conn_str, credentials=None, configuration=None, **kwargs):
        """
        Create BlobServiceClient from a Connection String.
        """

    @staticmethod
    def create_configuration(**kwargs):
        # type: (**Any) -> Configuration
        """
        Get an HTTP Pipeline Configuration with all default policies for the Blob
        Storage service.
        """
        return create_configuration(**kwargs)

    def make_url(self, protocol=None, sas_token=None):
        # type: (Optional[str], Optional[str]) -> str
        pass

    def generate_shared_access_signature(
            self, resource_types,  # type: Union[ResourceTypes, str]
            permission,  # type: Union[AccountPermissions, str]
            expiry,  # type: Optional[Union[datetime, str]]
            start=None,  # type: Optional[Union[datetime, str]]
            ip=None,  # type: Optional[str]
            protocol=None  # type: Optional[str]
        ):
        pass

    def get_account_information(self, timeout=None):
        # type: (Optional[int]) -> Dict[str, str]
        """
        :returns: A dict of account information (SKU and account type).
        """

    def get_service_stats(self, timeout=None, **kwargs):
        # type: (Optional[int], **Any) -> Dict[str, Any]
        """
        Retrieves statistics related to replication for the Blob service. It is
        only available when read-access geo-redundant replication is enabled for
        the storage account.

        With geo-redundant replication, Azure Storage maintains your data durable
        in two locations. In both locations, Azure Storage constantly maintains
        multiple healthy replicas of your data. The location where you read,
        create, update, or delete data is the primary storage account location.
        The primary location exists in the region you choose at the time you
        create an account via the Azure Management Azure classic portal, for
        example, North Central US. The location to which your data is replicated
        is the secondary location. The secondary location is automatically
        determined based on the location of the primary; it is in a second data
        center that resides in the same region as the primary location. Read-only
        access is available from the secondary location, if read-access geo-redundant
        replication is enabled for your storage account.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: The blob service stats.
        :rtype: Dict[str, Any]
        """
        return self._client.service.get_statistics(timeout=timeout, secondary_storage=True, **kwargs)

    def get_service_properties(self, timeout=None, **kwargs):
        # type(Optional[int]) -> Dict[str, Any]
        """
        :returns: A dict of service properties.
        """
        try:
            return self._client.service.get_properties(
                timeout=timeout,
                error_map=basic_error_map(),
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def set_service_properties(
            self, logging=None,  # type: Optional[Union[Logging, Dict[str, Any]]]
            hour_metrics=None,  # type: Optional[Union[Metrics, Dict[str, Any]]]
            minute_metrics=None,  # type: Optional[Union[Metrics, Dict[str, Any]]]
            cors=None,  # type: Optional[List[Union[CorsRule, Dict[str, Any]]]]
            target_version=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            delete_retention_policy=None,  # type: Optional[Union[RetentionPolicy, Dict[str, Any]]]
            static_website=None,  # type: Optional[Union[StaticWebsite, Dict[str, Any]]]
            **kwargs
        ):
        # type: (...) -> None
        """
        :returns: None
        """
        props = StorageServiceProperties(
            logging=logging,
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=cors,
            default_service_version=target_version,
            delete_retention_policy=delete_retention_policy,
            static_website=static_website
        )
        try:
            return self._client.service.set_properties(
                props,
                timeout=timeout,
                error_map=basic_error_map(),
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def list_container_properties(
            self, prefix=None,  # type: Optional[str]
            include_metadata=False,  # type: Optional[bool]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> ContainerPropertiesPaged
        """
        :returns: An iterable (auto-paging) of ContainerProperties.
        """
        include = 'metadata' if include_metadata else None
        results_per_page = kwargs.pop('results_per_page', None)
        marker = kwargs.pop('marker', "")
        command = functools.partial(
            self._client.service.list_containers_segment,
            include=include,
            timeout=timeout,
            **kwargs)
        return ContainerPropertiesPaged(
            command, prefix=prefix, results_per_page=results_per_page, marker=marker)

    def get_container_client(self, container):
        # type: (Union[ContainerProperties, str]) -> ContainerClient
        """
        Get a client to interact with the specified container.

        :returns: A ContainerClient.
        """
        return ContainerClient(self.url, container=container, configuration=self._config, _pipeline=self._pipeline)

    def get_blob_client(
            self, container,  # type: Union[ContainerProperties, str]
            blob,  # type: Union[BlobProperties, str]
            blob_type=BlobType.BlockBlob,  # type: Union[BlobType, str]
            snapshot=None  # type: Optional[Union[SnapshotProperties, str]]
        ):
        # type: (...) -> BlobClient
        """
        Get a client to interact with the specified blob.

        :returns: A BlobClient.
        """
        return BlobClient(
            self.url, container=container, blob=blob, blob_type=blob_type,
            snapshot=snapshot, configuration=self._config, _pipeline=self._pipeline)
