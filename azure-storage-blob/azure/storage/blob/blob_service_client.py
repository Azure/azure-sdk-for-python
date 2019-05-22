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
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from azure.storage.common import SharedAccessSignature

from .container_client import ContainerClient
from .blob_client import BlobClient
from .models import (
    ContainerProperties,
    StorageServiceProperties,
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
            account_name, # type: Optional[str]
            account_key, # type: Optional[str]
            credentials=None,  # type: Optional[HTTPPolicy]
            configuration=None, # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        # TODO: Parse URL
        # TODO: Alternative constructors
        self.url = url
        self.account = None
        self.account_name = account_name
        self.account_key = account_key
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
        """
        Creates the url to access this blob.

        :param str protocol:
            Protocol to use: 'http' or 'https'. If not specified, uses the
            protocol specified in the URL when the client was created..
        :param str sas_token:
            Shared access signature token created with
            generate_shared_access_signature.
        :return: blob access URL.
        :rtype: str
        """
        parsed_url = urlparse(self.url)
        new_scheme = protocol or parsed_url.scheme
        query = []
        if sas_token:
            query.append(sas_token)
        new_url = "{}://{}{}".format(
            new_scheme,
            parsed_url.netloc,
            parsed_url.path)
        if query:
            new_url += "?{}".format('&'.join(query))
        return new_url

    def generate_shared_access_signature(
            self, resource_types,  # type: Union[ResourceTypes, str]
            permission,  # type: Union[AccountPermissions, str]
            expiry,  # type: Optional[Union[datetime, str]]
            start=None,  # type: Optional[Union[datetime, str]]
            ip=None,  # type: Optional[str]
            protocol=None  # type: Optional[str]
        ):
        '''
        Generates a shared access signature for the blob service.
        Use the returned signature with the sas_token parameter of any BlobService.
        :param ResourceTypes resource_types:
            Specifies the resource types that are accessible with the account SAS.
        :param AccountPermissions permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :param expiry:
            The time at which the shared access signature becomes invalid.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has
            been specified in an associated stored access policy. Azure will always
            convert values to UTC. If a date is passed in without timezone info, it
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If
            omitted, start time for this call is assumed to be the time when the
            storage service receives the request. Azure will always convert values
            to UTC. If a date is passed in without timezone info, it is assumed to
            be UTC.
        :type start: datetime or str
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~azure.storage.common.models.Protocol` for possible values.
        :return: A Shared Access Signature (sas) token.
        :rtype: str
        '''
        if self.account_name is None:
            raise ValueError('Account name should not be None')
        if self.account_key is None:
            raise ValueError('Account key should not be None')

        sas = SharedAccessSignature(self.account_name, self.account_key)
        return sas.generate_account(Services.BLOB, resource_types, permission,
                                    expiry, start=start, ip=ip, protocol=protocol)

    def get_account_information(self, timeout=None):
        # type: (Optional[int]) -> Dict[str, str]
        """
        :returns: A dict of account information (SKU and account type).
        """
        response = self._client.service.get_account_info(cls=return_response_headers)
        return {
            'SKU': response.get('x-ms-sku-name'),
            'AccountType': response.get('x-ms-account-kind')
        }

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
        command = functools.partial(
            self._client.service.list_containers_segment,
            include=include,
            timeout=timeout,
            **kwargs)
        return ContainerPropertiesPaged(command, prefix=prefix, results_per_page=results_per_page)

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
