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
    from urllib.parse import urlparse # pylint: disable=unused-import
except ImportError:
    from urlparse import urlparse # type: ignore

from azure.core.async_paging import AsyncItemPaged
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from azure.storage.queue._shared.policies_async import ExponentialRetry
from azure.storage.queue.queue_service_client import QueueServiceClient as QueueServiceClientBase
from azure.storage.queue._shared.models import LocationMode
from azure.storage.queue._shared.base_client_async import AsyncStorageAccountHostsMixin
from azure.storage.queue._shared.response_handlers import process_storage_error
from azure.storage.queue._generated.aio import AzureQueueStorage
from azure.storage.queue._generated.models import StorageServiceProperties, StorageErrorException

from azure.storage.queue.aio.models import QueuePropertiesPaged
from .queue_client_async import QueueClient

if TYPE_CHECKING:
    from datetime import datetime
    from azure.core import Configuration
    from azure.core.pipeline.policies import HTTPPolicy
    from azure.storage.queue._shared.models import AccountPermissions, ResourceTypes
    from azure.storage.queue.aio.models import (
        QueueProperties
    )
    from azure.storage.queue.models import Logging, Metrics, CorsRule


class QueueServiceClient(AsyncStorageAccountHostsMixin, QueueServiceClientBase):
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

    Example:
        .. literalinclude:: ../tests/test_queue_samples_authentication.py
            :start-after: [START create_queue_service_client]
            :end-before: [END create_queue_service_client]
            :language: python
            :dedent: 8
            :caption: Creating the QueueServiceClient with an account url and credential.
    """

    def __init__(
            self, account_url,  # type: str
            credential=None,  # type: Optional[Any]
            loop=None, # type: Any
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        kwargs['retry_policy'] = kwargs.get('retry_policy') or ExponentialRetry(**kwargs)
        super(QueueServiceClient, self).__init__( # type: ignore
            account_url,
            credential=credential,
            loop=loop,
            **kwargs)
        self._client = AzureQueueStorage(url=self.url, pipeline=self._pipeline, loop=loop) # type: ignore
        self._loop = loop

    @distributed_trace_async
    async def get_service_stats(self, timeout=None, **kwargs): # type: ignore
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
        :rtype: ~azure.storage.queue._generated.models._models.StorageServiceStats
        """
        try:
            return await self._client.service.get_statistics( # type: ignore
                timeout=timeout, use_location=LocationMode.SECONDARY, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_service_properties(self, timeout=None, **kwargs): # type: ignore
        # type: (Optional[int], Optional[Any]) -> Dict[str, Any]
        """Gets the properties of a storage account's Queue service, including
        Azure Storage Analytics.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: ~azure.storage.queue._generated.models._models.StorageServiceProperties

        Example:
            .. literalinclude:: ../tests/test_queue_samples_service.py
                :start-after: [START get_queue_service_properties]
                :end-before: [END get_queue_service_properties]
                :language: python
                :dedent: 8
                :caption: Getting queue service properties.
        """
        try:
            return await self._client.service.get_properties(timeout=timeout, **kwargs) # type: ignore
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def set_service_properties( # type: ignore
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
        :type logging: ~azure.storage.queue.models.Logging
        :param hour_metrics:
            The hour metrics settings provide a summary of request
            statistics grouped by API in hourly aggregates for queues.
        :type hour_metrics: ~azure.storage.queue.models.Metrics
        :param minute_metrics:
            The minute metrics settings provide request statistics
            for each minute for queues.
        :type minute_metrics: ~azure.storage.queue.models.Metrics
        :param cors:
            You can include up to five CorsRule elements in the
            list. If an empty list is specified, all CORS rules will be deleted,
            and CORS will be disabled for the service.
        :type cors: list(:class:`~azure.storage.queue.models.CorsRule`)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        Example:
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
            return await self._client.service.set_properties(props, timeout=timeout, **kwargs) # type: ignore
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def list_queues(
            self, name_starts_with=None,  # type: Optional[str]
            include_metadata=False,  # type: Optional[bool]
            results_per_page=None,  # type: Optional[int]
            timeout=None,  # type: Optional[int]
            **kwargs
        ) -> AsyncItemPaged:
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
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.core.queue.models.QueueProperties]

        Example:
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
        return AsyncItemPaged(
            command, prefix=name_starts_with, results_per_page=results_per_page,
            page_iterator_class=QueuePropertiesPaged
        )

    @distributed_trace_async
    async def create_queue( # type: ignore
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
        :rtype: ~azure.storage.queue.queue_client.QueueClient

        Example:
            .. literalinclude:: ../tests/test_queue_samples_service.py
                :start-after: [START qsc_create_queue]
                :end-before: [END qsc_create_queue]
                :language: python
                :dedent: 8
                :caption: Create a queue in the service.
        """
        queue = self.get_queue_client(name)
        await queue.create_queue(
            metadata=metadata, timeout=timeout, **kwargs)
        return queue

    @distributed_trace_async
    async def delete_queue( # type: ignore
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
        :type queue: str or ~azure.storage.queue.models.QueueProperties
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        Example:
            .. literalinclude:: ../tests/test_queue_samples_service.py
                :start-after: [START qsc_delete_queue]
                :end-before: [END qsc_delete_queue]
                :language: python
                :dedent: 12
                :caption: Delete a queue in the service.
        """
        queue_client = self.get_queue_client(queue)
        await queue_client.delete_queue(timeout=timeout, **kwargs)

    def get_queue_client(self, queue, **kwargs):
        # type: (Union[QueueProperties, str], Optional[Any]) -> QueueClient
        """Get a client to interact with the specified queue.

        The queue need not already exist.

        :param queue:
            The queue. This can either be the name of the queue,
            or an instance of QueueProperties.
        :type queue: str or ~azure.storage.queue.models.QueueProperties
        :returns: A :class:`~azure.core.queue.queue_client.QueueClient` object.
        :rtype: ~azure.core.queue.queue_client.QueueClient

        Example:
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
            _hosts=self._hosts, loop=self._loop, **kwargs)
