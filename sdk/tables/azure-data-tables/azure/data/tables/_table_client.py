# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import Optional, Any, Union, List, Tuple, Dict, Mapping, Iterable, overload
try:
    from urllib.parse import urlparse, unquote
except ImportError:
    from urlparse import urlparse  # type: ignore
    from urllib2 import unquote  # type: ignore

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

from ._deserialize import _convert_to_entity, _trim_service_metadata
from ._entity import TableEntity
from ._error import _process_table_error, _validate_table_name
from ._generated.models import (
    SignedIdentifier,
    TableProperties,
    QueryOptions
)
from ._serialize import _get_match_headers, _add_entity_properties
from ._base_client import parse_connection_str, TablesBaseClient
from ._serialize import serialize_iso, _parameter_filter_substitution
from ._deserialize import _return_headers_and_deserialized
from ._table_batch import TableBatchOperations
from ._models import (
    TableEntityPropertiesPaged,
    UpdateMode,
    AccessPolicy,
    TransactionOperation
)

EntityType = Union[TableEntity, Mapping[str, Any]]
OperationType = Union[TransactionOperation, str]
TransactionOperationType = Union[Tuple[OperationType, EntityType], Tuple[OperationType, EntityType, Mapping[str, Any]]]


class TableClient(TablesBaseClient):
    """A client to interact with a specific Table in an Azure Tables account.

    :ivar str account_name: The name of the Tables account.
    :ivar str table_name: The name of the table.
    :ivar str url: The full URL to the Tables account.
    """

    def __init__(
        self,
        endpoint,  # type: str
        table_name,  # type: str
        credential=None,  # type: Union[AzureNamedKeyCredential, AzureSasCredential]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Create TableClient from a Credential.

        :param str endpoint: A URL to an Azure Tables account.
        :param str table_name: The table name.
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string or an account shared access
            key.
        :type credential:
            :class:`~azure.core.credentials.AzureNamedKeyCredential` or
            :class:`~azure.core.credentials.AzureSasCredential`
        :returns: None
        """
        if not table_name:
            raise ValueError("Please specify a table name.")
        _validate_table_name(table_name)
        self.table_name = table_name
        super(TableClient, self).__init__(endpoint, credential=credential, **kwargs)

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}{}".format(self.scheme, hostname, self._query_str)

    @classmethod
    def from_connection_string(
        cls,
        conn_str,  # type: str
        table_name,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> TableClient
        """Create TableClient from a Connection String.

        :param str conn_str: A connection string to an Azure Tables account.
        :param str table_name: The table name.
        :returns: A table client.
        :rtype: :class:`~azure.data.tables.TableClient`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_client.py
                :start-after: [START create_table_client]
                :end-before: [END create_table_client]
                :language: python
                :dedent: 8
                :caption: Authenticating a TableServiceClient from a connection_string
        """
        endpoint, credential = parse_connection_str(
            conn_str=conn_str, credential=None, keyword_args=kwargs
        )
        return cls(endpoint, table_name=table_name, credential=credential, **kwargs)

    @classmethod
    def from_table_url(cls, table_url, credential=None, **kwargs):
        # type: (str, Optional[Any], Any) -> TableClient
        """A client to interact with a specific Table.

        :param str table_url: The full URI to the table, including SAS token if used.
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string, an account
            shared access key.
        :type credential: str
        :returns: A table client.
        :rtype: :class:`~azure.data.tables.TableClient`
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
        endpoint = "{}://{}{}?{}".format(
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
        return cls(endpoint, table_name=table_name, credential=credential, **kwargs)

    @distributed_trace
    def get_table_access_policy(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str,AccessPolicy]
        """Retrieves details about any stored access policies specified on the table that may be
        used with Shared Access Signatures.

        :return: Dictionary of SignedIdentifiers
        :rtype: Dict[str, :class:`~azure.data.tables.AccessPolicy`]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        timeout = kwargs.pop("timeout", None)
        try:
            _, identifiers = self._client.table.get_access_policy(
                table=self.table_name,
                timeout=timeout,
                cls=kwargs.pop("cls", None) or _return_headers_and_deserialized,
                **kwargs
            )
        except HttpResponseError as error:
            _process_table_error(error)
        return {s.id: s.access_policy or AccessPolicy() for s in identifiers}

    @distributed_trace
    def set_table_access_policy(
        self,
        signed_identifiers,  # type: Dict[str,AccessPolicy]
        **kwargs
    ):
        # type: (...) -> None
        """Sets stored access policies for the table that may be used with Shared Access Signatures.

        :param signed_identifiers: Access policies to set for the table
        :type signed_identifiers: Dict[str, :class:`~azure.data.tables.AccessPolicy`]
        :return: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        identifiers = []
        for key, value in signed_identifiers.items():
            if value:
                value.start = serialize_iso(value.start)
                value.expiry = serialize_iso(value.expiry)
            identifiers.append(SignedIdentifier(id=key, access_policy=value))
        signed_identifiers = identifiers  # type: ignore
        try:
            self._client.table.set_access_policy(
                table=self.table_name, table_acl=signed_identifiers or None, **kwargs
            )
        except HttpResponseError as error:
            try:
                _process_table_error(error)
            except HttpResponseError as table_error:
                if (table_error.error_code == 'InvalidXmlDocument'
                and len(signed_identifiers) > 5):
                    raise ValueError(
                        'Too many access policies provided. The server does not support setting '
                        'more than 5 access policies on a single resource.'
                    )
                raise

    @distributed_trace
    def create_table(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str,str]
        """Creates a new table under the current account.

        :return: Dictionary of operation metadata returned from service
        :rtype: Dict[str,str]
        :raises: :class:`~azure.core.exceptions.ResourceExistsError` If the entity already exists

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_delete_table.py
                :start-after: [START create_table_from_table_client]
                :end-before: [END create_table_from_table_client]
                :language: python
                :dedent: 8
                :caption: Creating a table from the TableClient object
        """
        table_properties = TableProperties(table_name=self.table_name)
        try:
            metadata, _ = self._client.table.create(
                table_properties,
                cls=kwargs.pop("cls", _return_headers_and_deserialized),
                **kwargs
            )
            return _trim_service_metadata(metadata)
        except HttpResponseError as error:
            _process_table_error(error)

    @distributed_trace
    def delete_table(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Deletes the table under the current account. No error will be raised
        if the table does not exist

        :return: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_delete_table.py
                :start-after: [START delete_table_from_table_client]
                :end-before: [END delete_table_from_table_client]
                :language: python
                :dedent: 8
                :caption: Deleting a table from the TableClient object
        """
        try:
            self._client.table.delete(table=self.table_name, **kwargs)
        except HttpResponseError as error:
            if error.status_code == 404:
                return
            _process_table_error(error)

    @overload
    def delete_entity(self, partition_key, row_key, **kwargs):
        # type: (str, str, Any) -> None
        pass

    @overload
    def delete_entity(self, entity, **kwargs):
        # type: (Union[TableEntity, Mapping[str, Any]], Any) -> None
        pass

    @distributed_trace
    def delete_entity(self, *args, **kwargs):
        # type: (Union[TableEntity, str], Any) -> None
        """Deletes the specified entity in a table. No error will be raised if
        the entity or PartitionKey-RowKey pairing is not found.

        :param str partition_key: The partition key of the entity.
        :param str row_key: The row key of the entity.
        :param entity: The entity to delete
        :type entity: Union[TableEntity, Mapping[str, str]]
        :keyword str etag: Etag of the entity
        :keyword match_condition: MatchCondition
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_insert_delete_entities.py
                :start-after: [START delete_entity]
                :end-before: [END delete_entity]
                :language: python
                :dedent: 12
                :caption: Deleting an entity of a Table
        """
        try:
            entity = kwargs.pop('entity', None)
            if not entity:
                entity = args[0]
            partition_key = entity['PartitionKey']
            row_key = entity['RowKey']
        except (TypeError, IndexError):
            partition_key = kwargs.pop('partition_key', None)
            if not partition_key:
                partition_key = args[0]
            row_key = kwargs.pop("row_key", None)
            if not row_key:
                row_key = args[1]

        match_condition = kwargs.pop("match_condition", None)
        etag = kwargs.pop("etag", None)
        if match_condition and entity and not etag:
            try:
                etag = entity.metadata.get("etag", None)
            except (AttributeError, TypeError):
                pass

        if_match, _ = _get_match_headers(
            kwargs=dict(
                kwargs,
                etag=etag,
                match_condition=match_condition,
            ),
            etag_param="etag",
            match_param="match_condition",
        )

        try:
            self._client.table.delete_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                if_match=if_match or "*",
                **kwargs
            )
        except HttpResponseError as error:
            if error.status_code == 404:
                return
            _process_table_error(error)

    @distributed_trace
    def create_entity(
        self,
        entity,  # type: EntityType
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str,str]
        """Insert entity in a table.

        :param entity: The properties for the table entity.
        :type entity: Dict[str,str] or :class:`~azure.data.tables.TableEntity`
        :return: Dictionary mapping operation metadata returned from the service
        :rtype: Dict[str,str]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_insert_delete_entities.py
                :start-after: [START create_entity]
                :end-before: [END create_entity]
                :language: python
                :dedent: 12
                :caption: Creating and adding an entity to a Table
        """
        if "PartitionKey" in entity and "RowKey" in entity:
            entity = _add_entity_properties(entity)
        else:
            raise ValueError("PartitionKey and RowKey were not provided in entity")
        try:
            metadata, _ = self._client.table.insert_entity(
                table=self.table_name,
                table_entity_properties=entity,
                cls=kwargs.pop("cls", _return_headers_and_deserialized),
                **kwargs
            )
            return _trim_service_metadata(metadata)
        except ResourceNotFoundError as error:
            _process_table_error(error)

    @distributed_trace
    def update_entity(
        self,
        entity,  # type: EntityType
        mode=UpdateMode.MERGE,  # type: UpdateMode
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str,str]
        """Update entity in a table.

        :param entity: The properties for the table entity.
        :type entity: :class:`~azure.data.tables.TableEntity` or Dict[str,str]
        :param mode: Merge or Replace entity
        :type mode: :class:`~azure.data.tables.UpdateMode`
        :keyword str etag: Etag of the entity
        :keyword match_condition: MatchCondition
        :paramtype match_condition: ~azure.core.MatchCondition
        :return: Dictionary mapping operation metadata returned from the service
        :rtype: Dict[str,str]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_update_upsert_merge_entities.py
                :start-after: [START update_entity]
                :end-before: [END update_entity]
                :language: python
                :dedent: 16
                :caption: Updating an already exiting entity in a Table
        """
        match_condition = kwargs.pop("match_condition", None)
        etag = kwargs.pop("etag", None)
        if match_condition and not etag:
            try:
                etag = entity.metadata.get("etag", None)
            except (AttributeError, TypeError):
                pass

        if_match, _ = _get_match_headers(
            kwargs=dict(
                kwargs,
                etag=etag,
                match_condition=match_condition,
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
                metadata, _ = self._client.table.update_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=entity,
                    if_match=if_match or "*",
                    cls=kwargs.pop("cls", _return_headers_and_deserialized),
                    **kwargs
                )
            elif mode is UpdateMode.MERGE:
                metadata, _ = self._client.table.merge_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    if_match=if_match or "*",
                    table_entity_properties=entity,
                    cls=kwargs.pop("cls", _return_headers_and_deserialized),
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
        # type: (...) -> ItemPaged[TableEntity]
        """Lists entities in a table.

        :keyword int results_per_page: Number of entities returned per service request.
        :keyword select: Specify desired properties of an entity to return.
        :paramtype select: str or List[str]
        :return: ItemPaged[:class:`~azure.data.tables.TableEntity`]
        :rtype: ~azure.core.paging.ItemPaged
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_update_upsert_merge_entities.py
                :start-after: [START query_entities]
                :end-before: [END query_entities]
                :language: python
                :dedent: 16
                :caption: List all entities held within a table
        """
        user_select = kwargs.pop("select", None)
        if user_select and not isinstance(user_select, str):
            user_select = ",".join(user_select)
        top = kwargs.pop("results_per_page", None)

        command = functools.partial(self._client.table.query_entities, **kwargs)
        return ItemPaged(
            command,
            table=self.table_name,
            results_per_page=top,
            select=user_select,
            page_iterator_class=TableEntityPropertiesPaged,
        )

    @distributed_trace
    def query_entities(
        self,
        query_filter,
        **kwargs
    ):
        # type: (str, Dict[str, Any]) -> ItemPaged[TableEntity]
        """Lists entities in a table.

        :param str query_filter: Specify a filter to return certain entities
        :keyword int results_per_page: Number of entities returned per service request.
        :keyword select: Specify desired properties of an entity to return.
        :paramtype select: str or List[str]
        :keyword parameters: Dictionary for formatting query with additional, user defined parameters
        :paramtype parameters: Dict[str, Any]
        :return: ItemPaged[:class:`~azure.data.tables.TableEntity`]
        :rtype: ~azure.core.paging.ItemPaged
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_query_table.py
                :start-after: [START query_entities]
                :end-before: [END query_entities]
                :language: python
                :dedent: 8
                :caption: Query entities held within a table
        """
        parameters = kwargs.pop("parameters", None)
        query_filter = _parameter_filter_substitution(
            parameters, query_filter
        )
        top = kwargs.pop("results_per_page", None)
        user_select = kwargs.pop("select", None)
        if user_select and not isinstance(user_select, str):
            user_select = ",".join(user_select)

        command = functools.partial(self._client.table.query_entities, **kwargs)
        return ItemPaged(
            command,
            table=self.table_name,
            results_per_page=top,
            filter=query_filter,
            select=user_select,
            page_iterator_class=TableEntityPropertiesPaged,
        )

    @distributed_trace
    def get_entity(
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
        :keyword select: Specify desired properties of an entity to return.
        :paramtype select: str or List[str]
        :return: Dictionary mapping operation metadata returned from the service
        :rtype: :class:`~azure.data.tables.TableEntity`
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_update_upsert_merge_entities.py
                :start-after: [START get_entity]
                :end-before: [END get_entity]
                :language: python
                :dedent: 16
                :caption: Get a single entity from a table
        """
        user_select = kwargs.pop("select", None)
        if user_select and not isinstance(user_select, str):
            user_select = ",".join(user_select)
        try:
            entity = self._client.table.query_entity_with_partition_and_row_key(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                query_options=QueryOptions(select=user_select),
                **kwargs
            )
            properties = _convert_to_entity(entity)
            return properties
        except HttpResponseError as error:
            _process_table_error(error)

    @distributed_trace
    def upsert_entity(
        self,
        entity,  # type: EntityType
        mode=UpdateMode.MERGE,  # type: UpdateMode
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str,str]
        """Update/Merge or Insert entity into table.

        :param entity: The properties for the table entity.
        :type entity: :class:`~azure.data.tables.TableEntity` or Dict[str,str]
        :param mode: Merge or Replace entity
        :type mode: :class:`~azure.data.tables.UpdateMode`
        :return: Dictionary mapping operation metadata returned from the service
        :rtype: Dict[str,str]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_update_upsert_merge_entities.py
                :start-after: [START upsert_entity]
                :end-before: [END upsert_entity]
                :language: python
                :dedent: 16
                :caption: Update/merge or insert an entity into a table
        """

        partition_key = entity["PartitionKey"]
        row_key = entity["RowKey"]
        entity = _add_entity_properties(entity)
        try:
            metadata = None
            if mode is UpdateMode.MERGE:
                metadata, _ = self._client.table.merge_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=entity,
                    cls=kwargs.pop("cls", _return_headers_and_deserialized),
                    **kwargs
                )
            elif mode is UpdateMode.REPLACE:
                metadata, _ = self._client.table.update_entity(
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

    def submit_transaction(
        self,
        operations,  # type: Iterable[TransactionOperationType]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Mapping[str, Any]]
        """Commit a list of operations as a single transaction.

        If any one of these operations fails, the entire transaction will be rejected.

        :param operations: The list of operations to commit in a transaction. This should be a list of
         tuples containing an operation name, the entity on which to operate, and optionally, a dict of additional
         kwargs for that operation.
        :type operations: Iterable[Tuple[str, EntityType]]
        :return: A list of mappings with response metadata for each operation in the transaction.
        :rtype: List[Mapping[str, Any]]
        :raises: :class:`~azure.data.tables.TableTransactionError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_batching.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Using transactions to send multiple requests at once
        """
        batched_requests = TableBatchOperations(
            self._client,
            self._client._serialize,  # pylint: disable=protected-access
            self._client._deserialize,  # pylint: disable=protected-access
            self._client._config,  # pylint: disable=protected-access
            self.table_name,
            **kwargs
        )
        for operation in operations:
            try:
                operation_kwargs = operation[2]
            except IndexError:
                operation_kwargs = {}
            try:
                getattr(batched_requests, operation[0].lower())(operation[1], **operation_kwargs)
            except AttributeError:
                raise ValueError("Unrecognized operation: {}".format(operation[0]))
        return self._batch_send(*batched_requests.requests, **kwargs)
