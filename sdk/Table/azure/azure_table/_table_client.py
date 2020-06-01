from urllib.parse import urlparse, quote

import six
from azure.azure_table._generated import AzureTable
from azure.azure_table._message_encoding import NoEncodePolicy, NoDecodePolicy
from azure.azure_table._shared.base_client import StorageAccountHostsMixin, parse_query, parse_connection_str
from azure.azure_table._version import VERSION


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
