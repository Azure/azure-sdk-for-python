# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List,
    TYPE_CHECKING
)

from .container_client import ContainerClient
from .blob_client import BlobClient
from .models import ContainerProperties
from .common import BlobType
from ._utils import (
    create_client,
    create_pipeline,
    create_configuration,
    get_access_conditions
)


if TYPE_CHECKING:
    from datetime import datetime
    from azure.core import Configuration
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.pipeline.policies import HTTPPolicy
    from .models import (
        AccountPermissions,
        ResourceTypes,
        BlobProperties
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
        self.url = url
        self.account = None
        self._pipeline = create_pipeline(configuration, credentials, **kwargs)
        self._client = create_client(url, self._pipeline)

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

    def get_service_stats(self, timeout=None):
        # type: (Optional[int]) -> Dict[str, Any]
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
        response = self._client.service.get_statistics(timeout=timeout)  # type: Dict[str, Any]
        return response.__dict__

    def get_service_properties(self, timeout=None):
        # type(Optional[int]) -> Dict[str, Any]
        """
        :returns: A dict of service properties.
        """

    def set_service_properties(
            self, logging=None,  # type: Any
            hour_metrics=None,  # type: Any
            minute_metrics=None,  # type: Any
            cors=None,  # type: List[Any]
            target_version=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            delete_retention_policy=None,  # type: Any
            static_website=None  # type: Any
        ):
        # type: (...) -> None
        """
        TODO: Fix type hints
        :returns: None
        """

    def get_container_properties(self, lease=None, timeout=None, **kwargs):
        # type: (Optional[Union[Lease, str]], Optional[int], **Any) -> ContainerProperties
        """
        :returns: ContainerProperties
        """
        access_conditions = get_access_conditions(lease)
        response = self._client.container.get_properties(
            timeout=timeout, lease_access_conditions=access_conditions, **kwargs)
        deserialized = ContainerProperties()
        deserialized.name = response.name
        # Transfer data from response -> deserilized
        return deserialized

    def list_container_properties(
            self, prefix=None,  # type: Optional[str]
            include_metadata=False,  # type: Optional[bool]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> Iterable[ContainerProperties]
        """
        :returns: An iterable (auto-paging) of ContainerProperties.
        """

    def get_container_client(self, container):
        # type: (Union[ContainerProperties, str]) -> ContainerClient
        """
        :returns: A ContainerClient.
        """
        return ContainerClient(self.url, container=container, _pipeline=self._pipeline)

    def get_blob_client(self, container, blob, blob_type=BlobType.BlockBlob):
        # type: (Union[ContainerProperties, str], Union[BlobProperties, str], Union[BlobType, str]) -> BlobClient
        """
        :returns: A BlobClient.
        """
        return BlobClient(
            self.url, container=container, blob=blob,
            blob_type=blob_type, _pipeline=self._pipeline)
