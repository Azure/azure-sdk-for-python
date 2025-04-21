# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import Optional, Any, Union, List, Dict, Mapping, Iterable, overload, cast, Tuple
from urllib.parse import urlparse, unquote

from azure.core import MatchConditions
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

from ._common_conversion import _prepare_key, _return_headers_and_deserialized, _trim_service_metadata
from ._encoder import TableEntityEncoder, EncoderMapType
from ._decoder import TableEntityDecoder, deserialize_iso, DecoderMapType
from ._base_client import parse_connection_str, TablesBaseClient, AudienceType
from ._entity import TableEntity
from ._error import (
    _decode_error,
    _process_table_error,
    _reprocess_error,
    _validate_tablename_error,
    _validate_key_values,
)
from ._generated.models import SignedIdentifier, TableProperties
from ._serialize import (
    serialize_iso,
    _parameter_filter_substitution,
    _get_match_condition,
)
from ._table_batch import (
    TableBatchOperations,
    EntityType,
    TransactionOperationType,
)
from ._models import TableEntityPropertiesPaged, UpdateMode, TableAccessPolicy, TableItem


class TableClient(TablesBaseClient):
    """A client to interact with a specific Table in an Azure Tables account.

    :ivar str account_name: The name of the Tables account.
    :ivar str table_name: The name of the table.
    :ivar str scheme: The scheme component in the full URL to the Tables account.
    :ivar str url: The full endpoint URL to this entity, including SAS token if used.
    :ivar str api_version: The version of the Storage API used for requests.
    :ivar credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be one of AzureNamedKeyCredential (azure-core),
        AzureSasCredential (azure-core), or a TokenCredential implementation from azure-identity.
    :vartype credential:
        ~azure.core.credentials.AzureNamedKeyCredential or
        ~azure.core.credentials.AzureSasCredential or
        ~azure.core.credentials.TokenCredential or None
    :ivar encoder_map: A dictionary maps the type and the convertion function of this type used in encoding.
    :vartype encoder_map:
        dict[Union[Type, EdmType], Callable[[Any], Tuple[Optional[EdmType], Union[str, bool, int]]]] or None
    :ivar decoder_map: A dictionary maps the type and the convertion function of this type used in decoding.
    :vartype decoder_map:
        dict[EdmType, Callable[[Any], Tuple[Optional[EdmType], Union[str, bool, int]]]] or None
    :ivar flatten_result_entity: Whether to flatten entity metadata in deserialization. Default is False,
        which means the metadata would be deserialized to property metadata in TableEntity.
    :vartype flatten_result_entity: bool
    """

    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential
        self,
        endpoint: str,
        table_name: str,
        *,
        credential: Optional[Union[AzureSasCredential, AzureNamedKeyCredential, TokenCredential]] = None,
        audience: Optional[AudienceType] = None,
        api_version: Optional[str] = None,
        encoder_map: Optional[EncoderMapType] = None,
        decoder_map: Optional[DecoderMapType] = None,
        flatten_result_entity: bool = False,
        **kwargs: Any,
    ) -> None:
        """Create TableClient from a Credential.

        :param str endpoint: A URL to an Azure Tables account.
        :param str table_name: The table name.
        :keyword credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be one of AzureNamedKeyCredential (azure-core),
            AzureSasCredential (azure-core), or a TokenCredential implementation from azure-identity.
        :paramtype credential:
            ~azure.core.credentials.AzureNamedKeyCredential or
            ~azure.core.credentials.AzureSasCredential or
            ~azure.core.credentials.TokenCredential or None
        :keyword audience: Optional audience to use for Microsoft Entra ID authentication. If not specified,
            the public cloud audience will be used.
        :paramtype audience: str or None
        :keyword api_version: Specifies the version of the operation to use for this request. Default value
            is "2019-02-02".
        :paramtype api_version: str or None
        :keyword encoder_map:
            A dictionary maps the type and the convertion function of this type used in encoding.
        :paramtype encoder_map:
            dict[Union[Type, EdmType], Callable[[Any], Tuple[Optional[EdmType], Union[str, bool, int]]]] or None
        :keyword decoder_map:
            A dictionary maps the type and the convertion function of this type used in decoding.
        :paramtype decoder_map:
            dict[EdmType, Callable[[Any], Tuple[Optional[EdmType], Union[str, bool, int]]]] or None
        :paramtype bool flatten_result_entity:
            Whether to flatten entity metadata in deserialization. Default is False,
            which means the metadata would be deserialized to property metadata in TableEntity.
        :returns: None
        """
        if not table_name:
            raise ValueError("Please specify a table name.")
        self.table_name: str = table_name
        self.encoder = TableEntityEncoder(convert_map=encoder_map)
        self.decoder = TableEntityDecoder(convert_map=decoder_map, flatten_result_entity=flatten_result_entity)
        super(TableClient, self).__init__(
            endpoint, credential=credential, api_version=api_version, audience=audience, **kwargs
        )

    @classmethod
    def from_connection_string(cls, conn_str: str, table_name: str, **kwargs: Any) -> "TableClient":
        """Creates TableClient from a Connection String.

        :param str conn_str: A connection string to an Azure Tables account.
        :param str table_name: The table name.
        :returns: A table client.
        :rtype: ~azure.data.tables.TableClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_client.py
                :start-after: [START create_table_client]
                :end-before: [END create_table_client]
                :language: python
                :dedent: 8
                :caption: Authenticating a TableServiceClient from a connection_string
        """
        endpoint, credential = parse_connection_str(conn_str=conn_str, credential=None, keyword_args=kwargs)
        return cls(endpoint, table_name=table_name, credential=credential, **kwargs)

    @classmethod
    def from_table_url(
        cls,
        table_url: str,
        *,
        credential: Optional[Union[AzureNamedKeyCredential, AzureSasCredential]] = None,
        **kwargs: Any,
    ) -> "TableClient":
        """A client to interact with a specific Table.

        :param str table_url: The full URI to the table, including SAS token if used.
        :keyword credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be one of AzureNamedKeyCredential (azure-core),
            AzureSasCredential (azure-core), or a TokenCredential implementation from azure-identity.
        :paramtype credential:
            ~azure.core.credentials.AzureNamedKeyCredential or
            ~azure.core.credentials.AzureSasCredential or None
        :returns: A table client.
        :rtype: ~azure.data.tables.TableClient
        """
        try:
            if not table_url.lower().startswith("http"):
                table_url = "https://" + table_url
        except AttributeError as exc:
            raise ValueError("Table URL must be a string.") from exc
        parsed_url = urlparse(table_url.rstrip("/"))

        if not parsed_url.netloc:
            raise ValueError(f"Invalid URL: {table_url}")

        table_path = parsed_url.path.lstrip("/").split("/")
        account_path = ""
        if len(table_path) > 1:
            account_path = "/" + "/".join(table_path[:-1])
        endpoint = f"{parsed_url.scheme}://{parsed_url.netloc.rstrip('/')}{account_path}?{parsed_url.query}"
        table_name = unquote(table_path[-1])
        if table_name.lower().startswith("tables('"):
            table_name = table_name[8:-2]
        if not table_name:
            raise ValueError("Invalid URL. Please provide a URL with a valid table name")
        return cls(endpoint, table_name=table_name, credential=credential, **kwargs)

    @distributed_trace
    def get_table_access_policy(self, **kwargs) -> Dict[str, Optional[TableAccessPolicy]]:
        """Retrieves details about any stored access policies specified on the table that may be
        used with Shared Access Signatures.

        :return: Dictionary of SignedIdentifiers.
        :rtype: dict[str, ~azure.data.tables.TableAccessPolicy] or dict[str, None]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        timeout = kwargs.pop("timeout", None)
        try:
            identifiers = self._client.table.get_access_policy(
                table=self.table_name,
                timeout=timeout,
                **kwargs,
            )
        except HttpResponseError as error:
            _process_table_error(error, table_name=self.table_name)
        output: Dict[str, Optional[TableAccessPolicy]] = {}
        for identifier in cast(List[SignedIdentifier], identifiers):
            if identifier.access_policy:
                output[identifier.id] = TableAccessPolicy(
                    start=deserialize_iso(identifier.access_policy.start),
                    expiry=deserialize_iso(identifier.access_policy.expiry),
                    permission=identifier.access_policy.permission,
                )
            else:
                output[identifier.id] = None
        return output

    @distributed_trace
    def set_table_access_policy(self, signed_identifiers: Mapping[str, Optional[TableAccessPolicy]], **kwargs) -> None:
        """Sets stored access policies for the table that may be used with Shared Access Signatures.

        :param signed_identifiers: Access policies to set for the table.
        :type signed_identifiers: Mapping[str, Optional[~azure.data.tables.TableAccessPolicy]]
        :return: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        identifiers = []
        for key, value in signed_identifiers.items():
            payload = None
            if value:
                payload = TableAccessPolicy(
                    start=serialize_iso(value.start),
                    expiry=serialize_iso(value.expiry),
                    permission=value.permission,
                )
            identifiers.append(SignedIdentifier(id=key, access_policy=payload))
        try:
            self._client.table.set_access_policy(table=self.table_name, table_acl=identifiers or None, **kwargs)
        except HttpResponseError as error:
            try:
                _process_table_error(error, table_name=self.table_name)
            except HttpResponseError as table_error:
                _reprocess_error(table_error, identifiers=identifiers)
                raise

    @distributed_trace
    def create_table(self, **kwargs) -> TableItem:
        """Creates a new table under the current account.

        :return: A TableItem representing the created table.
        :rtype: ~azure.data.tables.TableItem
        :raises: :class:`~azure.core.exceptions.ResourceExistsError` If the entity already exists

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_delete_table.py
                :start-after: [START create_table_from_table_client]
                :end-before: [END create_table_from_table_client]
                :language: python
                :dedent: 8
                :caption: Creating a table from the TableClient object.
        """
        table_properties = TableProperties(table_name=self.table_name)
        try:
            self._client.table.create(table_properties, **kwargs)
        except HttpResponseError as error:
            try:
                _process_table_error(error, table_name=self.table_name)
            except HttpResponseError as decoded_error:
                _reprocess_error(decoded_error)
                raise
        return TableItem(name=self.table_name)

    @distributed_trace
    def delete_table(self, **kwargs) -> None:
        """Deletes the table under the current account. No error will be raised if the table does not exist.

        :return: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_delete_table.py
                :start-after: [START delete_table_from_table_client]
                :end-before: [END delete_table_from_table_client]
                :language: python
                :dedent: 8
                :caption: Deleting a table from the TableClient object.
        """
        try:
            self._client.table.delete(table=self.table_name, **kwargs)
        except HttpResponseError as error:
            if error.status_code == 404:
                return
            try:
                _process_table_error(error, table_name=self.table_name)
            except HttpResponseError as decoded_error:
                _reprocess_error(decoded_error)
                raise

    @overload
    def delete_entity(
        self,
        partition_key: str,
        row_key: str,
        *,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any,
    ) -> None:
        """Deletes the specified entity in a table. No error will be raised if
        the entity or PartitionKey-RowKey pairing is not found.

        :param str partition_key: The partition key of the entity.
        :param str row_key: The row key of the entity.
        :keyword etag: Etag of the entity.
        :paramtype etag: str or None
        :keyword match_condition: The condition under which to perform the operation.
            Supported values include: MatchConditions.IfNotModified, MatchConditions.Unconditionally.
        :paramtype match_condition: ~azure.core.MatchConditions or None
        :return: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_insert_delete_entities.py
                :start-after: [START delete_entity]
                :end-before: [END delete_entity]
                :language: python
                :dedent: 12
                :caption: Deleting an entity of a Table
        """

    @overload
    def delete_entity(
        self,
        entity: EntityType,
        *,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any,
    ) -> None:
        """Deletes the specified entity in a table. No error will be raised if
        the entity or PartitionKey-RowKey pairing is not found.

        :param entity: The entity to delete.
        :type entity: Union[TableEntity, Mapping[str, Any]]
        :keyword etag: Etag of the entity.
        :paramtype etag: str or None
        :keyword match_condition: The condition under which to perform the operation.
            Supported values include: MatchConditions.IfNotModified, MatchConditions.Unconditionally.
        :paramtype match_condition: ~azure.core.MatchConditions or None
        :return: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_insert_delete_entities.py
                :start-after: [START delete_entity]
                :end-before: [END delete_entity]
                :language: python
                :dedent: 12
                :caption: Deleting an entity of a Table
        """

    @distributed_trace
    def delete_entity(self, *args: Union[EntityType, str], **kwargs: Any) -> None:
        entity = kwargs.pop("entity", None)
        try:
            if not entity:
                entity = args[0]
            entity_json = self.encoder(entity)
            partition_key = entity_json.get("PartitionKey")
            row_key = entity_json.get("RowKey")
        except (TypeError, IndexError, AttributeError):
            partition_key = kwargs.pop("partition_key", None)
            if partition_key is None:
                partition_key = cast(str, args[0])
            row_key = kwargs.pop("row_key", None)
            if row_key is None:
                row_key = cast(str, args[1])

        match_condition = kwargs.pop("match_condition", None)
        etag = kwargs.pop("etag", None)
        if match_condition and not etag and isinstance(entity, TableEntity):
            etag = entity.metadata.get("etag")
        match_condition = _get_match_condition(
            etag=etag,
            match_condition=match_condition or MatchConditions.Unconditionally,
        )

        try:
            self._client.table.delete_entity(
                table=self.table_name,
                partition_key=_prepare_key(partition_key),
                row_key=_prepare_key(row_key),
                etag=etag or "*",
                match_condition=match_condition,
                **kwargs,
            )
        except HttpResponseError as error:
            if error.status_code == 404:
                return
            _process_table_error(error, table_name=self.table_name)

    @distributed_trace
    def create_entity(self, entity: EntityType, **kwargs: Any) -> Dict[str, Any]:
        """Inserts an entity in a table.

        :param entity: The properties for the table entity.
        :type entity: Union[TableEntity, Mapping[str, Any]]
        :return: Dictionary mapping operation metadata returned from the service.
        :rtype: dict[str, Any]
        :raises: :class:`~azure.core.exceptions.ResourceExistsError` If the entity already exists

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_insert_delete_entities.py
                :start-after: [START create_entity]
                :end-before: [END create_entity]
                :language: python
                :dedent: 12
                :caption: Creating and adding an entity to a Table
        """
        entity_json = self.encoder(entity)
        try:
            metadata, content = cast(
                Tuple[Dict[str, str], Optional[Dict[str, Any]]],
                self._client.table.insert_entity(
                    table=self.table_name,
                    table_entity_properties=entity_json,
                    cls=kwargs.pop("cls", _return_headers_and_deserialized),
                    **kwargs,
                ),
            )
        except HttpResponseError as error:
            decoded = _decode_error(error.response, error.message)
            _validate_key_values(decoded, entity_json.get("PartitionKey"), entity_json.get("RowKey"))
            _validate_tablename_error(decoded, self.table_name)
            # We probably should have been raising decoded error before removing _reraise_error()
            raise error
        return _trim_service_metadata(metadata, content=content)

    @distributed_trace
    def update_entity(
        self,
        entity: EntityType,
        mode: Union[str, UpdateMode] = UpdateMode.MERGE,
        *,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Updates an already existing entity in a table.

        :param entity: The properties for the table entity.
        :type entity: Custom entity type
        :param mode: Merge or Replace entity.
        :type mode: ~azure.data.tables.UpdateMode or str
        :keyword etag: Etag of the entity.
        :paramtype etag: str or None
        :keyword match_condition: The condition under which to perform the operation.
            Supported values include: MatchConditions.IfNotModified, MatchConditions.Unconditionally.
        :paramtype match_condition: ~azure.core.MatchConditions or None
        :return: Dictionary mapping operation metadata returned from the service.
        :rtype: dict[str, Any]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        if match_condition and not etag and isinstance(entity, TableEntity):
            etag = entity.metadata.get("etag")
        match_condition = _get_match_condition(
            etag=etag, match_condition=match_condition or MatchConditions.Unconditionally
        )
        entity_json = self.encoder(entity)
        partition_key = entity_json.get("PartitionKey")
        row_key = entity_json.get("RowKey")

        try:
            if mode == UpdateMode.REPLACE:
                metadata, content = cast(
                    Tuple[Dict[str, str], Optional[Dict[str, Any]]],
                    self._client.table.update_entity(
                        table=self.table_name,
                        partition_key=_prepare_key(partition_key),
                        row_key=_prepare_key(row_key),
                        table_entity_properties=entity_json,
                        etag=etag,
                        match_condition=match_condition,
                        cls=kwargs.pop("cls", _return_headers_and_deserialized),
                        **kwargs,
                    ),
                )
            elif mode == UpdateMode.MERGE:
                metadata, content = cast(
                    Tuple[Dict[str, str], Optional[Dict[str, Any]]],
                    self._client.table.merge_entity(
                        table=self.table_name,
                        partition_key=_prepare_key(partition_key),
                        row_key=_prepare_key(row_key),
                        etag=etag,
                        match_condition=match_condition,
                        table_entity_properties=entity_json,
                        cls=kwargs.pop("cls", _return_headers_and_deserialized),
                        **kwargs,
                    ),
                )
            else:
                raise ValueError(f"Mode type '{mode}' is not supported.")
        except HttpResponseError as error:
            _process_table_error(error, table_name=self.table_name)
        return _trim_service_metadata(metadata, content=content)

    @distributed_trace
    def list_entities(
        self,
        *,
        results_per_page: Optional[int] = None,
        select: Optional[Union[str, List[str]]] = None,
        **kwargs,
    ) -> ItemPaged[TableEntity]:
        """Lists entities in a table.

        :keyword results_per_page: Number of entities returned per service request.
        :paramtype results_per_page: int or None
        :keyword select: Specify desired properties of an entity to return.
        :paramtype select: str or list[str] or None
        :return: Queried entities.
        :rtype: An iterator of custom entity type.
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        if select and not isinstance(select, str):
            select = ",".join(select)

        command = functools.partial(self._client.table.query_entities, **kwargs)
        return ItemPaged(
            command,
            table=self.table_name,
            results_per_page=results_per_page,
            select=select,
            decoder=self.decoder,
            page_iterator_class=TableEntityPropertiesPaged,
        )

    @distributed_trace
    def query_entities(
        self,
        query_filter: str,
        *,
        results_per_page: Optional[int] = None,
        select: Optional[Union[str, List[str]]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> ItemPaged[TableEntity]:
        # pylint: disable=line-too-long
        """Queries entities in a table.

        :param str query_filter: Specify a filter to return certain entities. For more information
         on filter formatting, see the `samples documentation <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/tables/azure-data-tables/samples#writing-filters>`_.
        :keyword results_per_page: Number of entities returned per service request.
        :paramtype results_per_page: int or None
        :keyword select: Specify desired properties of an entity to return.
        :paramtype select: str or list[str] or None
        :keyword parameters: Dictionary for formatting query with additional, user defined parameters.
        :paramtype parameters: dict[str, Any] or None
        :return: An iterator of :class:`~azure.data.tables.TableEntity`
        :rtype: ~azure.core.paging.ItemPaged[~azure.data.tables.TableEntity]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_query_table.py
                :start-after: [START query_entities]
                :end-before: [END query_entities]
                :language: python
                :dedent: 8
                :caption: Querying entities held within a table
        """
        query_filter = _parameter_filter_substitution(parameters, query_filter)
        if select and not isinstance(select, str):
            select = ",".join(select)

        command = functools.partial(self._client.table.query_entities, **kwargs)
        return ItemPaged(
            command,
            table=self.table_name,
            results_per_page=results_per_page,
            filter=query_filter,
            select=select,
            decoder=self.decoder,
            page_iterator_class=TableEntityPropertiesPaged,
        )

    @distributed_trace
    def get_entity(
        self,
        partition_key: str,
        row_key: str,
        *,
        select: Optional[Union[str, List[str]]] = None,
        **kwargs,
    ) -> TableEntity:
        """Gets a single entity in a table.

        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :keyword select: Specify desired properties of an entity to return.
        :paramtype select: str or list[str] or None
        :return: Dictionary mapping operation metadata returned from the service.
        :rtype: ~azure.data.tables.TableEntity
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_update_upsert_merge_entities.py
                :start-after: [START get_entity]
                :end-before: [END get_entity]
                :language: python
                :dedent: 16
                :caption: Getting an entity with PartitionKey and RowKey from a table
        """
        user_select = None
        if select and not isinstance(select, str):
            user_select = ",".join(select)
        elif isinstance(select, str):
            user_select = select
        try:
            entity_json = self._client.table.query_entity_with_partition_and_row_key(
                table=self.table_name,
                partition_key=_prepare_key(partition_key),
                row_key=_prepare_key(row_key),
                select=user_select,
                **kwargs,
            )
        except HttpResponseError as error:
            _process_table_error(error, table_name=self.table_name)
        return self.decoder(entity_json)

    @distributed_trace
    def upsert_entity(
        self,
        entity: EntityType,
        mode: Union[str, UpdateMode] = UpdateMode.MERGE,
        **kwargs,
    ) -> Dict[str, Any]:
        """Updates (merge or replace) or inserts an entity into a table.

        :param entity: The properties for the table entity.
        :type entity: ~azure.data.tables.TableEntity or dict[str, Any]
        :param mode: Merge or Replace entity.
        :type mode: ~azure.data.tables.UpdateMode or str
        :return: Dictionary mapping operation metadata returned from the service.
        :rtype: dict[str, Any]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_update_upsert_merge_entities.py
                :start-after: [START upsert_entity]
                :end-before: [END upsert_entity]
                :language: python
                :dedent: 16
                :caption: Replacing/Merging or Inserting an entity into a table
        """
        entity_json = self.encoder(entity)
        partition_key = entity_json.get("PartitionKey")
        row_key = entity_json.get("RowKey")

        try:
            if mode == UpdateMode.MERGE:
                metadata, content = cast(
                    Tuple[Dict[str, str], Optional[Dict[str, Any]]],
                    self._client.table.merge_entity(
                        table=self.table_name,
                        partition_key=_prepare_key(partition_key),
                        row_key=_prepare_key(row_key),
                        table_entity_properties=entity_json,
                        cls=kwargs.pop("cls", _return_headers_and_deserialized),
                        **kwargs,
                    ),
                )
            elif mode == UpdateMode.REPLACE:
                metadata, content = cast(
                    Tuple[Dict[str, str], Optional[Dict[str, Any]]],
                    self._client.table.update_entity(
                        table=self.table_name,
                        partition_key=_prepare_key(partition_key),
                        row_key=_prepare_key(row_key),
                        table_entity_properties=entity_json,
                        cls=kwargs.pop("cls", _return_headers_and_deserialized),
                        **kwargs,
                    ),
                )
            else:
                raise ValueError(
                    f"Update mode {mode} is not supported. For a list of supported modes see the UpdateMode enum."
                )
        except HttpResponseError as error:
            _process_table_error(error, table_name=self.table_name)
        return _trim_service_metadata(metadata, content=content)

    @distributed_trace
    def submit_transaction(
        self,
        operations: Iterable[TransactionOperationType],
        **kwargs,
    ) -> List[Mapping[str, Any]]:
        """Commits a list of operations as a single transaction.

        If any one of these operations fails, the entire transaction will be rejected.

        :param operations: The list of operations to commit in a transaction. This should be an iterable of
         tuples containing an operation name, the entity on which to operate, and optionally, a dict of additional
         kwargs for that operation. For example::

            - ('upsert', {'PartitionKey': 'A', 'RowKey': 'B'})
            - ('upsert', {'PartitionKey': 'A', 'RowKey': 'B'}, {'mode': UpdateMode.REPLACE})

        :type operations: Iterable[Tuple[str, TableEntity, Mapping[str, Any]]]
        :return: A list of mappings with response metadata for each operation in the transaction.
        :rtype: list[Mapping[str, Any]]
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
            config=self._client._config,  # pylint: disable=protected-access
            endpoint=f"{self.scheme}://{self._primary_hostname}",
            table_name=self.table_name,
            is_cosmos_endpoint=self._cosmos_endpoint,
            encoder=self.encoder,
        )
        try:
            for operation in operations:
                batched_requests.add_operation(operation)
        except TypeError as exc:
            raise TypeError(
                "The value of 'operations' must be an iterator "
                "of Tuples. Please check documentation for correct Tuple format."
            ) from exc

        try:
            return self._batch_send(self.table_name, *batched_requests.requests, **kwargs)
        except HttpResponseError as ex:
            if ex.status_code == 400 and not batched_requests.requests:
                return []
            raise
