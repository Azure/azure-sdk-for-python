# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import Any

from azure.core.pipeline import Pipeline

from azure.table._generated import AzureTable
from azure.table._generated.models import TableProperties, TableServiceProperties, QueryOptions
from azure.table._models import TablePropertiesPaged, service_stats_deserialize, service_properties_deserialize
from azure.table._base_client import parse_connection_str, TransportWrapper
from azure.table._shared.models import LocationMode
from azure.table._shared.response_handlers import process_table_error
from azure.table._version import VERSION
from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from azure.table._table_client import TableClient
from azure.table._shared._error import _validate_table_name
from azure.table._table_service_client_base import TableServiceClientBase


class TableServiceClient(TableServiceClientBase):
    """ :ivar str account_name: Name of the storage account (Cosmos or Azure)"""
    def __init__(
            self, account_url,  # type: str
            credential=None,  # type: Union[str,TokenCredential]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Create TableServiceClient from a Credential.

        :param account_url:
            A url to an Azure Storage account.
        :type account_url: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
        :type credential: Union[str,TokenCredential]
        :returns: None
        """

        super(TableServiceClient, self).__init__(account_url, service='table', credential=credential, **kwargs)
        self._client = AzureTable(self.url, pipeline=self._pipeline)
        self._client._config.version = kwargs.get('api_version', VERSION)  # pylint: disable=protected-access

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}/{}".format(self.scheme, hostname, self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            **kwargs  # type: Any
    ):  # type: (...) -> TableServiceClient
        """Create TableServiceClient from a Connection String.

        :param conn_str:
            A connection string to an Azure Storage account.
        :type conn_str: str
        :returns: A Table service client.
        :rtype: ~azure.table.TableServiceClient
        """
        account_url, secondary, credential = parse_connection_str(
            conn_str=conn_str, credential=None, service='table')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(account_url, credential=credential, **kwargs)

    @distributed_trace
    def get_service_stats(self, **kwargs):
        # type: (...) -> dict[str,object]
        """Retrieves statistics related to replication for the Table service. It is only available on the secondary
        location endpoint when read-access geo-redundant replication is enabled for the account.

        :return: Dictionary of Service Stats
        :rtype:dict[str, object]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        try:
            timeout = kwargs.pop('timeout', None)
            stats = self._client.service.get_statistics(  # type: ignore
                timeout=timeout, use_location=LocationMode.SECONDARY, **kwargs)
            return service_stats_deserialize(stats)
        except HttpResponseError as error:
            process_table_error(error)

    @distributed_trace
    def get_service_properties(self, **kwargs):
        # type: (...) -> dict[str,Any]
        """Gets the properties of an account's Table service,
        including properties for Analytics and CORS (Cross-Origin Resource Sharing) rules.

        :return: Dictionary of service properties
        :rtype:dict[str, Any]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        timeout = kwargs.pop('timeout', None)
        try:
            service_props = self._client.service.get_properties(timeout=timeout, **kwargs)  # type: ignore
            return service_properties_deserialize(service_props)
        except HttpResponseError as error:
            process_table_error(error)

    @distributed_trace
    def set_service_properties(
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
       :type analytics_logging: ~azure.table.TableAnalyticsLogging
       :param hour_metrics: Hour level metrics
       :type hour_metrics: ~azure.table.Metrics
       :param minute_metrics: Minute level metrics
       :type minute_metrics: ~azure.table.Metrics
       :param cors: Cross-origin resource sharing rules
       :type cors: ~azure.table.CorsRule
       :return: None
       :rtype: None
       :raises: ~azure.core.exceptions.HttpResponseError
       """
        props = TableServiceProperties(
            logging=analytics_logging,
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=cors
        )
        try:
            return self._client.service.set_properties(props, **kwargs)  # type: ignore
        except HttpResponseError as error:
            process_table_error(error)

    @distributed_trace
    def create_table(
            self,
            table_name,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> TableClient
        """Creates a new table under the given account.

        :param table_name: The Table name.
        :type table_name: str
        :return: TableClient, or the result of cls(response)
        :rtype: ~azure.table.TableClient
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        _validate_table_name(table_name)

        table_properties = TableProperties(table_name=table_name, **kwargs)
        self._client.table.create(table_properties)
        table = self.get_table_client(table_name=table_name)
        return table

    @distributed_trace
    def delete_table(
            self,
            table_name,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Creates a new table under the given account.

        :param table_name: The Table name.
        :type table_name: str
        :return: None
        :rtype: None
        """
        _validate_table_name(table_name)

        self._client.table.delete(table=table_name, **kwargs)

    @distributed_trace
    def query_tables(
            self,
            filter=None,  # pylint: disable=W0622
            **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[str]
        """Queries tables under the given account.

        :keyword int results_per_page: Number of tables per page in return ItemPaged
        :keyword str select: Specify desired properties of a table to return certain tables
        :param filter: Specify a filter to return certain tables
        :type filter: str
        :return: A query of tables
        :rtype: ItemPaged[str]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        query_options = QueryOptions(top=kwargs.pop('results_per_page', None), select=kwargs.pop('select', None),
                                     filter=filter)
        command = functools.partial(self._client.table.query,
                                    **kwargs)
        return ItemPaged(
            command, results_per_page=query_options,
            page_iterator_class=TablePropertiesPaged
        )

    @distributed_trace
    def list_tables(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[str]
        """Queries tables under the given account.

        :keyword int results_per_page: Number of tables per page in return ItemPaged
        :keyword str select: Specify desired properties of a table to return certain tables
        :keyword str filter: Specify desired filter for tables
        :return: A query of tables
        :rtype: ItemPaged[str]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        query_options = QueryOptions(top=kwargs.pop('results_per_page', None), select=kwargs.pop('select', None),
                                     filter=kwargs.pop('filter', None))

        command = functools.partial(self._client.table.query,
                                    **kwargs)
        return ItemPaged(
            command, results_per_page=query_options,
            page_iterator_class=TablePropertiesPaged
        )

    def get_table_client(self, table_name, **kwargs):
        # type: (Union[TableProperties, str], Optional[Any]) -> TableClient
        """Get a client to interact with the specified table.

       The table need not already exist.

       :param table_name:
           The table name
       :type table_name: str
       :returns: A :class:`~azure.table.TableClient` object.
       :rtype: ~azure.table.TableClient

       """
        try:
            table_name = table_name.name
        except AttributeError:
            table_name = table_name

        _pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport),  # pylint: disable = protected-access
            policies=self._pipeline._impl_policies  # pylint: disable = protected-access
        )

        return TableClient(
            self.url, table_name=table_name, credential=self.credential,
            key_resolver_function=self.key_resolver_function, require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key, api_version=self.api_version, _pipeline=_pipeline,
            _configuration=self._config, _location_mode=self._location_mode, _hosts=self._hosts, **kwargs)
