import functools

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.table import VERSION
from azure.table._entity import Entity
from azure.table._generated.aio._azure_table_async import AzureTable
from azure.table._generated.models import SignedIdentifier, TableProperties, QueryOptions
from azure.table._models import AccessPolicy
from azure.table._shared.base_client import parse_connection_str
from azure.table._shared.base_client_async import AsyncStorageAccountHostsMixin
from azure.table._shared.policies_async import ExponentialRetry
from azure.table._shared.request_handlers import serialize_iso
from azure.table._shared.response_handlers import return_headers_and_deserialized, process_storage_error
from azure.table._table_client import TableClient as TableClientBase

from .._models import TableEntityPropertiesPaged, UpdateMode
from .._deserialize import _convert_to_entity
from .._serialize import _add_entity_properties, _get_match_headers

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
            table_name,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        kwargs["retry_policy"] = kwargs.get("retry_policy") or ExponentialRetry(**kwargs)
        loop = kwargs.pop('loop', None)
        super(TableClient, self).__init__(
            account_url, table_name=table_name, credential=credential, loop=loop, **kwargs
        )
        self._client = AzureTable(self.url, pipeline=self._pipeline, loop=loop)  # type: ignore
        self._client._config.version = kwargs.get('api_version', VERSION)  # pylint: disable=protected-access
        self._loop = loop

    @distributed_trace_async
    async def get_table_access_policy(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> dict[str,AccessPolicy]
        """Retrieves details about any stored access policies specified on the table that may be
        used with Shared Access Signatures.
        :return: Dictionary of SignedIdentifiers
        :rtype: dict[str,AccessPolicy]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        timeout = kwargs.pop('timeout', None)
        try:
            _, identifiers = await self._client.table.get_access_policy(
                table=self.table_name,
                timeout=timeout,
                cls=return_headers_and_deserialized,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        return {s.id: s.access_policy or AccessPolicy() for s in identifiers}

    @distributed_trace_async
    async def set_table_access_policy(
            self,
            signed_identifiers,  # type: dict[str,AccessPolicy]
            **kwargs):
        # type: (...) -> None
        """Sets stored access policies for the table that may be used with Shared Access Signatures.
        :param signed_identifiers:
        :type signed_identifiers: dict[str,AccessPolicy]
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
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
        signed_identifiers = identifiers  # type: ignore
        try:
            await self._client.table.set_access_policy(
                table=self.table_name,
                table_acl=signed_identifiers or None,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_table_properties(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> TableServiceProperties
        """Gets the properties of an account's Table service,
        including properties for Analytics and CORS (Cross-Origin Resource Sharing) rules.
        :return: TableServiceProperties
        :rtype: TableServiceProperties
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        timeout = kwargs.pop('timeout', None)
        request_id_parameter = kwargs.pop('request_id_parameter', None)
        try:
            response = await self._client.service.get_properties(
                timeout=timeout,
                request_id_parameter=request_id_parameter,
                **kwargs)
            return response
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def create_table(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> str
        """Creates a new table under the given account.
        :return: Table created
        :rtype: str
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        table_properties = TableProperties(table_name=self.table_name, **kwargs)
        table = await self._client.table.create(table_properties)
        return table

    @distributed_trace_async
    async def delete_table(
            self,
            request_id_parameter=None,  # type: Optional[str]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Creates a new table under the given account.
        :param request_id_parameter: Request Id parameter
        :type request_id_parameter: str
        :return: None
        :rtype: None
        """
        await self._client.table.delete(table=self.table_name, request_id_parameter=request_id_parameter, **kwargs)

    @distributed_trace_async
    async def delete_entity(
            self,
            partition_key,  # type: str
            row_key,  # type: str
            etag=None,  # type: Optional[object]
            match_condition=None,  # type: Optional[MatchCondition]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Deletes the specified entity in a table.
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param etag: Etag of the entity
        :type etag: str
        :param match_condition: MatchCondition
        :type match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if_match, if_not_match = _get_match_headers(kwargs=dict(kwargs, etag=etag, match_condition=match_condition),
                                                    etag_param='etag', match_param='match_condition')

        await self._client.table.delete_entity(
            table=self.table_name,
            partition_key=partition_key,
            row_key=row_key,
            if_match=if_match or if_not_match or '*',
            **kwargs)

    @distributed_trace_async
    async def create_entity(
            self,
            table_entity_properties,  # type: dict[str,str]
            **kwargs  # type: Any
    ):
        # type: (...) -> Entity
        """Insert entity in a table.
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, str]
        :return: Entity mapping str to azure.table.EntityProperty
        :rtype: ~azure.table.Entity
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if table_entity_properties:

            if "PartitionKey" in table_entity_properties and "RowKey" in table_entity_properties:
                table_entity_properties = _add_entity_properties(table_entity_properties)
            else:
                raise ValueError
        try:

            inserted_entity = await self._client.table.insert_entity(
                table=self.table_name,
                table_entity_properties=table_entity_properties,
                **kwargs
            )
            properties = _convert_to_entity(inserted_entity)
            return Entity(properties)
        except ValueError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def update_entity(  # pylint:disable=R1710
            self,
            mode,  # type: Any
            table_entity_properties,  # type: dict[str,str]
            partition_key=None,  # type: Optional[str]
            row_key=None,  # type: Optional[str]
            etag=None,  # type: Optional[object]
            match_condition=None,  # type: Optional[MatchCondition]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Update entity in a table.
        :param mode: Merge or Replace entity
        :type mode: ~azure.table.UpdateMode
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, str]
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param etag: Etag of the entity
        :type etag: str
        :param match_condition: MatchCondition
        :type match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if_match, if_not_match = _get_match_headers(kwargs=dict(kwargs, etag=etag, match_condition=match_condition),
                                                    etag_param='etag', match_param='match_condition')

        if table_entity_properties:
            partition_key = table_entity_properties['PartitionKey']
            row_key = table_entity_properties['RowKey']
            table_entity_properties = _add_entity_properties(table_entity_properties)

        if mode is UpdateMode.replace:
            await self._client.table.update_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=table_entity_properties,
                if_match=if_match or if_not_match or "*",
                **kwargs)
        if mode is UpdateMode.merge:
            await self._client.table.merge_entity(table=self.table_name, partition_key=partition_key,
                                                  row_key=row_key, if_match=if_match or if_not_match or "*",
                                                  table_entity_properties=table_entity_properties, **kwargs)

    @distributed_trace
    def query_entities(
            self,
            results_per_page=None,
            select=None,
            filter=None,  # pylint: disable=W0622
            **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[Entity]
        """Queries entities in a table.
        :param results_per_page: Number of entities per page in return ItemPaged
        :type results_per_page: int
        :param select: Specify desired properties of an entity to return certain entities
        :type select: str
        :param filter: Specify a filter to return certain entities
        :type filter: str
        :return: Query of table entities
        :rtype: ItemPaged[Entity]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        query_options = QueryOptions(top=results_per_page, select=select, filter=filter)

        command = functools.partial(
            self._client.table.query_entities,
            **kwargs)
        return AsyncItemPaged(
            command, results_per_page=query_options, table=self.table_name,
            page_iterator_class=TableEntityPropertiesPaged
        )

    @distributed_trace_async
    async def get_entity(
            self,
            partition_key,  # type: str
            row_key,  # type: str
            results_per_page=None,
            select=None,
            filter=None,  # pylint: disable=W0622
            **kwargs  # type: Any
    ):
        # type: (...) -> Entity
        """Queries entities in a table.
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param results_per_page: Number of entities per page in return ItemPaged
        :type results_per_page: int
        :param select: Specify desired properties of an entity to return certain entities
        :type select: str
        :param filter: Specify a filter to return certain entities
        :type filter: str
        :return: Entity mapping str to azure.table.EntityProperty
        :rtype: ~azure.table.Entity
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        query_options = QueryOptions(top=results_per_page, select=select, filter=filter)
        entity = await self._client.table.query_entities_with_partition_and_row_key(table=self.table_name,
                                                                                    partition_key=partition_key,
                                                                                    row_key=row_key,
                                                                                    query_options=query_options,
                                                                                    **kwargs)
        properties = _convert_to_entity(entity.additional_properties)
        return Entity(properties)

    @distributed_trace_async
    async def upsert_entity(  # pylint:disable=R1710
            self,
            mode,  # type: Any
            table_entity_properties,  # type: dict[str,str]
            partition_key=None,  # type: Optional[str]
            row_key=None,  # type: Optional[str]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        # TODO: Return type will need to change
        """Update/Merge or Insert entity into table.
        :param mode: Merge or Replace and Insert on fail
        :type mode: ~azure.table.UpdateMode
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, str]
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :return: Entity mapping str to azure.table.EntityProperty or None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if table_entity_properties:
            partition_key = table_entity_properties['PartitionKey']
            row_key = table_entity_properties['RowKey']
            table_entity_properties = _add_entity_properties(table_entity_properties)

        if mode is UpdateMode.merge:
            try:
                await self._client.table.merge_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=table_entity_properties,
                    **kwargs
                )
            except ResourceNotFoundError:
                await self.create_entity(
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=table_entity_properties,
                    **kwargs
                )
        if mode is UpdateMode.replace:
            try:
                await self._client.table.update_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=table_entity_properties,
                    **kwargs)
            except ResourceNotFoundError:
                await self.create_entity(
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=table_entity_properties,
                    **kwargs
                )
