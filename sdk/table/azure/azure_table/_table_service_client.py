import functools
from urllib.parse import urlparse

from azure.azure_table._generated import AzureTable
from azure.azure_table._generated.models import TableProperties, TableServiceStats, TableServiceProperties, \
    AccessPolicy, SignedIdentifier
from azure.azure_table._models import TablePropertiesPaged, service_stats_deserialize, service_properties_deserialize
from azure.azure_table._shared.base_client import StorageAccountHostsMixin, parse_connection_str, parse_query, \
    TransportWrapper
from azure.azure_table._shared.models import LocationMode
from azure.azure_table._shared.request_handlers import serialize_iso
from azure.azure_table._shared.response_handlers import process_storage_error, return_headers_and_deserialized
from azure.azure_table._version import VERSION
from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from azure.azure_table._table_client import TableClient
from msrest.pipeline import Pipeline


class TableServiceClient(StorageAccountHostsMixin):
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
            raise ValueError("You need to provide either a SAS token or an account shared key to authenticate.")
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(TableServiceClient, self).__init__(parsed_url, service='table', credential=credential, **kwargs)
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
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
    ):  # type: (...) -> TableServiceClient
        """Create TableServiceClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
        :returns: A Table service client.
        :rtype: ~azure.storage.table.TableClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_authentication.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the TableServiceClient with a connection string.
        """
        account_url, secondary, credential = parse_connection_str(
            conn_str, credential, 'table')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(account_url, credential=credential, **kwargs)

    @distributed_trace
    def get_table_access_policy(
            self,
            table_name,
            **kwargs
    ):
        timeout = kwargs.pop('timeout', None)
        try:
            _, identifiers = self._client.table.get_access_policy(
                table=table_name,
                timeout=timeout,
                cls=return_headers_and_deserialized,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        return {s.id: s.access_policy or AccessPolicy() for s in identifiers}

    @distributed_trace
    def set_table_access_policy(self, table_name, signed_identifiers, **kwargs):
        # type: (Dict[str, AccessPolicy], Optional[Any]) -> None
        if len(signed_identifiers) > 5:
            raise ValueError(
                'Too many access policies provided. The server does not support setting '
                'more than 5 access policies on a single resource.')
        identifiers = []
        for key, value in signed_identifiers.items():
            if value:
                value.start = serialize_iso(value.start)
                value.expiry = serialize_iso(value.expiry)
            identifiers.append(SignedIdentifier(id=key, access_policy=value))
        try:
            self._client.table.set_access_policy(
                table=table_name,
                table_acl=identifiers or None,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def get_service_stats(self, **kwargs):
        # type: (Optional[Any]) -> Dict[str, Any]
        try:
            # failing on get_statistics
            stats = self._client.service.get_statistics(**kwargs)
            return service_stats_deserialize(stats)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def get_service_properties(self, **kwargs):
        # type: (Optional[Any]) -> Dict[str, Any]
        timeout = kwargs.pop('timeout', None)
        try:
            service_props = self._client.service.get_properties(timeout=timeout, **kwargs)  # type: ignore
            return service_properties_deserialize(service_props)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def set_service_properties(  # type: ignore
            self, analytics_logging=None,  # type: Optional[TableAnalyticsLogging]
            hour_metrics=None,  # type: Optional[Metrics]
            minute_metrics=None,  # type: Optional[Metrics]
            cors=None,  # type: Optional[List[CorsRule]]
            **kwargs
    ):
        # type: (...) -> None

        timeout = kwargs.pop('timeout', None)
        props = TableServiceProperties(
            logging=analytics_logging,
            hour_metrics=hour_metrics,
            minute_metrics=minute_metrics,
            cors=cors
        )
        try:
            return self._client.service.set_properties(props, timeout=timeout, **kwargs)  # type: ignore
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def create_table(
            self,
            table_name
    ):
        table_properties = TableProperties(table_name=table_name)
        response = self._client.table.create(table_properties)
        return response
        # table = self.get_table_client(table=table_name)

    @distributed_trace
    def delete_table(
            self,
            table_name,
            request_id_parameter=None
    ):
        response = self._client.table.delete(table=table_name, request_id_parameter=request_id_parameter)
        return response
        # table = self.get_table_client(table=table_name)
        # table.delete_queue(table_name)

    @distributed_trace
    def list_tables(
            self,
            request_id_parameter=None,
            next_table_name=None,  # type: Optional[str]
            query_options=None,  # type: Optional[QueryOptions]
            **kwargs
    ):
        command = functools.partial(
            self._client.table.query,
            **kwargs)
        return ItemPaged(
            command, results_per_page=query_options,
            page_iterator_class=TablePropertiesPaged
        )

    @distributed_trace
    def query_tables(
            self,
            request_id_parameter=None,
            next_table_name=None,
            query_options=None,
            **kwargs
    ):
        command = functools.partial(self._client.table.query,
                                    **kwargs)
        return ItemPaged(
            command, results_per_page=query_options,
            page_iterator_class=TablePropertiesPaged
        )

    def upsert_item(self,
                    table_name,
                    timeout=None,
                    request_id_parameter=None,
                    if_match=None,
                    table_entity_properties=None,
                    query_options=None
                    ):
        response = self._client.table.insert_entity(table=table_name, table_entity_properties=table_entity_properties)
        return response

    @distributed_trace
    def query_table_entities(
            self,
            table_name,
            timeout=None,
            request_id_parameter=None,
            next_partition_key=None,
            next_row_key=None,
            query_options=None
    ):
        response = self._client.table.query_entities(table_name=table_name)

    @distributed_trace
    def query_table_entities_with_partition_and_row_key(
            self,
            table_name,
            partition_key,
            row_key,
            timeout=None,
            request_id_parameter=None,
            query_options=None
    ):
        response = self._client.table.query_entities_with_partition_and_row_key(table_name=table_name)

    @distributed_trace
    def update_entity(
            self,
            table_name,
            partition_key,
            row_key,
            timeout=None,
            request_id_parameter=None,
            if_match=None,
            table_entity_properties=None,
            query_options=None
    ):
        response = self._client.table.update_entity()

    @distributed_trace
    def merge_entity(
            self,
            table_name,
            partition_key,
            row_key,
            timeout=None,
            request_id_parameter=None,
            if_match=None,
            table_entity_properties=None,
            query_options=None
    ):
        response = self._client.table.merge_entity()

    @distributed_trace
    def delete_entity(
            self,
            table_name,
            partition_key,
            row_key,
            if_match,
            timeout=None,
            request_id_parameter=None,
            query_options=None
    ):
        response = self._client.table.delete_entity()

    @distributed_trace
    def insert_entity(
            self,
            table_name,
            timeout=None,
            request_id_parameter=None,
            if_match=None,
            table_entity_properties=None,
            query_options=None
    ):
        response = self._client.table.insert_entity()

    def get_access_policy(
            self,
            table_name,
            timeout=None,
            request_id_parameter=None
    ):
        response = self._client.table.get_access_policy(table=table_name)

    def set_access_policy(
            self,
            table_name,
            timeout=None,
            request_id_parameter=None,
            table_acl=None
    ):
        response = self._client.table.set_access_policy()

    def batch(
            self,
            *reqs
    ):
        response = self.batch(*reqs)
        return response

    def get_table_client(self, table, **kwargs):
        # type: (Union[TableProperties, str], Optional[Any]) -> TableClient

        try:
            table_name = table.name
        except AttributeError:
            table_name = table

        _pipeline = Pipeline(
            transport=TransportWrapper(self._pipeline._transport),  # pylint: disable = protected-access
            policies=self._pipeline._impl_policies  # pylint: disable = protected-access
        )

        return TableClient(
            self.url, table_name=table_name, credential=self.credential,
            key_resolver_function=self.key_resolver_function, require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key, api_version=self.api_version, _pipeline=_pipeline,
            _configuration=self._config, _location_mode=self._location_mode, _hosts=self._hosts, **kwargs)
