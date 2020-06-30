from azure.table import VERSION
from azure.table._generated.aio._azure_table_async import AzureTable
from azure.table._shared.base_client_async import AsyncStorageAccountHostsMixin
from azure.table._shared.policies_async import ExponentialRetry
from azure.table._table_client import TableClient as TableClientBase


class TableClient(AsyncStorageAccountHostsMixin, TableClientBase):
    """A client to interact with a specific Queue.

    :param str account_url:
        The URL to the storage account. In order to create a client given the full URI to the queue,
        use the :func:`from_queue_url` classmethod.
    :param queue_name: The name of the queue.
    :type queue_name: str
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string, an account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is '2019-07-07'.
        Setting to an older version may result in reduced feature compatibility.
    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    :keyword message_encode_policy: The encoding policy to use on outgoing messages.
        Default is not to encode messages. Other options include :class:`TextBase64EncodePolicy`,
        :class:`BinaryBase64EncodePolicy` or `None`.
    :keyword message_decode_policy: The decoding policy to use on incoming messages.
        Default value is not to decode messages. Other options include :class:`TextBase64DecodePolicy`,
        :class:`BinaryBase64DecodePolicy` or `None`.

    .. admonition:: Example:

        .. literalinclude:: ../samples/queue_samples_message_async.py
            :start-after: [START async_create_queue_client]
            :end-before: [END async_create_queue_client]
            :language: python
            :dedent: 16
            :caption: Create the queue client with url and credential.

        .. literalinclude:: ../samples/queue_samples_message_async.py
            :start-after: [START async_create_queue_client_from_connection_string]
            :end-before: [END async_create_queue_client_from_connection_string]
            :language: python
            :dedent: 8
            :caption: Create the queue client with a connection string.
    """

    def __init__(
            self,
            account_url,  # type: str
            queue_name,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        kwargs["retry_policy"] = kwargs.get("retry_policy") or ExponentialRetry(**kwargs)
        loop = kwargs.pop('loop', None)
        super(TableClient, self).__init__(
            account_url, queue_name=queue_name, credential=credential, loop=loop, **kwargs
        )
        self._client = AzureTable(self.url, pipeline=self._pipeline, loop=loop)  # type: ignore
        self._client._config.version = kwargs.get('api_version', VERSION)  # pylint: disable=protected-access
        self._loop = loop
