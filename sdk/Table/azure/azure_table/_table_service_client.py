from urllib.parse import urlparse

from azure.azure_table._generated import AzureTable
from azure.azure_table._generated.models import TableProperties, TableServiceStats
from azure.azure_table._shared.base_client import StorageAccountHostsMixin, parse_connection_str, parse_query
from azure.azure_table._shared.models import LocationMode
from azure.azure_table._shared.response_handlers import process_storage_error
from azure.azure_table._version import VERSION
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace


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
            conn_str, credential, 'queue')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(account_url, credential=credential, **kwargs)

    def get_service_stats(self, **kwargs):
        # type: (Optional[Any]) -> Dict[str, Any]
        timeout = kwargs.pop('timeout', None)
        try:
            stats = self._client.service.get_statistics(  # type: ignore
                timeout=timeout, use_location=LocationMode.SECONDARY, **kwargs)
            return TableServiceStats(stats)
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

    @distributed_trace
    def delete_table(
            self,
            table_name,
            request_id_parameter=None
    ):
        response = self._client.table.delete(table=table_name, request_id_parameter=request_id_parameter)
        return response

    @distributed_trace
    def query_table(
            self,
            request_id_parameter=None,
            next_table_name=None,
            query_options=None
    ):
        # somehow use self._query_string to query things
        response = self._client.table.query(next_table_name=next_table_name)
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
        response = self._client.table.get_access_policy()

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
