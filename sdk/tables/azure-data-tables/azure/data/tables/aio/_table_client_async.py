# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from typing import (
    Union,
    Any,
    Dict,
)

try:
    from urllib.parse import urlparse, unquote
except ImportError:
    from urlparse import urlparse  # type: ignore
    from urllib2 import unquote  # type: ignore

from azure.core.async_paging import AsyncItemPaged
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .._base_client import parse_connection_str
from .._constants import CONNECTION_TIMEOUT
from .._entity import TableEntity
from .._generated.aio import AzureTable
from .._generated.models import SignedIdentifier, TableProperties
from .._models import AccessPolicy, BatchTransactionResult
from .._serialize import serialize_iso
from .._deserialize import _return_headers_and_deserialized
from .._error import _process_table_error
from .._models import UpdateMode
from .._deserialize import _convert_to_entity, _trim_service_metadata
from .._serialize import _add_entity_properties, _get_match_headers
from .._table_client_base import TableClientBase
from ._base_client_async import AsyncStorageAccountHostsMixin
from ._models import TableEntityPropertiesPaged
from ._policies_async import ExponentialRetry
from ._table_batch_async import TableBatchOperations


class TableClient(AsyncStorageAccountHostsMixin, TableClientBase):
    """ :ivar str account_name: Name of the storage account (Cosmos or Azure)"""

    def __init__(
        self,
        account_url,  # type: str
        table_name,  # type: str
        credential=None,  # type: str
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
            access key values. The value can be a SAS token string or an account shared access
            key.
        :type credential: str

        :returns: None
        """
        kwargs["retry_policy"] = kwargs.get("retry_policy") or ExponentialRetry(
            **kwargs
        )
        loop = kwargs.pop("loop", None)
        super(TableClient, self).__init__(
            account_url,
            table_name=table_name,
            credential=credential,
            loop=loop,
            **kwargs
        )
        kwargs['connection_timeout'] = kwargs.get('connection_timeout') or CONNECTION_TIMEOUT
        self._configure_policies(**kwargs)
        self._client = AzureTable(
            self.url,
            policies=kwargs.pop('policies', self._policies),
            loop=loop,
            **kwargs
        )
        self._loop = loop

    @classmethod
    def from_connection_string(
        cls,
        conn_str,  # type: str
        table_name,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> TableClient
        """Create TableClient from a Connection string.

        :param conn_str:
            A connection string to an Azure Storage or Cosmos account.
        :type conn_str: str
        :param table_name: The table name.
        :type table_name: str
        :returns: A table client.
        :rtype: ~azure.data.tables.TableClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_client_async.py
                :start-after: [START create_table_client]
                :end-before: [END create_table_client]
                :language: python
                :dedent: 8
                :caption: Creating the TableClient from a connection string.
        """
        account_url, credential = parse_connection_str(
            conn_str=conn_str, credential=None, service="table", keyword_args=kwargs
        )
        return cls(account_url, table_name=table_name, credential=credential, **kwargs)

    @classmethod
    def from_table_url(cls, table_url, credential=None, **kwargs):
        # type: (str, Optional[Any], Any) -> TableClient
        """A client to interact with a specific Table.

        :param table_url: The full URI to the table, including SAS token if used.
        :type table_url: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string, an account
            shared access key.
        :type credential: str
        :returns: A table client.
        :rtype: ~azure.data.tables.TableClient
        """
        try:
            if not table_url.lower().startswith("http"):
                table_url = "https://" + table_url
        except AttributeError:
            raise ValueError("Table URL must be a string.")
        parsed_url = urlparse(table_url.rstrip("/"))

        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(table_url))

        table_path = parsed_url.path.lstrip("/").split("/")
        account_path = ""
        if len(table_path) > 1:
            account_path = "/" + "/".join(table_path[:-1])
        account_url = "{}://{}{}?{}".format(
            parsed_url.scheme,
            parsed_url.netloc.rstrip("/"),
            account_path,
            parsed_url.query,
        )
        table_name = unquote(table_path[-1])
        if not table_name:
            raise ValueError(
                "Invalid URL. Please provide a URL with a valid table name"
            )
        return cls(account_url, table_name=table_name, credential=credential, **kwargs)

    @distributed_trace_async
    async def get_table_access_policy(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> dict[str,AccessPolicy]
        """
        Retrieves details about any stored access policies specified on the table that may be
        used with Shared Access Signatures.

        :return: Dictionary of SignedIdentifiers
        :rtype: dict[str,~azure.data.tables.AccessPolicy]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        timeout = kwargs.pop("timeout", None)
        try:
            _, identifiers = await self._client.table.get_access_policy(
                table=self.table_name,
                timeout=timeout,
                cls=kwargs.pop("cls", None) or _return_headers_and_deserialized,
                **kwargs
            )
        except HttpResponseError as error:
            _process_table_error(error)
        return {
            s.id: s.access_policy
            or AccessPolicy(start=None, expiry=None, permission=None)
            for s in identifiers
        }

    @distributed_trace_async
    async def set_table_access_policy(
        self,
        signed_identifiers,  # type: dict[str,AccessPolicy]
        **kwargs
    ):
        # type: (...) -> None
        """Sets stored access policies for the table that may be used with Shared Access Signatures.

        :param signed_identifiers:
        :type signed_identifiers: dict[str,AccessPolicy]
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
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
                table=self.table_name, table_acl=signed_identifiers or None, **kwargs
            )
        except HttpResponseError as error:
            _process_table_error(error)

    @distributed_trace_async
    async def create_table(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str,str]
        """Creates a new table under the given account.

        :return: Dictionary of operation metadata returned from service
        :rtype: dict[str,str]
        :raises ~azure.core.exceptions.ResourceExistsError: If the table already exists

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_delete_table_async.py
                :start-after: [START create_table]
                :end-before: [END create_table]
                :language: python
                :dedent: 8
                :caption: Creating a table from the TableClient object.
        """
        table_properties = TableProperties(table_name=self.table_name, **kwargs)
        try:
            metadata, _ = await self._client.table.create(
                table_properties,
                cls=kwargs.pop("cls", _return_headers_and_deserialized),
            )
            return _trim_service_metadata(metadata)
        except HttpResponseError as error:
            _process_table_error(error)

    @distributed_trace_async
    async def delete_table(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Deletes the table under the current account.

        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.ResourceNotFoundError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_create_delete_table_async.py
                :start-after: [START delete_from_table_client]
                :end-before: [END delete_from_table_client]
                :language: python
                :dedent: 8
                :caption: Deleting a table from the TableClient object.
        """
        try:
            await self._client.table.delete(table=self.table_name, **kwargs)
        except HttpResponseError as error:
            _process_table_error(error)

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
        :keyword ~azure.core.MatchConditions match_condition: MatchCondition
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.ResourceNotFoundError: If the table does not exist

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_insert_delete_entities_async.py
                :start-after: [START delete_entity]
                :end-before: [END delete_entity]
                :language: python
                :dedent: 8
                :caption: Adding an entity to a Table
        """
        if_match, _ = _get_match_headers(
            kwargs=dict(
                kwargs,
                etag=kwargs.pop("etag", None),
                match_condition=kwargs.pop("match_condition", None),
            ),
            etag_param="etag",
            match_param="match_condition",
        )
        try:
            await self._client.table.delete_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                if_match=if_match or "*",
                **kwargs
            )
        except HttpResponseError as error:
            _process_table_error(error)

    @distributed_trace_async
    async def create_entity(
        self,
        entity,  # type: Union[TableEntity, Dict[str,str]]
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str,str]
        """Insert entity in a table.

        :param entity: The properties for the table entity.
        :type entity: TableEntity or dict[str,str]
        :return: Dictionary mapping operation metadata returned from the service
        :rtype: dict[str,str]
        :raises ~azure.core.exceptions.ResourceExistsError: If the entity already exists

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_insert_delete_entities_async.py
                :start-after: [START create_entity]
                :end-before: [END create_entity]
                :language: python
                :dedent: 8
                :caption: Adding an entity to a Table
        """
        if "PartitionKey" in entity and "RowKey" in entity:
            entity = _add_entity_properties(entity)
        else:
            raise ValueError("PartitionKey and RowKey were not provided in entity")
        try:
            metadata, _ = await self._client.table.insert_entity(
                table=self.table_name,
                table_entity_properties=entity,
                cls=kwargs.pop("cls", _return_headers_and_deserialized),
                **kwargs
            )
            return _trim_service_metadata(metadata)
        except ResourceNotFoundError as error:
            _process_table_error(error)

    @distributed_trace_async
    async def update_entity(
        self,
        entity,  # type: Union[TableEntity, Dict[str,str]]
        mode=UpdateMode.MERGE,  # type: UpdateMode
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str,str]
        """Update entity in a table.

        :param entity: The properties for the table entity.
        :type entity: dict[str, str]
        :param mode: Merge or Replace entity
        :type mode: ~azure.data.tables.UpdateMode
        :keyword str partition_key: The partition key of the entity.
        :keyword str row_key: The row key of the entity.
        :keyword str etag: Etag of the entity
        :keyword ~azure.core.MatchConditions match_condition: MatchCondition
        :return: Dictionary of operation metadata returned from service
        :rtype: dict[str,str]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_update_upsert_merge_entities_async.py
                :start-after: [START update_entity]
                :end-before: [END update_entity]
                :language: python
                :dedent: 8
                :caption: Querying entities from a TableClient
        """
        if_match, _ = _get_match_headers(
            kwargs=dict(
                kwargs,
                etag=kwargs.pop("etag", None),
                match_condition=kwargs.pop("match_condition", None),
            ),
            etag_param="etag",
            match_param="match_condition",
        )

        partition_key = entity["PartitionKey"]
        row_key = entity["RowKey"]
        entity = _add_entity_properties(entity)
        try:
            metadata = None
            if mode is UpdateMode.REPLACE:
                metadata, _ = await self._client.table.update_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=entity,
                    if_match=if_match or "*",
                    cls=kwargs.pop("cls", _return_headers_and_deserialized),
                    **kwargs
                )
            elif mode is UpdateMode.MERGE:
                metadata, _ = await self._client.table.merge_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    if_match=if_match or "*",
                    cls=kwargs.pop("cls", _return_headers_and_deserialized),
                    table_entity_properties=entity,
                    **kwargs
                )
            else:
                raise ValueError("Mode type is not supported")
            return _trim_service_metadata(metadata)
        except HttpResponseError as error:
            _process_table_error(error)

    @distributed_trace
    def list_entities(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[TableEntity]
        """Lists entities in a table.

        :keyword int results_per_page: Number of entities per page in return AsyncItemPaged
        :keyword select: Specify desired properties of an entity to return certain entities
        :paramtype select: str or list[str]
        :return: Query of table entities
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.data.tables.TableEntity]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_update_upsert_merge_entities_async.py
                :start-after: [START list_entities]
                :end-before: [END list_entities]
                :language: python
                :dedent: 8
                :caption: Querying entities from a TableClient
        """
        user_select = kwargs.pop("select", None)
        if user_select and not isinstance(user_select, str):
            user_select = ", ".join(user_select)
        top = kwargs.pop("results_per_page", None)

        command = functools.partial(self._client.table.query_entities, **kwargs)
        return AsyncItemPaged(
            command,
            table=self.table_name,
            results_per_page=top,
            select=user_select,
            page_iterator_class=TableEntityPropertiesPaged,
        )

    @distributed_trace
    def query_entities(
        self,
        filter,  # type: str  # pylint: disable=redefined-builtin
        **kwargs
    ):
        # type: (...) -> AsyncItemPaged[TableEntity]
        """Lists entities in a table.

        :param str filter: Specify a filter to return certain entities
        :keyword int results_per_page: Number of entities per page in return AsyncItemPaged
        :keyword select: Specify desired properties of an entity to return certain entities
        :paramtype select: str or list[str]
        :keyword dict parameters: Dictionary for formatting query with additional, user defined parameters
        :return: Query of table entities
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.data.tables.TableEntity]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_query_table_async.py
                :start-after: [START query_entities]
                :end-before: [END query_entities]
                :language: python
                :dedent: 8
                :caption: Querying entities from a TableClient
        """
        parameters = kwargs.pop("parameters", None)
        filter = self._parameter_filter_substitution(
            parameters, filter
        )  # pylint: disable = redefined-builtin
        top = kwargs.pop("results_per_page", None)
        user_select = kwargs.pop("select", None)
        if user_select and not isinstance(user_select, str):
            user_select = ", ".join(user_select)

        command = functools.partial(self._client.table.query_entities, **kwargs)
        return AsyncItemPaged(
            command,
            table=self.table_name,
            results_per_page=top,
            filter=filter,
            select=user_select,
            page_iterator_class=TableEntityPropertiesPaged,
        )

    @distributed_trace_async
    async def get_entity(
        self,
        partition_key,  # type: str
        row_key,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> TableEntity
        """Get a single entity in a table.

        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :return: Dictionary mapping operation metadata returned from the service
        :rtype: ~azure.data.tables.TableEntity
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_update_upsert_merge_entities_async.py
                :start-after: [START get_entity]
                :end-before: [END get_entity]
                :language: python
                :dedent: 8
                :caption: Getting an entity from PartitionKey and RowKey
        """
        try:
            entity = await self._client.table.query_entity_with_partition_and_row_key(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                **kwargs
            )

            properties = _convert_to_entity(entity)
            return properties
        except HttpResponseError as error:
            _process_table_error(error)

    @distributed_trace_async
    async def upsert_entity(
        self,
        entity,  # type: Union[TableEntity, Dict[str,str]]
        mode=UpdateMode.MERGE,  # type: UpdateMode
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str,str]
        """Update/Merge or Insert entity into table.

        :param entity: The properties for the table entity.
        :type entity: TableEntity or dict[str,str]
        :param mode: Merge or Replace and Insert on fail
        :type mode: ~azure.data.tables.UpdateMode
        :return: Dictionary mapping operation metadata returned from the service
        :rtype: dict[str,str]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_update_upsert_merge_entities_async.py
                :start-after: [START upsert_entity]
                :end-before: [END upsert_entity]
                :language: python
                :dedent: 8
                :caption: Update/Merge or Insert an entity into a table
        """

        partition_key = entity["PartitionKey"]
        row_key = entity["RowKey"]
        entity = _add_entity_properties(entity)

        try:
            metadata = None
            if mode is UpdateMode.MERGE:
                metadata, _ = await self._client.table.merge_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=entity,
                    cls=kwargs.pop("cls", _return_headers_and_deserialized),
                    **kwargs
                )
            elif mode is UpdateMode.REPLACE:
                metadata, _ = await self._client.table.update_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=entity,
                    cls=kwargs.pop("cls", _return_headers_and_deserialized),
                    **kwargs
                )
            else:
                raise ValueError(
                    """Update mode {} is not supported.
                    For a list of supported modes see the UpdateMode enum""".format(
                        mode
                    )
                )
            return _trim_service_metadata(metadata)
        except HttpResponseError as error:
            _process_table_error(error)

    @distributed_trace
    def create_batch(self, **kwargs: Dict[str, Any]) -> TableBatchOperations:
        """Create a Batching object from a Table Client

        :return: Object containing requests and responses
        :rtype: ~azure.data.tables.TableBatchOperations

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_batching_async.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        return TableBatchOperations(
            self._client,
            self._client._serialize,  # pylint: disable=protected-access
            self._client._deserialize,  # pylint: disable=protected-access
            self._client._config,  # pylint: disable=protected-access
            self.table_name,
            self,
            **kwargs
        )

    @distributed_trace_async
    async def send_batch(
        self, batch: TableBatchOperations, **kwargs: Dict[Any, str]
    ) -> BatchTransactionResult:
        """Commit a TableBatchOperations to send requests to the server

        :return: Object containing requests and responses
        :rtype: ~azure.data.tables.BatchTransactionResult
        :raises ~azure.data.tables.BatchErrorException:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_batching_async.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Using batches to send multiple requests at once
        """
        return await self._batch_send(
            batch._entities, *batch._requests, **kwargs  # pylint: disable=protected-access
        )
