# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from typing import (
    Union,
    Optional,
    Any,
)

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import HttpResponseError, ResourceExistsError
from azure.core.pipeline import AsyncPipeline
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .. import LocationMode
from .._constants import CONNECTION_TIMEOUT
from .._base_client import parse_connection_str
from .._generated.aio._azure_table import AzureTable
from .._generated.models import TableServiceProperties, TableProperties
from .._models import service_stats_deserialize, service_properties_deserialize
from .._error import _process_table_error
from .._table_service_client_base import TableServiceClientBase
from .._models import TableItem
from ._policies_async import ExponentialRetry
from ._table_client_async import TableClient
from ._base_client_async import AsyncStorageAccountHostsMixin
from ._models import TablePropertiesPaged


class TableServiceClient(AsyncStorageAccountHostsMixin, TableServiceClientBase):
    """A client to interact with the Table Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete tables within the account.
    For operations relating to a specific queue, a client for this entity
    can be retrieved using the :func:`~get_table_client` function.

    :param str account_url:
        The URL to the table service endpoint. Any other entities included
        in the URL path (e.g. queue) will be discarded. This URL can be optionally
        authenticated with a SAS token.
    :param str credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string, an account
        shared access key.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is '2019-07-07'.
        Setting to an older version may result in reduced feature compatibility.
    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token, or the connection string already has shared
        access key values. The value can be a SAS token string or an account shared access
        key.
    :type credential: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START auth_from_shared_key]
            :end-before: [END auth_from_shared_key]
            :language: python
            :dedent: 8
            :caption: Creating the tableServiceClient with an account url and credential.

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START auth_by_sas]
            :end-before: [END auth_by_sas]
            :language: python
            :dedent: 8
            :caption: Creating the tableServiceClient with Shared Access Signature.
    """

    def __init__(
        self,
        account_url,  # type: str
        credential=None,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        kwargs["retry_policy"] = kwargs.get("retry_policy") or ExponentialRetry(
            **kwargs
        )
        loop = kwargs.pop("loop", None)
        super(TableServiceClient, self).__init__(  # type: ignore
            account_url, service="table", credential=credential, loop=loop, **kwargs
        )
        kwargs['connection_timeout'] = kwargs.get('connection_timeout') or CONNECTION_TIMEOUT
        self._configure_policies(**kwargs)
        self._client = AzureTable(
            self.url,
            policies=kwargs.pop('policies', self._policies),
            **kwargs
        )
        self._loop = loop

    @classmethod
    def from_connection_string(
        cls,
        conn_str,  # type: any
        **kwargs  # type: Any
    ):  # type: (...) -> TableServiceClient
        """Create TableServiceClient from a Connection String.

        :param conn_str:
            A connection string to an Azure Storage or Cosmos account.
        :type conn_str: str
        :returns: A Table service client.
        :rtype: ~azure.data.tables.TableServiceClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the tableServiceClient from a connection string

        """
        account_url, credential = parse_connection_str(
            conn_str=conn_str, credential=None, service="table", keyword_args=kwargs
        )
        return cls(account_url, credential=credential, **kwargs)

    @distributed_trace_async
    async def get_service_stats(self, **kwargs):
        # type: (...) -> dict[str,object]
        """Retrieves statistics related to replication for the Table service. It is only available on the secondary
        location endpoint when read-access geo-redundant replication is enabled for the account.

        :keyword callable cls: A custom type or function that will be passed the direct response

        :return: Dictionary of service stats
        :rtype: ~azure.data.tables.models.TableServiceStats
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        try:
            timeout = kwargs.pop("timeout", None)
            stats = await self._client.service.get_statistics(  # type: ignore
                timeout=timeout, use_location=LocationMode.SECONDARY, **kwargs
            )
            return service_stats_deserialize(stats)
        except HttpResponseError as error:
            _process_table_error(error)

    @distributed_trace_async
    async def get_service_properties(self, **kwargs):
        # type: (...) -> dict[str,Any]
        """Gets the properties of an account's Table service,
        including properties for Analytics and CORS (Cross-Origin Resource Sharing) rules.

        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: TableServiceProperties, or the result of cls(response)
        :rtype: ~azure.data.tables.models.TableServiceProperties
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        timeout = kwargs.pop("timeout", None)
        try:
            service_props = await self._client.service.get_properties(timeout=timeout, **kwargs)  # type: ignore
            return service_properties_deserialize(service_props)
        except HttpResponseError as error:
            _process_table_error(error)

    @distributed_trace_async
    async def set_service_properties(
        self,
        analytics_logging=None,  # type: Optional[TableAnalyticsLogging]
        hour_metrics=None,  # type: Optional[Metrics]
        minute_metrics=None,  # type: Optional[Metrics]
        cors=None,  # type: Optional[CorsRule]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Sets properties for an account's Table service endpoint,
         including properties for Analytics and CORS (Cross-Origin Resource Sharing) rules.

        :param analytics_logging: Properties for analytics
        :type analytics_logging: ~azure.data.tables.TableAnalyticsLogging
        :param hour_metrics: Hour level metrics
        :type hour_metrics: ~azure.data.tables.Metrics
        :param minute_metrics: Minute level metrics
        :type minute_metrics: ~azure.data.tables.Metrics
        :param cors: Cross-origin resource sharing rules
        :type cors: ~azure.data.tables.CorsRule
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        props = TableServiceProperties(
            logging=analytics_logging,
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=cors,
        )
        try:
            return await self._client.service.set_properties(props, **kwargs)  # type: ignore
        except HttpResponseError as error:
            _process_table_error(error)

    @distributed_trace_async
    async def create_table(
        self,
        table_name,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> TableClient
        """Creates a new table under the given account.

        :param headers:
        :param table_name: The Table name.
        :type table_name: ~azure.data.tables._models.Table
        :return: TableClient, or the result of cls(response)
        :rtype: ~azure.data.tables.TableClient or None
        :raises ~azure.core.exceptions.ResourceExistsError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_delete_table_async.py
                :start-after: [START create_table]
                :end-before: [END create_table]
                :language: python
                :dedent: 8
                :caption: Creating a table from TableServiceClient.
        """
        table = self.get_table_client(table_name=table_name)
        await table.create_table(**kwargs)
        return table

    @distributed_trace_async
    async def create_table_if_not_exists(
        self,
        table_name,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> TableClient
        """Creates a new table if it does not currently exist.
        If the table currently exists, the current table is
        returned.

        :param table_name: The Table name.
        :type table_name: str
        :return: TableClient
        :rtype: ~azure.data.tables.aio.TableClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_delete_table_async.py
                :start-after: [START create_if_not_exists]
                :end-before: [END create_if_not_exists]
                :language: python
                :dedent: 8
                :caption: Creating a table if it does not already exist
        """
        table = self.get_table_client(table_name=table_name)
        try:
            await table.create_table(**kwargs)
        except ResourceExistsError:
            pass
        return table

    @distributed_trace_async
    async def delete_table(
        self,
        table_name,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Deletes the table under the current account

        :param table_name: The Table name.
        :type table_name: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.ResourceNotFoundError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_delete_table_async.py
                :start-after: [START delete_table]
                :end-before: [END delete_table]
                :language: python
                :dedent: 8
                :caption: Deleting a table
        """
        table = self.get_table_client(table_name=table_name)
        await table.delete_table(**kwargs)

    @distributed_trace
    def list_tables(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[TableItem]
        """Queries tables under the given account.

        :keyword int results_per_page: Number of tables per page in return ItemPaged
        :keyword select: Specify desired properties of a table to return certain tables
        :paramtype select: str or list[str]
        :return: AsyncItemPaged
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.data.tables.TableItem]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_query_tables_async.py
                :start-after: [START tsc_list_tables]
                :end-before: [END tsc_list_tables]
                :language: python
                :dedent: 8
                :caption: Listing all tables in an account
        """
        user_select = kwargs.pop("select", None)
        if user_select and not isinstance(user_select, str):
            user_select = ", ".join(user_select)
        top = kwargs.pop("results_per_page", None)

        command = functools.partial(self._client.table.query, **kwargs)
        return AsyncItemPaged(
            command,
            results_per_page=top,
            select=user_select,
            page_iterator_class=TablePropertiesPaged,
        )

    @distributed_trace
    def query_tables(
        self,
        filter,  # type: str    pylint: disable=redefined-builtin
        **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[TableItem]
        """Queries tables under the given account.

        :param filter: Specify a filter to return certain tables.
        :type filter: str
        :keyword int results_per_page: Number of tables per page in return ItemPaged
        :keyword select: Specify desired properties of a table to return certain tables
        :paramtype select: str or list[str]
        :keyword dict[str,str] parameters: Dictionary for formatting query with additional, user defined parameters
        :return: An ItemPaged of tables
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.data.tables.TableItem]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_query_tables_async.py
                :start-after: [START tsc_query_tables]
                :end-before: [END tsc_query_tables]
                :language: python
                :dedent: 8
                :caption: Querying tables in an account given specific parameters
        """
        parameters = kwargs.pop("parameters", None)
        filter = self._parameter_filter_substitution(
            parameters, filter
        )  # pylint: disable=redefined-builtin
        user_select = kwargs.pop("select", None)
        if user_select and not isinstance(user_select, str):
            user_select = ", ".join(user_select)
        top = kwargs.pop("results_per_page", None)

        command = functools.partial(self._client.table.query, **kwargs)
        return AsyncItemPaged(
            command,
            results_per_page=top,
            select=user_select,
            filter=filter,
            page_iterator_class=TablePropertiesPaged,
        )

    def get_table_client(
        self,
        table_name,  # type: str
        **kwargs  # type: Optional[Any]
    ):
        # type: (...) -> TableClient
        """Get a client to interact with the specified table.

        The table need not already exist.

        :param table:
            The queue. This can either be the name of the queue,
            or an instance of QueueProperties.
        :type table: str or ~azure.storage.table.TableProperties
        :returns: A :class:`~azure.data.tables.TableClient` object.
        :rtype: ~azure.data.tables.TableClient

        """
        _pipeline = AsyncPipeline(
            transport=self._client._client._pipeline._transport,  # pylint: disable=protected-access
            policies=self._policies,  # pylint: disable = protected-access
        )

        return TableClient(
            self.url,
            table_name=table_name,
            credential=self.credential,
            key_resolver_function=self.key_resolver_function,
            require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            api_version=self.api_version,
            transport=self._client._client._pipeline._transport,  # pylint: disable=protected-access
            policies=self._policies,
            _configuration=self._client._config,  # pylint: disable=protected-access
            _location_mode=self._location_mode,
            _hosts=self._hosts,
            **kwargs
        )
