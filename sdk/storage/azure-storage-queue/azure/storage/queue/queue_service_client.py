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

from .queue_client import QueueClient
from ._utils import (
    create_client,
    create_pipeline,
    create_configuration,
    parse_connection_str,
    process_storage_error,
    basic_error_map
)
from .models import StorageServiceProperties, StorageErrorException
from ._shared_access_signature import QueueSharedAccessSignature

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

if TYPE_CHECKING:
    from azure.core import Configuration
    from azure.core.pipeline.policies import HTTPPolicy


class QueueServiceClient(object):

    def __init__(
            self, account_url,  # type: str
            credentials=None,  # type: Optional[HTTPPolicy]
            configuration=None, # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        """
        :param str account_name:
            The storage account name. This is used to authenticate requests 
            signed with an account key and to construct the storage endpoint. It 
            is required unless a connection string is given.
        :param credentials: Optional credentials object to override the SAS key as provided
         in the connection string.
        :param configuration: Optional pipeline configuration settings.
        :type configuration: ~azure.core.configuration.Configuration
        """
        parsed_url = urlparse(account_url.rstrip('/'))
        self.scheme = parsed_url.scheme
        self.account = parsed_url.hostname.split(".queue.core.")[0]
        self.credentials = credentials
        self.url = account_url if not parsed_url.path else "{}://{}".format(
            self.scheme,
            parsed_url.hostname
        )

        self.require_encryption = kwargs.get('require_encryption', False)
        self.key_encryption_key = kwargs.get('key_encryption_key')
        self.key_resolver_function = kwargs.get('key_resolver_function')

        self._config, self._pipeline = create_pipeline(configuration, credentials, **kwargs)
        self._client = create_client(self.url, self._pipeline)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            credentials=None,  # type: Optional[HTTPPolicy]
            configuration=None, # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        """
        Create QueueServiceClient from a Connection String.
        :param str conn_str: A connection string to an Azure Storage account.
        :param credentials: Optional credentials object to override the SAS key as provided
         in the connection string.
        :param configuration: Optional pipeline configuration settings.
        :type configuration: ~azure.core.configuration.Configuration
        """
        account_url, creds = parse_connection_str(conn_str, credentials)
        return cls(account_url, credentials=creds, configuration=configuration, **kwargs)

    def generate_shared_access_signature(
            self, resource_types,  # type: Union[ResourceTypes, str]
            permission,  # type: Union[AccountPermissions, str]
            expiry,  # type: Optional[Union[datetime, str]]
            start=None,  # type: Optional[Union[datetime, str]]
            ip=None,  # type: Optional[str]
            protocol=None  # type: Optional[str]
        ):
        """
        Generates a shared access signature for the queue service.
        Use the returned signature with the sas_token parameter of any QueueService.
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
        """
        if not hasattr(self.credentials, 'account_key') and not self.credentials.account_key:
            raise ValueError("No account SAS key available.")

        sas = SharedAccessSignature(self.account, self.credentials.account_key)
        return sas.generate_account(resource_types, permission,
                                    expiry, start=start, ip=ip, protocol=protocol)

    def get_service_stats(self, timeout=None, **kwargs):
        # type: (Optional[int], Optional[Any]) -> Dict[str, Any]
        """
        Retrieves statistics related to replication for the Queue service. It is
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
        :return: The queue service stats.
        :rtype: ~azure.storage.queue._generated.models.StorageServiceStats
        """
        try:
            return self._client.service.get_statistics(timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def get_service_properties(self, timeout=None, **kwargs):
        # type(Optional[int], Optional[Any]) -> Dict[str, Any]
        """
        Gets the properties of a storage account's Queue service, including
        Azure Storage Analytics.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.queue._generated.models.StorageServiceProperties
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
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """
        Sets the properties of a storage account's Queue service, including
        Azure Storage Analytics. If an element (e.g. Logging) is left as None, the 
        existing settings on the service for that functionality are preserved.
        :param logging:
            Groups the Azure Analytics Logging settings.
        :type logging:
            :class:`~azure.storage.queue.models.Logging`
        :param hour_metrics:
            The hour metrics settings provide a summary of request 
            statistics grouped by API in hourly aggregates for queues.
        :type hour_metrics:
            :class:`~azure.storage.queue.models.Metrics`
        :param minute_metrics:
            The minute metrics settings provide request statistics 
            for each minute for queues.
        :type minute_metrics:
            :class:`~azure.storage.queue.models.Metrics`
        :param cors:
            You can include up to five CorsRule elements in the 
            list. If an empty list is specified, all CORS rules will be deleted, 
            and CORS will be disabled for the service.
        :type cors: list(:class:`~azure.storage.queue.models.CorsRule`)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        props = StorageServiceProperties(
            logging=logging,
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=cors
        )
        try:
            return self._client.service.set_properties(
                props,
                timeout=timeout,
                error_map=basic_error_map(),
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def list_queues(self, prefix=None, include_metadata=False, timeout=None, **kwargs):
        """
        Returns an auto-paging iterable of dict-like QueueProperties.
        :param str prefix:
            Filters the results to return only queues with names that begin
            with the specified prefix.
        :param bool include_metadata:
            Specifies that container metadata be returned in the response.
        :param int timeout:
            The server timeout, expressed in seconds. This function may make multiple 
            calls to the service in which case the timeout value specified will be 
            applied to each individual call.
        """
        try:
            return self._client.service.list_queues_segment(
                prefix=prefix,
                include=include_metadata,
                timeout=timeout,
                error_map=basic_error_map(),
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    def get_queue_client(self, queue_name):
        # type: (str) -> QueueClient
        """
        Get a client to interact with the specified queue.
        The queue need not already exist.
        :param queue_name: The name of the queue with which to interact.
        :type queue: str
        :returns: A QueueClient.
        :rtype: ~azure.core.queue.queue_client.QueueClient
        """
        return QueueClient(
            self.queue_url, queue_name=queue_name, credentials=self.credentials,
            configuration=self._config, _pipeline=self._pipeline,
            require_encryption=self.require_encryption, key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)
