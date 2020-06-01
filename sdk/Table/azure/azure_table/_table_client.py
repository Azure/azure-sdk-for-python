from urllib.parse import urlparse, quote

import six
from azure.azure_table._deserialize import deserialize_table_creation
from azure.azure_table._generated import AzureTable
from azure.azure_table._generated.models import TableProperties, AccessPolicy, SignedIdentifier
from azure.azure_table._message_encoding import NoEncodePolicy, NoDecodePolicy
from azure.azure_table._shared.base_client import StorageAccountHostsMixin, parse_query, parse_connection_str
from azure.azure_table._shared.request_handlers import add_metadata_headers, serialize_iso
from azure.azure_table._shared.response_handlers import process_storage_error
from azure.azure_table._version import VERSION
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace


class TableClient(StorageAccountHostsMixin):
    def __init__(
            self, account_url,  # type: str
            table_name,  # type: str
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
        if not table_name:
            raise ValueError("Please specify a queue name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(parsed_url))

        _, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError("You need to provide either a SAS token or an account shared key to authenticate.")

        self.table_name = table_name
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(TableClient, self).__init__(parsed_url, service='table', credential=credential, **kwargs)

        self._config.message_encode_policy = kwargs.get('message_encode_policy', None) or NoEncodePolicy()
        self._config.message_decode_policy = kwargs.get('message_decode_policy', None) or NoDecodePolicy()
        self._client = AzureTable(self.url, pipeline=self._pipeline)
        self._client._config.version = kwargs.get('api_version', VERSION)  # pylint: disable=protected-access

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        table_name = self.table_name
        if isinstance(table_name, six.text_type):
            table_name = table_name.encode('UTF-8')
        return "{}://{}/{}{}".format(
            self.scheme,
            hostname,
            quote(table_name),
            self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            table_name,  # type: str
            credential=None,  # type: Any
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Create QueueClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Storage account.
        :param table_name: The queue name.
        :type table_name: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
        :returns: A queue client.
        :rtype: ~azure.storage.queue.QueueClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/queue_samples_message.py
                :start-after: [START create_queue_client_from_connection_string]
                :end-before: [END create_queue_client_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Create the queue client from connection string.
        """
        account_url, secondary, credential = parse_connection_str(
            conn_str, credential, 'queue')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(account_url, table_name=table_name, credential=credential, **kwargs)  # type: ignore

    @distributed_trace
    def create_queue(self, table_name, **kwargs):
        # type: (Optional[Any]) -> None
        table_properties = TableProperties(table_name)
        request_id_parameter = kwargs.pop('request_id_parameter', None)
        response_preference = kwargs.pop('response_preference', None)
        query_option = kwargs.pop('query_options', None)
        try:
            return self._client.table.create(  # type: ignore
                table_properties=table_properties,
                request_id_parameter=request_id_parameter,
                response_preference=response_preference,
                query_options=query_option,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def delete_queue(self, table_name, **kwargs):
        # type: (Optional[Any]) -> None
        request_id_parameter = kwargs.pop('request_id_parameter', None)
        try:
            self._client.table.delete(
                table_name=table_name,
                request_id_parameter=request_id_parameter,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def get_table_properties(self, **kwargs):
        # type: (Optional[Any]) -> TableProperties
        timeout = kwargs.pop('timeout', None)
        request_id_parameter = kwargs.pop('request_id_parameter', None)
        try:
            response = self._client.table.get_properties(
                timeout=timeout,
                request_id_parameter=request_id_parameter,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        response.name = self.table_name
        return response  # type: ignore

    @distributed_trace
    def get_table_access_policy(self, table, **kwargs):
        # type: (Optional[Any]) -> Dict[str, Any]
        timeout = kwargs.pop('timeout', None)
        request_id_parameter = kwargs.pop('request_id_parameter', None)
        try:
            _, identifiers = self._client.table.get_access_policy(
                table=table,
                timeout=timeout,
                request_id_parameter=request_id_parameter,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        return {s.id: s.access_policy or AccessPolicy() for s in identifiers}

    @distributed_trace
    def set_table_access_policy(self, table, signed_identifiers, **kwargs):
        # type: (Dict[str, AccessPolicy], Optional[Any]) -> None
        timeout = kwargs.pop('timeout', None)
        request_id_parameter = kwargs.pop('request_id_parameter', None)
        if len(signed_identifiers) > 15:
            raise ValueError(
                'Too many access policies provided. The server does not support setting '
                'more than 15 access policies on a single resource.')
        identifiers = []
        for key, value in signed_identifiers.items():
            if value:
                value.start = serialize_iso(value.start)
                value.expiry = serialize_iso(value.expiry)
            identifiers.append(SignedIdentifier(id=key, access_policy=value))
        signed_identifiers = identifiers  # type: ignore
        try:
            self._client.table.set_access_policy(
                table,
                timeout=timeout,
                request_id_parameter=request_id_parameter,
                table_acl=signed_identifiers or None,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
