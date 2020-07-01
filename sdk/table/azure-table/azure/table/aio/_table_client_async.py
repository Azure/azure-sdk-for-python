import functools

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.table import VERSION
from azure.table._deserialization import _convert_to_entity
from azure.table._entity import Entity
from azure.table._generated.aio._azure_table_async import AzureTable
from azure.table._generated.models import SignedIdentifier
from azure.table._models import AccessPolicy
from azure.table._serialization import _add_entity_properties
from azure.table._serialize import _get_match_headers
from azure.table._shared.base_client_async import AsyncStorageAccountHostsMixin
from azure.table._shared.policies_async import ExponentialRetry
from azure.table._shared.request_handlers import serialize_iso
from azure.table._shared.response_handlers import return_headers_and_deserialized, process_storage_error
from azure.table._table_client import TableClient as TableClientBase
from azure.table.aio._models import TableEntityPropertiesPaged


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
        # type: (...) -> List["models.SignedIdentifier"]
        """Retrieves details about any stored access policies specified on the table that may be
        used with Shared Access Signatures.

                :keyword callable cls: A custom type or function that will be passed the direct response
                :return: list of SignedIdentifier, or the result of cls(response)
                :rtype: list[~azure.table.models.SignedIdentifier]
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
    async def set_table_access_policy(self, signed_identifiers, **kwargs):
        # type: (...) -> None
        """Sets stored access policies for the table that may be used with Shared Access Signatures.

                :param signed_identifiers:
                :type signed_identifiers: {id,AccessPolicy}
                :keyword callable cls: A custom type or function that will be passed the direct response
                :return: None, or the result of cls(response)
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
        # type: (...) -> "models.TableServiceProperties"
        """Gets the properties of an account's Table service,
        including properties for Analytics and CORS (Cross-Origin Resource Sharing) rules.

        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: TableServiceProperties, or the result of cls(response)
        :rtype: ~azure.table.models.TableServiceProperties
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
    async def delete_entity(
            self,
            partition_key,
            row_key,
            etag=None,
            match_condition=None,
            **kwargs
    ):
        # type: (...) -> None
        """Deletes the specified entity in a table.

        :param match_condition: MatchCondition
        :type match_condition: ~azure.core.MatchConditions
        :param etag: Etag of the entity
        :type etag: str
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if_match, if_not_match = _get_match_headers(kwargs=dict(kwargs, etag=etag, match_condition=match_condition),
                                                    etag_param='etag', match_param='match_condition')

        try:
            await self._client.table.delete_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                if_match=if_match or if_not_match or '*',
                **kwargs)
        except ResourceNotFoundError:
            raise ResourceNotFoundError

    @distributed_trace_async
    async def create_entity(
            self,
            headers=None,
            table_entity_properties=None,
            query_options=None,
            response_hook=None,  # pylint:disable=W0613
            **kwargs
    ):
        # type: (...) -> Dict[str, object]
        """Insert entity in a table.

        :param response_hook:
        :type response_hook:
        :param headers: Headers for service request
        :type headers: HttpResponse Headers
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, object]
        :param query_options: Parameter group.
        :type query_options: ~azure.table.models.QueryOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: dict mapping str to object, or the result of cls(response)
        :rtype: dict[str, object] or None
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
                query_options=query_options,
                **dict(kwargs, headers=headers)
            )
            properties = _convert_to_entity(inserted_entity)
            return Entity(properties)
        except ValueError as error:
            process_storage_error(error)

    @distributed_trace_async
    async def update_entity(
            self,
            partition_key=None,
            row_key=None,
            etag=None,
            match_condition=None,
            response_hook=None,  # pylint:disable=W0613
            table_entity_properties=None,
            **kwargs
    ):
        # type: (...) -> None
        """Update entity in a table.

        :param response_hook:
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, object]
        :param match_condition: MatchCondition
        :type match_condition: ~azure.core.MatchConditions
        :param etag: Etag of the entity
        :type etag: str
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if_match, if_not_match = _get_match_headers(kwargs=dict(kwargs, etag=etag, match_condition=match_condition),
                                                    etag_param='etag', match_param='match_condition')

        if table_entity_properties:
            partition_key = table_entity_properties['PartitionKey']
            row_key = table_entity_properties['RowKey']
            table_entity_properties = _add_entity_properties(table_entity_properties)

        try:
            await self._client.table.update_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=table_entity_properties,
                if_match=if_match or if_not_match or "*",
                **kwargs)
        except ResourceNotFoundError:
            raise ResourceNotFoundError

    @distributed_trace_async
    async def merge_entity(
            self,
            partition_key=None,  # type: str
            row_key=None,  # type: str
            etag=None,  # type: str
            match_condition=None,  # type: MatchConditions
            table_entity_properties=None,  # type: Optional[Dict[str, object]]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Merge entity in a table.

        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
         :param match_condition: MatchCondition
        :type match_condition: ~azure.core.MatchConditions
        :param etag: Etag of the entity
        :type etag: str
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, object]
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if_match, if_not_match = _get_match_headers(kwargs=dict(kwargs, etag=etag, match_condition=match_condition),
                                                    etag_param='etag', match_param='match_condition')

        if table_entity_properties:
            partition_key = table_entity_properties['PartitionKey']
            row_key = table_entity_properties['RowKey']
            table_entity_properties = _add_entity_properties(table_entity_properties)

        try:
            await self._client.table.merge_entity(table=self.table_name, partition_key=partition_key,
                                                  row_key=row_key, if_match=if_match or if_not_match or '*',
                                                  table_entity_properties=table_entity_properties, **kwargs)

        except ResourceNotFoundError:
            raise ResourceNotFoundError

    @distributed_trace_async
    async def query_entities(
            self,
            headers=None,
            query_options=None,
            **kwargs
    ):
        # type: (...) -> "models.TableEntityQueryResponse"
        """Queries entities in a table.

        :param headers: Headers for service request
        :type headers: HttpResponse Headers
        :param query_options: Parameter group.
        :type query_options: ~azure.table.models.QueryOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: TableEntityQueryResponse, or the result of cls(response)
        :rtype: ~azure.table.models.TableEntityQueryResponse
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        command = functools.partial(
            self._client.table.query_entities,
            **dict(kwargs, headers=headers))
        return AsyncItemPaged(
            command, results_per_page=query_options, table=self.table_name,
            page_iterator_class=TableEntityPropertiesPaged
        )

    @distributed_trace_async
    async def query_entities_with_partition_and_row_key(
            self,
            partition_key,
            row_key,
            headers=None,
            query_options=None,
            response_hook=None,  # pylint:disable=W0613
            **kwargs
    ):
        # type: (...) -> "models.TableEntityQueryResponse"
        """Queries entities in a table.

        :param response_hook:
        :type response_hook:
        :param headers: Headers for service request
        :type headers: HttpResponse Headers
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param query_options: Parameter group.
        :type query_options: ~azure.table.models.QueryOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: TableEntityQueryResponse, or the result of cls(response)
        :rtype: ~azure.table.models.TableEntityQueryResponse
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        try:
            entity = await self._client.table.query_entities_with_partition_and_row_key(table=self.table_name,
                                                                                        partition_key=partition_key,
                                                                                        row_key=row_key,
                                                                                        query_options=query_options,
                                                                                        **dict(kwargs, headers=headers))

            properties = _convert_to_entity(entity.additional_properties)

            return Entity(properties)
        except ResourceNotFoundError:
            raise ResourceNotFoundError

    @distributed_trace_async
    async def upsert_insert_merge_entity(
            self,
            partition_key=None,
            row_key=None,
            table_entity_properties=None,
            query_options=None,
            **kwargs
    ):
        # type: (...) -> Entity
        """Merge or Insert entity into table.


        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, object]
        :param query_options: Parameter group.
        :type query_options: ~azure.table.models.QueryOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: TableEntityQueryResponse, or the result of cls(response)
        :rtype: ~azure.table.models.TableEntityQueryResponse
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        # Insert or Merge
        if table_entity_properties:
            # Losing a key here
            partition_key = table_entity_properties['PartitionKey']
            row_key = table_entity_properties['RowKey']
            table_entity_properties = _add_entity_properties(table_entity_properties)

        try:
            merged_entity = await self._client.table.merge_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=table_entity_properties,
                query_options=query_options,
                **kwargs
            )
            return merged_entity
        except ResourceNotFoundError:
            insert_entity = await self.create_entity(
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=table_entity_properties,
                **kwargs
            )
            properties = _convert_to_entity(insert_entity)
            return Entity(properties)

    @distributed_trace_async
    async def upsert_insert_update_entity(
            self,
            partition_key=None,
            row_key=None,
            table_entity_properties=None,
            **kwargs
    ):
        # type: (...) -> Entity
        """Update or Insert entity into table.


        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, object]
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: TableEntityQueryResponse, or the result of cls(response)
        :rtype: ~azure.table.models.TableEntityQueryResponse
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        # Insert or Update
        if table_entity_properties:
            partition_key = table_entity_properties['PartitionKey']
            row_key = table_entity_properties['RowKey']
            table_entity_properties = _add_entity_properties(table_entity_properties)

        try:
            update_entity = await self._client.table.update_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=table_entity_properties,
                **kwargs)
            return update_entity
        except ResourceNotFoundError:
            insert_entity = await self.create_entity(
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=table_entity_properties
            )
            return Entity(insert_entity)
