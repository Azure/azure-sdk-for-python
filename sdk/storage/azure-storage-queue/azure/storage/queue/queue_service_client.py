# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List,
    TYPE_CHECKING)
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # type: ignore

from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from ._shared.shared_access_signature import SharedAccessSignature
from ._shared.models import LocationMode, Services
from ._shared.base_client import StorageAccountHostsMixin, parse_connection_str, parse_query
from ._shared.response_handlers import process_storage_error
from ._generated import AzureQueueStorage
from ._generated.models import StorageServiceProperties, StorageErrorException

from .models import QueuePropertiesPaged
from .queue_client import QueueClient

if TYPE_CHECKING:
    from datetime import datetime
    from azure.core import Configuration
    from azure.core.pipeline.policies import HTTPPolicy
    from ._shared.models import AccountSasPermissions, ResourceTypes
    from .models import (
        QueueProperties,
        Logging,
        Metrics,
        CorsRule
    )


class QueueServiceClient(StorageAccountHostsMixin):
    """A client to interact with the Queue Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete queues within the account.
    For operations relating to a specific queue, a client for this entity
    can be retrieved using the :func:`~get_queue_client` function.

    :ivar str url:
        The full queue service endpoint URL, including SAS token if used. This could be
        either the primary endpoint, or the secondard endpint depending on the current `location_mode`.
    :ivar str primary_endpoint:
        The full primary endpoint URL.
    :ivar str primary_hostname:
        The hostname of the primary endpoint.
    :ivar str secondary_endpoint:
        The full secondard endpoint URL if configured. If not available
        a ValueError will be raised. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.
    :ivar str secondary_hostname:
        The hostname of the secondary endpoint. If not available this
        will be None. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.
    :ivar str location_mode:
        The location mode that the client is currently using. By default
        this will be "primary". Options include "primary" and "secondary".
    :param str account_url:
        The URL to the queue service endpoint. Any other entities included
        in the URL path (e.g. queue) will be discarded. This URL can be optionally
        authenticated with a SAS token.
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string, and account
        shared access key, or an instance of a TokenCredentials class from azure.identity.

    .. admonition:: Example:

        .. literalinclude:: ../tests/test_queue_samples_authentication.py
            :start-after: [START create_queue_service_client]
            :end-before: [END create_queue_service_client]
            :language: python
            :dedent: 8
            :caption: Creating the QueueServiceClient with an account url and credential.

        .. literalinclude:: ../tests/test_queue_samples_authentication.py
            :start-after: [START create_queue_service_client_token]
            :end-before: [END create_queue_service_client_token]
            :language: python
            :dedent: 8
            :caption: Creating the QueueServiceClient with Azure Identity credentials.
    """

    def __init__(
            self, account_url,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        _, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError("You need to provide either a SAS token or an account key to authenticate.")
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(QueueServiceClient, self).__init__(parsed_url, service='queue', credential=credential, **kwargs)
        self._client = AzureQueueStorage(self.url, pipeline=self._pipeline)

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}/{}".format(self.scheme, hostname, self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):  # type: (...) -> QueueServiceClient
        """Create QueueServiceClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string, and account shared access
            key, or an instance of a TokenCredentials class from azure.identity.

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_queue_samples_authentication.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the QueueServiceClient with a connection string.
        """
        account_url, secondary, credential = parse_connection_str(
            conn_str, credential, 'queue')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(account_url, credential=credential, **kwargs)

    def generate_shared_access_signature(
            self, resource_types,  # type: Union[ResourceTypes, str]
            permission,  # type: Union[AccountSasPermissions, str]
            expiry,  # type: Optional[Union[datetime, str]]
            start=None,  # type: Optional[Union[datetime, str]]
            ip=None,  # type: Optional[str]
            protocol=None  # type: Optional[str]
        ):  # type: (...) -> str
        """Generates a shared access signature for the queue service.

        Use the returned signature with the credential parameter of any Queue Service.

        :param ~azure.storage.queue.ResourceTypes resource_types:
            Specifies the resource types that are accessible with the account SAS.
        :param ~azure.storage.queue.AccountSasPermissions permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
        :param expiry:
            The time at which the shared access signature becomes invalid.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has
            been specified in an associated stored access policy. Azure will always
            convert values to UTC. If a date is passed in without timezone info, it
            is assumed to be UTC.
        :type expiry: ~datetime.datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If
            omitted, start time for this call is assumed to be the time when the
            storage service receives the request. Azure will always convert values
            to UTC. If a date is passed in without timezone info, it is assumed to
            be UTC.
        :type start: ~datetime.datetime or str
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http.
        :return: A Shared Access Signature (sas) token.
        :rtype: str
        """
        if not hasattr(self.credential, 'account_key') and not self.credential.account_key:
            raise ValueError("No account SAS key available.")

        sas = SharedAccessSignature(self.credential.account_name, self.credential.account_key)
        return sas.generate_account(
            services=Services.QUEUE,
            resource_types=resource_types,
            permission=permission,
            expiry=expiry,
            start=start,
            ip=ip,
            protocol=protocol
        ) # type: ignore

    @distributed_trace
    def get_service_stats(self, timeout=None, **kwargs): # type: ignore
        # type: (Optional[int], Optional[Any]) -> Dict[str, Any]
        """Retrieves statistics related to replication for the Queue service.

        It is only available when read-access geo-redundant replication is enabled for
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
        :rtype: ~azure.storage.queue.StorageServiceStats
        """
        try:
            return self._client.service.get_statistics( # type: ignore
                timeout=timeout, use_location=LocationMode.SECONDARY, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def get_service_properties(self, timeout=None, **kwargs): # type: ignore
        # type: (Optional[int], Optional[Any]) -> Dict[str, Any]
        """Gets the properties of a storage account's Queue service, including
        Azure Storage Analytics.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.queue.StorageServiceProperties

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_queue_samples_service.py
                :start-after: [START get_queue_service_properties]
                :end-before: [END get_queue_service_properties]
                :language: python
                :dedent: 8
                :caption: Getting queue service properties.
        """
        try:
            return self._client.service.get_properties(timeout=timeout, **kwargs) # type: ignore
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def set_service_properties( # type: ignore
            self, logging=None,  # type: Optional[Logging]
            hour_metrics=None,  # type: Optional[Metrics]
            minute_metrics=None,  # type: Optional[Metrics]
            cors=None,  # type: Optional[List[CorsRule]]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """Sets the properties of a storage account's Queue service, including
        Azure Storage Analytics.

        If an element (e.g. Logging) is left as None, the
        existing settings on the service for that functionality are preserved.

        :param logging:
            Groups the Azure Analytics Logging settings.
        :type logging: ~azure.storage.queue.Logging
        :param hour_metrics:
            The hour metrics settings provide a summary of request
            statistics grouped by API in hourly aggregates for queues.
        :type hour_metrics: ~azure.storage.queue.Metrics
        :param minute_metrics:
            The minute metrics settings provide request statistics
            for each minute for queues.
        :type minute_metrics: ~azure.storage.queue.Metrics
        :param cors:
            You can include up to five CorsRule elements in the
            list. If an empty list is specified, all CORS rules will be deleted,
            and CORS will be disabled for the service.
        :type cors: list(~azure.storage.queue.CorsRule)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_queue_samples_service.py
                :start-after: [START set_queue_service_properties]
                :end-before: [END set_queue_service_properties]
                :language: python
                :dedent: 8
                :caption: Setting queue service properties.
        """
        props = StorageServiceProperties(
            logging=logging,
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=cors
        )
        try:
            return self._client.service.set_properties(props, timeout=timeout, **kwargs) # type: ignore
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def list_queues(
            self, name_starts_with=None,  # type: Optional[str]
            include_metadata=False,  # type: Optional[bool]
            results_per_page=None,  # type: Optional[int]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> ItemPaged[QueueProperties]
        """Returns a generator to list the queues under the specified account.

        The generator will lazily follow the continuation tokens returned by
        the service and stop when all queues have been returned.

        :param str name_starts_with:
            Filters the results to return only queues whose names
            begin with the specified prefix.
        :param bool include_metadata:
            Specifies that queue metadata be returned in the response.
        :param int results_per_page:
            The maximum number of queue names to retrieve per API
            call. If the request does not specify the server will return up to 5,000 items.
        :param int timeout:
            The server timeout, expressed in seconds. This function may make multiple
            calls to the service in which case the timeout value specified will be
            applied to each individual call.
        :returns: An iterable (auto-paging) of QueueProperties.
        :rtype: ~azure.core.paging.ItemPaged[~azure.core.queue.models.QueueProperties]

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_queue_samples_service.py
                :start-after: [START qsc_list_queues]
                :end-before: [END qsc_list_queues]
                :language: python
                :dedent: 12
                :caption: List queues in the service.
        """
        include = ['metadata'] if include_metadata else None
        command = functools.partial(
            self._client.service.list_queues_segment,
            prefix=name_starts_with,
            include=include,
            timeout=timeout,
            **kwargs)
        return ItemPaged(
            command, prefix=name_starts_with, results_per_page=results_per_page,
            page_iterator_class=QueuePropertiesPaged
        )

    @distributed_trace
    def create_queue(
            self, name,  # type: str
            metadata=None,  # type: Optional[Dict[str, str]]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> QueueClient
        """Creates a new queue under the specified account.

        If a queue with the same name already exists, the operation fails.
        Returns a client with which to interact with the newly created queue.

        :param str name: The name of the queue to create.
        :param metadata:
            A dict with name_value pairs to associate with the
            queue as metadata. Example: {'Category': 'test'}
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.queue.QueueClient

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_queue_samples_service.py
                :start-after: [START qsc_create_queue]
                :end-before: [END qsc_create_queue]
                :language: python
                :dedent: 8
                :caption: Create a queue in the service.
        """
        queue = self.get_queue_client(name)
        kwargs.setdefault('merge_span', True)
        queue.create_queue(
            metadata=metadata, timeout=timeout, **kwargs)
        return queue

    @distributed_trace
    def delete_queue(
            self, queue,  # type: Union[QueueProperties, str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """Deletes the specified queue and any messages it contains.

        When a queue is successfully deleted, it is immediately marked for deletion
        and is no longer accessible to clients. The queue is later removed from
        the Queue service during garbage collection.

        Note that deleting a queue is likely to take at least 40 seconds to complete.
        If an operation is attempted against the queue while it was being deleted,
        an :class:`HttpResponseError` will be thrown.

        :param queue:
            The queue to delete. This can either be the name of the queue,
            or an instance of QueueProperties.
        :type queue: str or ~azure.storage.queue.QueueProperties
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_queue_samples_service.py
                :start-after: [START qsc_delete_queue]
                :end-before: [END qsc_delete_queue]
                :language: python
                :dedent: 12
                :caption: Delete a queue in the service.
        """
        queue_client = self.get_queue_client(queue)
        kwargs.setdefault('merge_span', True)
        queue_client.delete_queue(timeout=timeout, **kwargs)

    def get_queue_client(self, queue, **kwargs):
        # type: (Union[QueueProperties, str], Optional[Any]) -> QueueClient
        """Get a client to interact with the specified queue.

        The queue need not already exist.

        :param queue:
            The queue. This can either be the name of the queue,
            or an instance of QueueProperties.
        :type queue: str or ~azure.storage.queue.QueueProperties
        :returns: A :class:`~azure.core.queue.queue_client.QueueClient` object.
        :rtype: ~azure.core.queue.queue_client.QueueClient

        .. admonition:: Example:

            .. literalinclude:: ../tests/test_queue_samples_service.py
                :start-after: [START get_queue_client]
                :end-before: [END get_queue_client]
                :language: python
                :dedent: 8
                :caption: Get the queue client.
        """
        return QueueClient(
            self.url, queue=queue, credential=self.credential, key_resolver_function=self.key_resolver_function,
            require_encryption=self.require_encryption, key_encryption_key=self.key_encryption_key,
            _pipeline=self._pipeline, _configuration=self._config, _location_mode=self._location_mode,
            _hosts=self._hosts, **kwargs)
