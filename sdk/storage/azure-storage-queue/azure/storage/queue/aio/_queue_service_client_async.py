# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from types import TracebackType
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union
from typing_extensions import Self

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import AsyncPipeline
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from ._models import QueuePropertiesPaged
from ._queue_client_async import QueueClient
from .._encryption import StorageEncryptionMixin
from .._generated.aio import AzureQueueStorage
from .._generated.models import KeyInfo, StorageServiceProperties
from .._models import CorsRule, QueueProperties, service_properties_deserialize, service_stats_deserialize
from .._queue_service_client_helpers import _parse_url
from .._serialize import get_api_version
from .._shared.base_client import StorageAccountHostsMixin
from .._shared.base_client_async import AsyncStorageAccountHostsMixin, AsyncTransportWrapper, parse_connection_str
from .._shared.models import LocationMode
from .._shared.parser import _to_utc_datetime
from .._shared.policies_async import ExponentialRetry
from .._shared.response_handlers import parse_to_internal_user_delegation_key, process_storage_error

if TYPE_CHECKING:
    from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
    from azure.core.credentials_async import AsyncTokenCredential
    from datetime import datetime
    from .._models import Metrics, QueueAnalyticsLogging
    from .._shared.models import UserDelegationKey


class QueueServiceClient(  # type: ignore [misc]
    AsyncStorageAccountHostsMixin, StorageAccountHostsMixin, StorageEncryptionMixin
):
    """A client to interact with the Queue Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete queues within the account.
    For operations relating to a specific queue, a client for this entity
    can be retrieved using the :func:`~get_queue_client` function.

    :param str account_url:
        The URL to the queue service endpoint. Any other entities included
        in the URL path (e.g. queue) will be discarded. This URL can be optionally
        authenticated with a SAS token.
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string,
        an instance of a AzureSasCredential or AzureNamedKeyCredential from azure.core.credentials,
        an account shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
        - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
        If using an instance of AzureNamedKeyCredential, "name" should be the storage account name, and "key"
        should be the storage account key.
    :type credential:
        ~azure.core.credentials.AzureNamedKeyCredential or
        ~azure.core.credentials.AzureSasCredential or
        ~azure.core.credentials_async.AsyncTokenCredential or
        str or dict[str, str] or None
    :keyword str api_version:
        The Storage API version to use for requests. Default value is the most recent service version that is
        compatible with the current SDK. Setting to an older version may result in reduced feature compatibility.
    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    :keyword str audience: The audience to use when requesting tokens for Azure Active Directory
        authentication. Only has an effect when credential is of type TokenCredential. The value could be
        https://storage.azure.com/ (default) or https://<account>.queue.core.windows.net.

    .. admonition:: Example:

        .. literalinclude:: ../samples/queue_samples_authentication_async.py
            :start-after: [START async_create_queue_service_client]
            :end-before: [END async_create_queue_service_client]
            :language: python
            :dedent: 8
            :caption: Creating the QueueServiceClient with an account url and credential.

        .. literalinclude:: ../samples/queue_samples_authentication_async.py
            :start-after: [START async_create_queue_service_client_oauth]
            :end-before: [END async_create_queue_service_client_oauth]
            :language: python
            :dedent: 8
            :caption: Creating the QueueServiceClient with Default Azure Identity credentials.
    """

    def __init__(
        self,
        account_url: str,
        credential: Optional[
            Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "AsyncTokenCredential"]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        audience: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        kwargs["retry_policy"] = kwargs.get("retry_policy") or ExponentialRetry(**kwargs)
        loop = kwargs.pop("loop", None)
        parsed_url, sas_token = _parse_url(account_url=account_url, credential=credential)
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(QueueServiceClient, self).__init__(
            parsed_url,
            service="queue",
            credential=credential,
            secondary_hostname=secondary_hostname,
            audience=audience,
            **kwargs,
        )
        self._client = AzureQueueStorage(self.url, base_url=self.url, pipeline=self._pipeline, loop=loop)
        self._client._config.version = get_api_version(api_version)  # type: ignore [assignment]
        self._loop = loop
        self._configure_encryption(kwargs)

    async def __aenter__(self) -> Self:
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self, typ: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None:
        await self._client.__aexit__(typ, exc, tb)  # pylint: disable=specify-parameter-names-in-call

    async def close(self) -> None:
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.

        :return: None
        :rtype: None
        """
        await self._client.close()

    def _format_url(self, hostname: str) -> str:
        """Format the endpoint URL according to the current location
        mode hostname.

        :param str hostname: The current location mode hostname.
        :returns: The formatted endpoint URL according to the specified location mode hostname.
        :rtype: str
        """
        return f"{self.scheme}://{hostname}/{self._query_str}"

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        credential: Optional[
            Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "AsyncTokenCredential"]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        audience: Optional[str] = None,
        **kwargs: Any,
    ) -> Self:
        """Create QueueServiceClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string,
            an instance of a AzureSasCredential or AzureNamedKeyCredential from azure.core.credentials,
            an account shared access key, or an instance of a TokenCredentials class from azure.identity.
            Credentials provided here will take precedence over those in the connection string.
            If using an instance of AzureNamedKeyCredential, "name" should be the storage account name, and "key"
            should be the storage account key.
        :type credential:
            Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential]]
        :keyword str api_version:
            The Storage API version to use for requests. Default value is the most recent service version that is
            compatible with the current SDK. Setting to an older version may result in reduced feature compatibility.
        :keyword str secondary_hostname:
            The hostname of the secondary endpoint.
        :keyword str audience: The audience to use when requesting tokens for Azure Active Directory
            authentication. Only has an effect when credential is of type TokenCredential. The value could be
            https://storage.azure.com/ (default) or https://<account>.queue.core.windows.net.
        :returns: A Queue service client.
        :rtype: ~azure.storage.queue.QueueClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_authentication.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the QueueServiceClient with a connection string.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, "queue")
        return cls(
            account_url,
            credential=credential,
            api_version=api_version,
            secondary_hostname=secondary_hostname or secondary,
            audience=audience,
            **kwargs,
        )

    @distributed_trace_async
    async def get_user_delegation_key(
        self, *, expiry: "datetime", start: Optional["datetime"] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> "UserDelegationKey":
        """
        Obtain a user delegation key for the purpose of signing SAS tokens.
        A token credential must be present on the service object for this request to succeed.

        :keyword expiry:
            A DateTime value. Indicates when the key stops being valid.
        :paramtype expiry: ~datetime.datetime
        :keyword start:
            A DateTime value. Indicates when the key becomes valid.
        :paramtype start: Optional[~datetime.datetime]
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-blob-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-blob
            #other-client--per-operation-configuration>`__.
        :return: The user delegation key.
        :rtype: ~azure.storage.queue.UserDelegationKey
        """
        key_info = KeyInfo(start=_to_utc_datetime(start), expiry=_to_utc_datetime(expiry))  # type: ignore
        try:
            user_delegation_key = await self._client.service.get_user_delegation_key(
                key_info=key_info, timeout=timeout, **kwargs
            )
        except HttpResponseError as error:
            process_storage_error(error)
        return parse_to_internal_user_delegation_key(user_delegation_key)

    @distributed_trace_async
    async def get_service_stats(self, *, timeout: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]:
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

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: The queue service stats.
        :rtype: Dict[str, Any]
        """
        try:
            stats = await self._client.service.get_statistics(
                timeout=timeout, use_location=LocationMode.SECONDARY, **kwargs
            )
            return service_stats_deserialize(stats)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_service_properties(self, *, timeout: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]:
        """Gets the properties of a storage account's Queue service, including
        Azure Storage Analytics.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :returns: An object containing queue service properties such as
            analytics logging, hour/minute metrics, cors rules, etc.
        :rtype: Dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_service_async.py
                :start-after: [START async_get_queue_service_properties]
                :end-before: [END async_get_queue_service_properties]
                :language: python
                :dedent: 12
                :caption: Getting queue service properties.
        """
        try:
            service_props = await self._client.service.get_properties(timeout=timeout, **kwargs)
            return service_properties_deserialize(service_props)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def set_service_properties(
        self,
        analytics_logging: Optional["QueueAnalyticsLogging"] = None,
        hour_metrics: Optional["Metrics"] = None,
        minute_metrics: Optional["Metrics"] = None,
        cors: Optional[List[CorsRule]] = None,
        *,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Sets the properties of a storage account's Queue service, including
        Azure Storage Analytics.

        If an element (e.g. analytics_logging) is left as None, the
        existing settings on the service for that functionality are preserved.

        :param analytics_logging:
            Groups the Azure Analytics Logging settings.
        :type analytics_logging: ~azure.storage.queue.QueueAnalyticsLogging
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
        :type cors: Optional[List(~azure.storage.queue.CorsRule)]
        :keyword int timeout:
            The timeout parameter is expressed in seconds.

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_service_async.py
                :start-after: [START async_set_queue_service_properties]
                :end-before: [END async_set_queue_service_properties]
                :language: python
                :dedent: 12
                :caption: Setting queue service properties.
        """
        props = StorageServiceProperties(
            logging=analytics_logging,
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=CorsRule._to_generated(cors),  # pylint: disable=protected-access
        )
        try:
            await self._client.service.set_properties(props, timeout=timeout, **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def list_queues(
        self,
        name_starts_with: Optional[str] = None,
        include_metadata: Optional[bool] = False,
        *,
        results_per_page: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncItemPaged:
        """Returns a generator to list the queues under the specified account.

        The generator will lazily follow the continuation tokens returned by
        the service and stop when all queues have been returned.

        :param str name_starts_with:
            Filters the results to return only queues whose names
            begin with the specified prefix.
        :param bool include_metadata:
            Specifies that queue metadata be returned in the response.
        :keyword int results_per_page:
            The maximum number of queue names to retrieve per API
            call. If the request does not specify the server will return up to 5,000 items.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-queue-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue
            #other-client--per-operation-configuration>`__. This function may make multiple
            calls to the service in which case the timeout value specified will be
            applied to each individual call.
        :returns: An iterable (auto-paging) of QueueProperties.
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.storage.queue.QueueProperties]

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_service_async.py
                :start-after: [START async_qsc_list_queues]
                :end-before: [END async_qsc_list_queues]
                :language: python
                :dedent: 16
                :caption: List queues in the service.
        """
        include = ["metadata"] if include_metadata else None
        command = functools.partial(
            self._client.service.list_queues_segment,
            prefix=name_starts_with,
            include=include,
            timeout=timeout,
            **kwargs,
        )
        return AsyncItemPaged(
            command,
            prefix=name_starts_with,
            results_per_page=results_per_page,
            page_iterator_class=QueuePropertiesPaged,
        )

    @distributed_trace_async
    async def create_queue(
        self, name: str, metadata: Optional[Dict[str, str]] = None, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> QueueClient:
        """Creates a new queue under the specified account.

        If a queue with the same name already exists, the operation fails.
        Returns a client with which to interact with the newly created queue.

        :param str name: The name of the queue to create.
        :param metadata:
            A dict with name_value pairs to associate with the
            queue as metadata. Example: {'Category': 'test'}
        :type metadata: Dict[str, str]
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: A QueueClient for the newly created Queue.
        :rtype: ~azure.storage.queue.aio.QueueClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_service_async.py
                :start-after: [START async_qsc_create_queue]
                :end-before: [END async_qsc_create_queue]
                :language: python
                :dedent: 12
                :caption: Create a queue in the service.
        """
        queue = self.get_queue_client(name)
        kwargs.setdefault("merge_span", True)
        await queue.create_queue(metadata=metadata, timeout=timeout, **kwargs)
        return queue

    @distributed_trace_async
    async def delete_queue(
        self, queue: Union["QueueProperties", str], *, timeout: Optional[int] = None, **kwargs: Any
    ) -> None:
        """Deletes the specified queue and any messages it contains.

        When a queue is successfully deleted, it is immediately marked for deletion
        and is no longer accessible to clients. The queue is later removed from
        the Queue service during garbage collection.

        Note that deleting a queue is likely to take at least 40 seconds to complete.
        If an operation is attempted against the queue while it was being deleted,
        an ~azure.core.exceptions.HttpResponseError will be thrown.

        :param queue:
            The queue to delete. This can either be the name of the queue,
            or an instance of QueueProperties.
        :type queue: str or ~azure.storage.queue.QueueProperties
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_service_async.py
                :start-after: [START async_qsc_delete_queue]
                :end-before: [END async_qsc_delete_queue]
                :language: python
                :dedent: 16
                :caption: Delete a queue in the service.
        """
        queue_client = self.get_queue_client(queue)
        kwargs.setdefault("merge_span", True)
        await queue_client.delete_queue(timeout=timeout, **kwargs)

    def get_queue_client(self, queue: Union["QueueProperties", str], **kwargs: Any) -> QueueClient:
        """Get a client to interact with the specified queue.

        The queue need not already exist.

        :param queue:
            The queue. This can either be the name of the queue,
            or an instance of QueueProperties.
        :type queue: str or ~azure.storage.queue.QueueProperties
        :returns: A ~azure.storage.queue.aio.QueueClient object.
        :rtype: ~azure.storage.queue.aio.QueueClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_service_async.py
                :start-after: [START async_get_queue_client]
                :end-before: [END async_get_queue_client]
                :language: python
                :dedent: 8
                :caption: Get the queue client.
        """
        if isinstance(queue, QueueProperties):
            queue_name = queue.name
        else:
            queue_name = queue

        _pipeline = AsyncPipeline(
            transport=AsyncTransportWrapper(self._pipeline._transport),  # pylint: disable=protected-access
            policies=self._pipeline._impl_policies,  # type: ignore # pylint: disable=protected-access
        )

        return QueueClient(
            self.url,
            queue_name=queue_name,
            credential=self.credential,
            key_resolver_function=self.key_resolver_function,
            require_encryption=self.require_encryption,
            encryption_version=self.encryption_version,
            key_encryption_key=self.key_encryption_key,
            api_version=self.api_version,
            _pipeline=_pipeline,
            _configuration=self._config,
            _location_mode=self._location_mode,
            _hosts=self._hosts,
            **kwargs,
        )
