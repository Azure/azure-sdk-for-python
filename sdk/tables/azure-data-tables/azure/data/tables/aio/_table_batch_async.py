# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Dict, Any, Optional, Union

from azure.core import MatchConditions

from .._common_conversion import _transform_patch_to_cosmos_post
from .._models import UpdateMode
from .._table_batch import EntityType, TransactionOperationType
from .._serialize import (
    _prepare_key,
    _add_entity_properties,
    _get_match_condition,
)
from .._generated import models
from .._generated.aio import AzureTable
from .._generated.aio._configuration import AzureTableConfiguration
from .._generated._serialization import Serializer, Deserializer
from .._generated._vendor import prep_if_match


class TableBatchOperations(object):
    """
    This is the class that is used for batch operations for the data tables
    service.

    The Tables service supports batch transactions on entities that are in the
    same table and belong to the same partition group. Multiple operations are
    supported within a single transaction. The batch can include at most 100
    entities, and its total payload may be no more than 4 MB in size.

    :ivar str table_name: The name of the table.
    :ivar requests: A list of :class:`~azure.core.pipeline.transport.HttpRequest` in a batch.
    :vartype requests: list[~azure.core.pipeline.transport.HttpRequest]
    """

    def __init__(
        self,
        client: AzureTable,
        serializer: Serializer,
        deserializer: Deserializer,
        config: AzureTableConfiguration,
        table_name: str,
        is_cosmos_endpoint: bool = False,
        **kwargs,
    ) -> None:
        """Create TableClient from a Credential.

        :param client: An AzureTable object.
        :type client: ~azure.data.tables._generated.aio.AzureTable
        :param serializer: A Serializer object for request serialization.
        :type serializer: ~azure.data.tables._generated._serialization.Serializer
        :param deserializer: A Deserializer object for request deserialization.
        :type deserializer: ~azure.data.tables._generated._serialization.Deserializer
        :param config: An AzureTableConfiguration object.
        :type config: ~azure.data.tables._generated.aio._configuration.AzureTableConfiguration
        :param table_name: The name of the Table to perform operations on.
        :type table_name: str
        :param is_cosmos_endpoint: True if the client endpoint is for Tables Cosmos. False if not. Default is False.
        :type is_cosmos_endpoint: bool
        :return: None
        """
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self._config = config
        self._is_cosmos_endpoint = is_cosmos_endpoint
        self.table_name = table_name

        self._partition_key = kwargs.pop("partition_key", None)
        self.requests = []  # type: ignore

    def __len__(self):
        return len(self.requests)

    def _verify_partition_key(self, entity: EntityType) -> None:
        if self._partition_key is None:
            self._partition_key = entity["PartitionKey"]
        elif entity["PartitionKey"] != self._partition_key:
            raise ValueError("Partition Keys must all be the same")

    def add_operation(self, operation: TransactionOperationType) -> None:
        """Add a single operation to a batch.

        :param operation: An operation include operation type and entity, may with kwargs.
        :type operation: A tuple of ~azure.data.tables.TransactionOperation or str, and
            ~azure.data.tables.TableEntity or Mapping[str, Any]. Or a tuple of
            ~azure.data.tables.TransactionOperation or str, and
            ~azure.data.tables.TableEntity or Mapping[str, Any], and Mapping[str, Any]
        :return: None
        """
        try:
            operation_type, entity, kwargs = operation  # type: ignore
        except ValueError:
            operation_type, entity, kwargs = *operation, {}  # type: ignore
        try:
            getattr(self, operation_type.lower())(entity, **kwargs)
        except AttributeError as exc:
            raise ValueError(f"Unrecognized operation: {operation}") from exc

    def create(self, entity: EntityType, **kwargs) -> None:
        """Insert entity in a table.

        :param entity: The properties for the table entity.
        :type entity: ~azure.data.tables.TableEntity or dict[str, Any]
        :return: None
        :raises ValueError: If PartitionKey and/or RowKey were not provided in entity.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_batching.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        self._verify_partition_key(entity)
        temp = entity.copy()  # type: ignore

        if "PartitionKey" in temp and "RowKey" in temp:
            temp = _add_entity_properties(temp)
        else:
            raise ValueError("PartitionKey and/or RowKey were not provided in entity")
        self._batch_create_entity(table=self.table_name, entity=temp, **kwargs)

    def _batch_create_entity(
        self,
        table: str,
        entity: EntityType,
        timeout: Optional[int] = None,
        request_id_parameter: Optional[str] = None,
        response_preference: Optional[Union[str, models.ResponseFormat]] = "return-no-content",
        format: Optional[Union[str, models.OdataMetadataFormat]] = None,  # pylint: disable=redefined-builtin
        **kwargs,
    ) -> None:
        """
        Adds an insert operation to the batch. See
        :func:`azure.data.tables.TableClient.insert_entity` for more information
        on insert operations.

        The operation will not be executed until the batch is committed

        :param: table:
            The table to perform the operation on
        :type: table: str
        :param: entity:
            The entity to insert. Can be a dict or an entity object
            Must contain a PartitionKey and a RowKey.
        :type: entity: dict[str, Any] or ~azure.data.tables.models.Entity
        :param timeout: The timeout parameter is expressed in seconds.
        :type timeout: int or None
        :param request_id_parameter: Provides a client-generated, opaque value with a 1 KB character
            limit that is recorded in the analytics logs when analytics logging is enabled.
        :type request_id_parameter: str or None
        :param response_preference: Specifies the return format. Default is return without content.
        :type response_preference: str or ~azure.data.tables.models.ResponseFormat
        :param format: Specifies the media type for the response. Known values are:
            "application/json;odata=nometadata", "application/json;odata=minimalmetadata", and
            "application/json;odata=fullmetadata".
        :type format: str or ~azure.data.tables.models.OdataMetadataFormat or None
        :return: None
        """
        data_service_version = "3.0"
        content_type = kwargs.pop("content_type", "application/json;odata=nometadata")
        accept = "application/json;odata=minimalmetadata"

        # Construct URL
        url = self._batch_create_entity.metadata["url"]  # type: ignore
        path_format_arguments = {
            "url": self._serialize.url("self._config.url", self._config.url, "str", skip_quote=True),
            "table": self._serialize.url("table", table, "str"),
        }
        url = self._client._client.format_url(url, **path_format_arguments)  # pylint: disable=protected-access

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters["timeout"] = self._serialize.query("timeout", timeout, "int", minimum=0)
        if format is not None:
            query_parameters["$format"] = self._serialize.query("format", format, "str")

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters["x-ms-version"] = self._serialize.header("self._config.version", self._config.version, "str")
        if request_id_parameter is not None:
            header_parameters["x-ms-client-request-id"] = self._serialize.header(
                "request_id_parameter", request_id_parameter, "str"
            )
        header_parameters["DataServiceVersion"] = self._serialize.header(
            "data_service_version", data_service_version, "str"
        )
        if response_preference is not None:
            header_parameters["Prefer"] = self._serialize.header("response_preference", response_preference, "str")
        header_parameters["Content-Type"] = self._serialize.header("content_type", content_type, "str")
        header_parameters["Accept"] = self._serialize.header("accept", accept, "str")

        body_content_kwargs = {}  # type: Dict[str, Any]
        if entity is not None:
            body_content = self._serialize.body(entity, "{object}")
        else:
            body_content = None
        body_content_kwargs["content"] = body_content
        request = self._client._client.post(  # pylint: disable=protected-access
            url, query_parameters, header_parameters, **body_content_kwargs
        )
        self.requests.append(request)

    _batch_create_entity.metadata = {"url": "/{table}"}  # type: ignore

    def update(self, entity: EntityType, mode: Union[str, UpdateMode] = UpdateMode.MERGE, **kwargs) -> None:
        """Adds an update operation to the current batch.

        :param entity: The properties for the table entity.
        :type entity: ~azure.data.tables.TableEntity or dict[str, Any]
        :param mode: Merge or Replace entity
        :type mode: ~azure.data.tables.UpdateMode
        :keyword str etag: Etag of the entity
        :keyword match_condition: MatchCondition
        :paramtype match_condition: ~azure.core.MatchCondition
        :return: None
        :raises ValueError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_batching_async.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        self._verify_partition_key(entity)
        match_condition = kwargs.pop("match_condition", None)
        etag = kwargs.pop("etag", None)
        if match_condition and not etag:
            try:
                etag = entity.metadata.get("etag", None)  # type: ignore[union-attr]
            except (AttributeError, TypeError):
                pass
        match_condition = _get_match_condition(
            etag=etag, match_condition=match_condition or MatchConditions.Unconditionally
        )

        entity = _add_entity_properties(entity)
        partition_key = entity["PartitionKey"]
        row_key = entity["RowKey"]

        if mode == UpdateMode.REPLACE:
            self._batch_update_entity(
                table=self.table_name,
                partition_key=_prepare_key(partition_key),
                row_key=_prepare_key(row_key),
                if_match=prep_if_match(etag, match_condition),
                table_entity_properties=entity,
                **kwargs,
            )
        elif mode == UpdateMode.MERGE:
            self._batch_merge_entity(
                table=self.table_name,
                partition_key=_prepare_key(partition_key),
                row_key=_prepare_key(row_key),
                if_match=prep_if_match(etag, match_condition),
                table_entity_properties=entity,
                **kwargs,
            )
        else:
            raise ValueError(f"Mode type '{mode}' is not supported.")

    def _batch_update_entity(
        self,
        table: str,
        partition_key: str,
        row_key: str,
        timeout: Optional[int] = None,
        request_id_parameter: Optional[str] = None,
        if_match: Optional[str] = None,
        table_entity_properties: Optional[EntityType] = None,
        format: Optional[Union[str, models.OdataMetadataFormat]] = None,  # pylint: disable=redefined-builtin
        **kwargs,
    ) -> None:
        """Update entity in a table.

        :param table: The name of the table.
        :type table: str
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param timeout: The timeout parameter is expressed in seconds.
        :type timeout: int or None
        :param request_id_parameter: Provides a client-generated, opaque value with a 1 KB character
            limit that is recorded in the analytics logs when analytics logging is enabled.
        :type request_id_parameter: str or None
        :param if_match: Match condition for an entity to be updated. If specified and a matching
            entity is not found, an error will be raised. To force an unconditional update, set to the
            wildcard character (*). If not specified, an insert will be performed when no existing entity
            is found to update and a replace will be performed if an existing entity is found.
        :type if_match: str or None
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, object] or None
        :param format: Specifies the media type for the response. Known values are:
            "application/json;odata=nometadata", "application/json;odata=minimalmetadata", and
            "application/json;odata=fullmetadata".
        :type format: str or ~azure.data.tables.models.OdataMetadataFormat or None
        :return: None
        """
        data_service_version = "3.0"
        content_type = kwargs.pop("content_type", "application/json")
        accept = "application/json"

        # Construct URL
        url = self._batch_update_entity.metadata["url"]  # type: ignore
        path_format_arguments = {
            "url": self._serialize.url("self._config.url", self._config.url, "str", skip_quote=True),
            "table": self._serialize.url("table", table, "str"),
            "partitionKey": self._serialize.url("partition_key", partition_key, "str"),
            "rowKey": self._serialize.url("row_key", row_key, "str"),
        }
        url = self._client._client.format_url(url, **path_format_arguments)  # pylint: disable=protected-access

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters["timeout"] = self._serialize.query("timeout", timeout, "int", minimum=0)
        if format is not None:
            query_parameters["$format"] = self._serialize.query("format", format, "str")

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters["x-ms-version"] = self._serialize.header("self._config.version", self._config.version, "str")
        if request_id_parameter is not None:
            header_parameters["x-ms-client-request-id"] = self._serialize.header(
                "request_id_parameter", request_id_parameter, "str"
            )
        header_parameters["DataServiceVersion"] = self._serialize.header(
            "data_service_version", data_service_version, "str"
        )
        if if_match is not None:
            header_parameters["If-Match"] = self._serialize.header("if_match", if_match, "str")
        header_parameters["Content-Type"] = self._serialize.header("content_type", content_type, "str")
        header_parameters["Accept"] = self._serialize.header("accept", accept, "str")

        body_content_kwargs = {}  # type: Dict[str, Any]
        if table_entity_properties is not None:
            body_content = self._serialize.body(table_entity_properties, "{object}")
        else:
            body_content = None
        body_content_kwargs["content"] = body_content
        request = self._client._client.put(  # pylint: disable=protected-access
            url, query_parameters, header_parameters, **body_content_kwargs
        )
        self.requests.append(request)

    _batch_update_entity.metadata = {"url": "/{table}(PartitionKey='{partitionKey}',RowKey='{rowKey}')"}  # type: ignore

    def _batch_merge_entity(
        self,
        table: str,
        partition_key: str,
        row_key: str,
        timeout: Optional[int] = None,
        request_id_parameter: Optional[str] = None,
        if_match: Optional[str] = None,
        table_entity_properties: Optional[EntityType] = None,
        format: Optional[Union[str, models.OdataMetadataFormat]] = None,  # pylint: disable=redefined-builtin
        **kwargs,
    ) -> None:
        """Merge entity in a table.

        :param table: The name of the table.
        :type table: str
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param timeout: The timeout parameter is expressed in seconds.
        :type timeout: int or None
        :param request_id_parameter: Provides a client-generated, opaque value with a 1 KB character
            limit that is recorded in the analytics logs when analytics logging is enabled.
        :type request_id_parameter: str or None
        :param if_match: Match condition for an entity to be updated. If specified and a matching
            entity is not found, an error will be raised. To force an unconditional update, set to the
            wildcard character (*). If not specified, an insert will be performed when no existing entity
            is found to update and a merge will be performed if an existing entity is found.
        :type if_match: str or None
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, object] or None
        :param format: Specifies the media type for the response. Known values are:
            "application/json;odata=nometadata", "application/json;odata=minimalmetadata", and
            "application/json;odata=fullmetadata".
        :type format: str or ~azure.data.tables.models.OdataMetadataFormat or None
        :return: None
        """
        data_service_version = "3.0"
        content_type = kwargs.pop("content_type", "application/json")
        accept = "application/json"

        # Construct URL
        url = self._batch_merge_entity.metadata["url"]  # type: ignore
        path_format_arguments = {
            "url": self._serialize.url("self._config.url", self._config.url, "str", skip_quote=True),
            "table": self._serialize.url("table", table, "str"),
            "partitionKey": self._serialize.url("partition_key", partition_key, "str"),
            "rowKey": self._serialize.url("row_key", row_key, "str"),
        }
        url = self._client._client.format_url(url, **path_format_arguments)  # pylint: disable=protected-access

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters["timeout"] = self._serialize.query("timeout", timeout, "int", minimum=0)
        if format is not None:
            query_parameters["$format"] = self._serialize.query("format", format, "str")

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters["x-ms-version"] = self._serialize.header("self._config.version", self._config.version, "str")
        if request_id_parameter is not None:
            header_parameters["x-ms-client-request-id"] = self._serialize.header(
                "request_id_parameter", request_id_parameter, "str"
            )
        header_parameters["DataServiceVersion"] = self._serialize.header(
            "data_service_version", data_service_version, "str"
        )
        if if_match is not None:
            header_parameters["If-Match"] = self._serialize.header("if_match", if_match, "str")
        header_parameters["Content-Type"] = self._serialize.header("content_type", content_type, "str")
        header_parameters["Accept"] = self._serialize.header("accept", accept, "str")

        body_content_kwargs = {}  # type: Dict[str, Any]
        if table_entity_properties is not None:
            body_content = self._serialize.body(table_entity_properties, "{object}")
        else:
            body_content = None
        body_content_kwargs["content"] = body_content
        request = self._client._client.patch(  # pylint: disable=protected-access
            url, query_parameters, header_parameters, **body_content_kwargs
        )
        if self._is_cosmos_endpoint:
            _transform_patch_to_cosmos_post(request)
        self.requests.append(request)

    _batch_merge_entity.metadata = {"url": "/{table}(PartitionKey='{partitionKey}',RowKey='{rowKey}')"}  # type: ignore

    def delete(self, entity: EntityType, **kwargs) -> None:
        """Deletes the specified entity in a table.

        :param entity: The properties for the table entity.
        :type entity: ~azure.data.tables.TableEntity or dict[str, Any]
        :keyword str etag: Etag of the entity
        :keyword match_condition: MatchCondition
        :paramtype match_condition: ~azure.core.MatchCondition
        :return: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_batching.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        self._verify_partition_key(entity)
        match_condition = kwargs.pop("match_condition", None)
        etag = kwargs.pop("etag", None)
        if match_condition and not etag:
            try:
                etag = entity.metadata.get("etag", None)  # type: ignore[union-attr]
            except (AttributeError, TypeError):
                pass
        match_condition = _get_match_condition(
            etag=etag, match_condition=match_condition or MatchConditions.Unconditionally
        )

        self._batch_delete_entity(
            table=self.table_name,
            partition_key=_prepare_key(entity["PartitionKey"]),
            row_key=_prepare_key(entity["RowKey"]),
            if_match=prep_if_match(etag, match_condition),  # type: ignore[arg-type]
            **kwargs,
        )

    def _batch_delete_entity(
        self,
        table: str,
        partition_key: str,
        row_key: str,
        if_match: str,
        timeout: Optional[int] = None,
        request_id_parameter: Optional[str] = None,
        format: Optional[Union[str, models.OdataMetadataFormat]] = None,  # pylint: disable=redefined-builtin
    ) -> None:
        """Deletes the specified entity in a table.

        :param table: The name of the table.
        :type table: str
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param if_match: Match condition for an entity to be deleted. If specified and a matching
         entity is not found, an error will be raised. To force an unconditional delete, set to the
         wildcard character (*).
        :type if_match: str
        :param timeout: The timeout parameter is expressed in seconds.
        :type timeout: int or None
        :param request_id_parameter: Provides a client-generated, opaque value with a 1 KB character
         limit that is recorded in the analytics logs when analytics logging is enabled.
        :type request_id_parameter: str or None
        :param format: Specifies the media type for the response. Known values are:
         "application/json;odata=nometadata", "application/json;odata=minimalmetadata", and
         "application/json;odata=fullmetadata".
        :type format: str or ~azure.data.tables.models.OdataMetadataFormat or None
        :return: None
        """
        data_service_version = "3.0"
        accept = "application/json;odata=minimalmetadata"

        # Construct URL
        url = self._batch_delete_entity.metadata["url"]  # type: ignore
        path_format_arguments = {
            "url": self._serialize.url("self._config.url", self._config.url, "str", skip_quote=True),
            "table": self._serialize.url("table", table, "str"),
            "partitionKey": self._serialize.url("partition_key", partition_key, "str"),
            "rowKey": self._serialize.url("row_key", row_key, "str"),
        }
        url = self._client._client.format_url(url, **path_format_arguments)  # pylint: disable=protected-access

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters["timeout"] = self._serialize.query("timeout", timeout, "int", minimum=0)
        if format is not None:
            query_parameters["$format"] = self._serialize.query("format", format, "str")

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters["x-ms-version"] = self._serialize.header("self._config.version", self._config.version, "str")
        if request_id_parameter is not None:
            header_parameters["x-ms-client-request-id"] = self._serialize.header(
                "request_id_parameter", request_id_parameter, "str"
            )
        header_parameters["DataServiceVersion"] = self._serialize.header(
            "data_service_version", data_service_version, "str"
        )
        header_parameters["If-Match"] = self._serialize.header("if_match", if_match, "str")
        header_parameters["Accept"] = self._serialize.header("accept", accept, "str")

        request = self._client._client.delete(  # pylint: disable=protected-access
            url, query_parameters, header_parameters
        )
        self.requests.append(request)

    _batch_delete_entity.metadata = {"url": "/{table}(PartitionKey='{partitionKey}',RowKey='{rowKey}')"}  # type: ignore

    def upsert(self, entity: EntityType, mode: Union[str, UpdateMode] = UpdateMode.MERGE, **kwargs) -> None:
        """Update/Merge or Insert entity into table.

        :param entity: The properties for the table entity.
        :type entity: ~azure.data.tables.TableEntity or dict[str, Any]
        :param mode: Merge or Replace entity
        :type mode: ~azure.data.tables.UpdateMode
        :return: None
        :raises ValueError: If mode type is not supported.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_batching.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        self._verify_partition_key(entity)
        temp = entity.copy()  # type: ignore

        partition_key = _prepare_key(temp["PartitionKey"])
        row_key = _prepare_key(temp["RowKey"])
        temp = _add_entity_properties(temp)

        if mode == UpdateMode.MERGE:
            self._batch_merge_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=temp,
                **kwargs,
            )
        elif mode == UpdateMode.REPLACE:
            self._batch_update_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=temp,
                **kwargs,
            )
        else:
            raise ValueError(f"Mode type '{mode}' is not supported.")
