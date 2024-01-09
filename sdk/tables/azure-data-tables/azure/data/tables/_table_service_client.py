# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import Optional, Any, Dict, List
from azure.core.exceptions import HttpResponseError, ResourceExistsError
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline import Pipeline

from ._generated.models import TableServiceProperties
from ._models import (
    TableItem,
    LocationMode,
    TableCorsRule,
    TableMetrics,
    TableAnalyticsLogging,
    TablePropertiesPaged,
    service_stats_deserialize,
    service_properties_deserialize,
)
from ._base_client import parse_connection_str, TablesBaseClient, TransportWrapper
from ._error import _process_table_error, _reprocess_error
from ._table_client import TableClient
from ._serialize import _parameter_filter_substitution


class TableServiceClient(TablesBaseClient):
    """A client to interact with the Table Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete tables within the account.
    For operations relating to a specific table, a client for this entity
    can be retrieved using the :func:`~get_table_client` function.

    :ivar str account_name: The name of the Tables account.
    :ivar str url: The full URL to the Tables account.
    :param str endpoint:
        The URL to the table service endpoint. Any other entities included
        in the URL path (e.g. table) will be discarded. This URL can be optionally
        authenticated with a SAS token.
    :keyword credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be one of AzureNamedKeyCredential (azure-core),
        AzureSasCredential (azure-core), or a TokenCredential implementation from azure-identity.
    :paramtype credential:
        ~azure.core.credentials.AzureNamedKeyCredential or
        ~azure.core.credentials.AzureSasCredential or
        ~azure.core.credentials.TokenCredential or None
    :keyword str api_version:
        The Storage API version to use for requests. Default value is '2019-02-02'.
        Setting to an older version may result in reduced feature compatibility.

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START auth_from_sas]
            :end-before: [END auth_from_sas]
            :language: python
            :dedent: 8
            :caption: Authenticating a TableServiceClient from a Shared Access Key

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START auth_from_shared_key]
            :end-before: [END auth_from_shared_key]
            :language: python
            :dedent: 8
            :caption: Authenticating a TableServiceClient from a Shared Account Key
    """

    @classmethod
    def from_connection_string(cls, conn_str: str, **kwargs: Any) -> "TableServiceClient":
        """Create TableServiceClient from a connection string.

        :param str conn_str: A connection string to an Azure Storage or Cosmos account.
        :returns: A Table service client.
        :rtype: ~azure.data.tables.TableServiceClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_authentication.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Authenticating a TableServiceClient from a connection_string
        """
        endpoint, credential = parse_connection_str(conn_str=conn_str, credential=None, keyword_args=kwargs)
        return cls(endpoint, credential=credential, **kwargs)

    @distributed_trace
    def get_service_stats(self, **kwargs) -> Dict[str, object]:
        """Retrieves statistics related to replication for the Table service. It is only available on the secondary
        location endpoint when read-access geo-redundant replication is enabled for the account.

        :return: Dictionary of service stats
        :rtype: dict[str, object]
        :raises: :class:`~azure.core.exceptions.HttpResponseError:`
        """
        try:
            timeout = kwargs.pop("timeout", None)
            stats = self._client.service.get_statistics(timeout=timeout, use_location=LocationMode.SECONDARY, **kwargs)
        except HttpResponseError as error:
            _process_table_error(error)
        return service_stats_deserialize(stats)

    @distributed_trace
    def get_service_properties(self, **kwargs) -> Dict[str, object]:
        """Gets the properties of an account's Table service,
        including properties for Analytics and CORS (Cross-Origin Resource Sharing) rules.

        :return: Dictionary of service properties
        :rtype: dict[str, object]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        timeout = kwargs.pop("timeout", None)
        try:
            service_props = self._client.service.get_properties(timeout=timeout, **kwargs)
        except HttpResponseError as error:
            try:
                _process_table_error(error)
            except HttpResponseError as decoded_error:
                _reprocess_error(decoded_error)
                raise
        return service_properties_deserialize(service_props)

    @distributed_trace
    def set_service_properties(
        self,
        *,
        analytics_logging: Optional[TableAnalyticsLogging] = None,
        hour_metrics: Optional[TableMetrics] = None,
        minute_metrics: Optional[TableMetrics] = None,
        cors: Optional[List[TableCorsRule]] = None,
        **kwargs,
    ) -> None:
        """Sets properties for an account's Table service endpoint,
         including properties for Analytics and CORS (Cross-Origin Resource Sharing) rules.

        :keyword analytics_logging: Properties for analytics
        :paramtype analytics_logging: ~azure.data.tables.TableAnalyticsLogging
        :keyword hour_metrics: Hour level metrics
        :paramtype hour_metrics: ~azure.data.tables.TableMetrics
        :keyword minute_metrics: Minute level metrics
        :paramtype minute_metrics: ~azure.data.tables.TableMetrics
        :keyword cors: Cross-origin resource sharing rules
        :paramtype cors: list[~azure.data.tables.TableCorsRule]
        :return: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        props = TableServiceProperties(
            logging=analytics_logging,
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=[c._to_generated() for c in cors] if cors is not None else cors,  # pylint:disable=protected-access
        )
        try:
            self._client.service.set_properties(props, **kwargs)
        except HttpResponseError as error:
            try:
                _process_table_error(error)
            except HttpResponseError as decoded_error:
                _reprocess_error(decoded_error)
                raise

    @distributed_trace
    def create_table(self, table_name: str, **kwargs) -> TableClient:
        """Creates a new table under the current account.

        :param table_name: The Table name.
        :type table_name: str
        :return: TableClient
        :rtype: ~azure.data.tables.TableClient
        :raises: :class:`~azure.core.exceptions.ResourceExistsError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_delete_table.py
                :start-after: [START create_table_from_tsc]
                :end-before: [END create_table_from_tsc]
                :language: python
                :dedent: 8
                :caption: Creating a table from the TableServiceClient object
        """
        table = self.get_table_client(table_name=table_name)
        table.create_table(**kwargs)
        return table

    @distributed_trace
    def create_table_if_not_exists(self, table_name: str, **kwargs) -> TableClient:
        """Creates a new table if it does not currently exist.
        If the table currently exists, the current table is
        returned.

        :param table_name: The Table name.
        :type table_name: str
        :return: TableClient
        :rtype: ~azure.data.tables.TableClient
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_delete_table.py
                :start-after: [START create_table_if_not_exists]
                :end-before: [END create_table_if_not_exists]
                :language: python
                :dedent: 8
                :caption: Creating a table if it doesn't exist, from the TableServiceClient object
        """
        table = self.get_table_client(table_name=table_name)
        try:
            table.create_table(**kwargs)
        except ResourceExistsError:
            pass
        return table

    @distributed_trace
    def delete_table(self, table_name: str, **kwargs) -> None:
        """Deletes the table under the current account. No error will be raised
        if the given table is not found.

        :param table_name: The Table name.
        :type table_name: str
        :return: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_delete_table.py
                :start-after: [START delete_table_from_tc]
                :end-before: [END delete_table_from_tc]
                :language: python
                :dedent: 8
                :caption: Deleting a table from the TableServiceClient object
        """
        table = self.get_table_client(table_name=table_name)
        table.delete_table(**kwargs)

    @distributed_trace
    def query_tables(
        self,
        query_filter: str,
        *,
        results_per_page: Optional[int] = None,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> ItemPaged[TableItem]:
        """Queries tables under the given account.

        :param str query_filter: Specify a filter to return certain tables.
        :keyword int results_per_page: Number of tables per page in return ItemPaged
        :keyword parameters: Dictionary for formatting query with additional, user defined parameters
        :paramtype parameters:  dict[str, Any]
        :return: An iterator of :class:`~azure.data.tables.TableItem`
        :rtype: ~azure.core.paging.ItemPaged[~azure.data.tables.TableItem]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_query_tables.py
                :start-after: [START tsc_query_tables]
                :end-before: [END tsc_query_tables]
                :language: python
                :dedent: 16
                :caption: Querying tables in a storage account
        """
        query_filter = _parameter_filter_substitution(parameters, query_filter)

        command = functools.partial(self._client.table.query, **kwargs)
        return ItemPaged(
            command,
            results_per_page=results_per_page,
            filter=query_filter,
            page_iterator_class=TablePropertiesPaged,
        )

    @distributed_trace
    def list_tables(self, *, results_per_page: Optional[int] = None, **kwargs) -> ItemPaged[TableItem]:
        """Queries tables under the given account.

        :keyword int results_per_page: Number of tables per page in returned ItemPaged
        :return: An iterator of :class:`~azure.data.tables.TableItem`
        :rtype: ~azure.core.paging.ItemPaged[~azure.data.tables.TableItem]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_query_tables.py
                :start-after: [START tsc_list_tables]
                :end-before: [END tsc_list_tables]
                :language: python
                :dedent: 16
                :caption: Listing all tables in a storage account
        """
        command = functools.partial(self._client.table.query, **kwargs)
        return ItemPaged(
            command,
            results_per_page=results_per_page,
            page_iterator_class=TablePropertiesPaged,
        )

    def get_table_client(self, table_name: str, **kwargs: Any) -> TableClient:
        """Get a client to interact with the specified table.

        The table need not already exist.

        :param str table_name: The table name
        :returns: A :class:`~azure.data.tables.TableClient` object.
        :rtype: ~azure.data.tables.TableClient

        """
        pipeline = Pipeline(
            transport=TransportWrapper(self._client._client._pipeline._transport),  # pylint: disable = protected-access
            policies=self._policies,
        )
        return TableClient(
            self.url,
            table_name=table_name,
            credential=self.credential,
            api_version=self.api_version,
            pipeline=pipeline,
            location_mode=self._location_mode,
            _hosts=self._hosts,
            **kwargs,
        )
