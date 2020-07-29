# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from typing import (
    Union,
    Any,
)

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.data.tables import VERSION
from azure.data.tables._entity import TableEntity
from azure.data.tables._generated.aio._azure_table_async import AzureTable
from azure.data.tables._generated.models import SignedIdentifier, TableProperties, QueryOptions
from azure.data.tables._models import AccessPolicy
from azure.data.tables._shared.base_client_async import AsyncStorageAccountHostsMixin
from azure.data.tables._shared.policies_async import ExponentialRetry
from azure.data.tables._shared.request_handlers import serialize_iso
from azure.data.tables._shared.response_handlers import return_headers_and_deserialized, process_table_error

from .._models import UpdateMode
from ._models import TableEntityPropertiesPaged, Table
from .._deserialize import _convert_to_entity
from .._serialize import _add_entity_properties, _get_match_headers
from .._shared._table_client_base import TableClientBase


class TableClient(AsyncStorageAccountHostsMixin, TableClientBase):
    """ :ivar str account_name: Name of the storage account (Cosmos or Azure)"""

    def __init__(
            self,
            account_url,  # type: str
            table_name,  # type: str
            credential,  # type : Optional[Any]=None
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Create TableClient from a Credential.

              :param account_url:
                  A url to an Azure Storage account.
              :type account_url: str
              :param table_name: The table name.
              :type table_name: str
              :param credential:
                  The credentials with which to authenticate. This is optional if the
                  account URL already has a SAS token, or the connection string already has shared
                  access key values. The value can be a SAS token string, an account shared access
                  key.
              :type credential: str

              :returns: None
              """
        kwargs["retry_policy"] = kwargs.get("retry_policy") or ExponentialRetry(**kwargs)
        loop = kwargs.pop('loop', None)
        super(TableClient, self).__init__(
            account_url, table_name=table_name, credential=credential, loop=loop, **kwargs
        )
        self._client = AzureTable(self.url, pipeline=self._pipeline, loop=loop)
        self._client._config.version = kwargs.get('api_version', VERSION)  # pylint: disable = W0212
        self._loop = loop

    @distributed_trace_async
    async def get_table_access_policy(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> dict[str,AccessPolicy]
        """
        Retrieves details about any stored access policies specified on the table that may be
        used with Shared Access Signatures.
        :return: Dictionary of SignedIdentifiers
        :rtype: dict[str,~azure.data.tables.AccessPolicy]
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
            process_table_error(error)
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
        self._validate_signed_identifiers(signed_identifiers)
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
            process_table_error(error)

    @distributed_trace_async
    async def create_table(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> Table
        """Creates a new table under the given account.
        :return: Table created
        :rtype: Table
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        table_properties = TableProperties(table_name=self.table_name, **kwargs)
        table = await self._client.table.create(table_properties)
        return Table(table)

    @distributed_trace_async
    async def delete_table(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Creates a new table under the given account.
        :return: None
        :rtype: None
        """
        await self._client.table.delete(table=self.table_name, **kwargs)

    @distributed_trace_async
    async def delete_entity(
            self,
            partition_key,  # type: str
            row_key,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Deletes the specified entity in a table.
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :keyword str etag: Etag of the entity
        :keyword  ~azure.core.MatchConditions match_condition: MatchCondition
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if_match, if_not_match = _get_match_headers(kwargs=dict(kwargs, etag=kwargs.pop('etag', None),
                                                                match_condition=kwargs.pop('match_condition', None)),
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
            entity,  # type: Union[TableEntity, dict[str,str]]
            **kwargs  # type: Any
    ):
        # type: (...) -> TableEntity
        """Insert entity in a table.
        :param entity: The properties for the table entity.
        :type entity: dict[str, str]
        :return: TableEntity mapping str to azure.data.tables.EntityProperty
        :rtype: ~azure.data.tables.TableEntity
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if entity:
            if "PartitionKey" in entity and "RowKey" in entity:
                entity = _add_entity_properties(entity)
            else:
                raise ValueError('PartitionKey and RowKey were not provided in entity')
        try:
            inserted_entity = await self._client.table.insert_entity(
                table=self.table_name,
                table_entity_properties=entity,
                **kwargs
            )
            properties = _convert_to_entity(inserted_entity)
            return properties
        except ResourceNotFoundError as error:
            process_table_error(error)

    @distributed_trace_async
    async def update_entity(
            self,
            entity,  # type: Union[TableEntity, dict[str,str]]
            mode=UpdateMode.MERGE,  # type: UpdateMode
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Update entity in a table.
        :param mode: Merge or Replace entity
        :type mode: ~azure.data.tables.UpdateMode
        :param entity: The properties for the table entity.
        :type entity: dict[str, str]
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
        if_match, if_not_match = _get_match_headers(kwargs=dict(kwargs, etag=kwargs.pop('etag', None),
                                                                match_condition=kwargs.pop('match_condition', None)),
                                                    etag_param='etag', match_param='match_condition')

        partition_key = entity['PartitionKey']
        row_key = entity['RowKey']
        entity = _add_entity_properties(entity)

        if mode is UpdateMode.REPLACE:
            await self._client.table.update_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=entity,
                if_match=if_match or if_not_match or "*",
                **kwargs)
        elif mode is UpdateMode.MERGE:
            await self._client.table.merge_entity(table=self.table_name, partition_key=partition_key,
                                                  row_key=row_key, if_match=if_match or if_not_match or "*",
                                                  table_entity_properties=entity, **kwargs)
        else:
            raise ValueError('Mode type is not supported')

    @distributed_trace
    def list_entities(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[TableEntity]
        """Lists entities in a table.

        :keyword int results_per_page: Number of entities per page in return ItemPaged
        :keyword Union[str, list(str)] select: Specify desired properties of an entity to return certain entities
        :return: Query of table entities
        :rtype: AsyncItemPaged[TableEntity]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        user_select = kwargs.pop('select', None)
        if user_select and not isinstance(user_select, str):
            user_select = ", ".join(user_select)

        query_options = QueryOptions(top=kwargs.pop('results_per_page', None), select=user_select)

        command = functools.partial(
            self._client.table.query_entities,
            **kwargs)
        return AsyncItemPaged(
            command, results_per_page=query_options, table=self.table_name,
            page_iterator_class=TableEntityPropertiesPaged
        )

    @distributed_trace
    def query_entities(
            self,
            filter,  # type: str  # pylint: disable = W0622
            **kwargs
    ):
        # type: (...) -> AsyncItemPaged[TableEntity]
        """Lists entities in a table.

        :param str filter: Specify a filter to return certain entities
        :keyword int results_per_page: Number of entities per page in return ItemPaged
        :keyword Union[str, list[str]] select: Specify desired properties of an entity to return certain entities
        :keyword dict parameters: Dictionary for formatting query with additional, user defined parameters
        :return: Query of table entities
        :rtype: ItemPaged[TableEntity]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        parameters = kwargs.pop('parameters', None)
        filter = self._parameter_filter_substitution(parameters, filter)  # pylint: disable = W0622

        user_select = kwargs.pop('select', None)
        if user_select and not isinstance(user_select, str):
            user_select = ", ".join(user_select)

        query_options = QueryOptions(top=kwargs.pop('results_per_page', None), select=user_select,
                                     filter=filter)

        command = functools.partial(
            self._client.table.query_entities,
            query_options=query_options,
            **kwargs)
        return AsyncItemPaged(
            command, table=self.table_name,
            page_iterator_class=TableEntityPropertiesPaged
        )

    @distributed_trace_async
    async def get_entity(
            self,
            partition_key,  # type: str
            row_key,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> TableEntity
        """Queries entities in a table.
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :return: TableEntity mapping str to azure.data.tables.EntityProperty
        :rtype: ~azure.data.tables.TableEntity
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        entity = await self._client.table.query_entities_with_partition_and_row_key(table=self.table_name,
                                                                                    partition_key=partition_key,
                                                                                    row_key=row_key,
                                                                                    **kwargs)
        properties = _convert_to_entity(entity.additional_properties)
        return properties

    @distributed_trace_async
    async def upsert_entity(
            self,
            entity,  # type: Union[TableEntity, dict[str,str]]
            mode=UpdateMode.MERGE,  # type: UpdateMode
            **kwargs  # type: Any
    ):
        # type: (...) -> None

        """Update/Merge or Insert entity into table.
        :param mode: Merge or Replace and Insert on fail
        :type mode: ~azure.data.tables.UpdateMode
        :param entity: The properties for the table entity.
        :type entity: dict[str, str]
        :return: Entity mapping str to azure.data.tables.EntityProperty or None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        partition_key = entity['PartitionKey']
        row_key = entity['RowKey']
        entity = _add_entity_properties(entity)

        try:
            if mode is UpdateMode.MERGE:
                await self._client.table.merge_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=entity,
                    **kwargs
                )
            elif mode is UpdateMode.REPLACE:
                await self._client.table.update_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=entity,
                    **kwargs)
            else:
                raise ValueError('Mode type is not supported')
        except ResourceNotFoundError:
            await self.create_entity(
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=entity,
                **kwargs
            )
