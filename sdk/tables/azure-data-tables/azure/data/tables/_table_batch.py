# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import (
    Union,
    Any,
    Dict,
)

from ._models import UpdateMode
from ._serialize import _get_match_headers, _add_entity_properties


class TableBatchOperations(object):
    """
    This is the class that is used for batch operations for the data tables
    service.

    The Tables service supports batch transactions on entities that are in the
    same table and belong to the same partition group. Multiple operations are
    supported within a single transaction. The batch can include at most 100
    entities, and its total payload may be no more than 4 MB in size.

    """

    def __init__(
        self,
        client,  # type: AzureTable
        serializer,  # type: msrest.Serializer
        deserializer,  # type: msrest.Deserializer
        config,  # type: AzureTableConfiguration
        table_name,  # type: str
        table_client,  # type: TableClient
        **kwargs  # type: Dict[str, Any]
    ):
        """Create TableClient from a Credential.

        :param client: an AzureTable object
        :type client: AzureTable
        :param serializer: serializer object for request serialization
        :type serializer: msrest.Serializer
        :param deserializer: deserializer object for request serialization
        :type deserializer: msrest.Deserializer
        :param config: Azure Table Configuration object
        :type config: AzureTableConfiguration
        :param table_name: name of the Table to perform operations on
        :type table_name: str
        :param table_client: TableClient object to perform operations on
        :type table_client: TableClient

        :returns: None
        """
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self._config = config
        self.table_name = table_name
        self._table_client = table_client

        self._partition_key = kwargs.pop("partition_key", None)
        self._requests = []
        self._entities = []

    def _verify_partition_key(
        self, entity  # type: Union[Entity, dict]
    ):
        # (...) -> None
        if self._partition_key is None:
            self._partition_key = entity["PartitionKey"]
        elif "PartitionKey" in entity:
            if entity["PartitionKey"] != self._partition_key:
                raise ValueError("Partition Keys must all be the same")

    def create_entity(
        self,
        entity,  # type: Union[TableEntity, Dict[str,str]]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Adds an insert operation to the current batch.

        :param entity: The properties for the table entity.
        :type entity: TableEntity or dict[str,str]
        :return: None
        :raises ValueError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_batching.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        self._verify_partition_key(entity)

        if "PartitionKey" in entity and "RowKey" in entity:
            entity = _add_entity_properties(entity)
        else:
            raise ValueError("PartitionKey and RowKey were not provided in entity")
        self._batch_create_entity(table=self.table_name, entity=entity, **kwargs)
        self._entities.append(entity)

    def _batch_create_entity(
        self,
        table,  # type: str
        entity,  # type: Union[TableEntity, Dict[str,str]]
        timeout=None,  # type: Optional[int]
        request_id_parameter=None,  # type: Optional[str]
        response_preference="return-no-content",  # type: Optional[Union[str, "models.ResponseFormat"]]
        query_options=None,  # type: Optional["models.QueryOptions"]
        **kwargs  # type: Any
    ):
        # (...) -> None
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
        :type: entity: dict or :class:`~azure.data.tables.models.Entity`
        """
        _format = None
        if query_options is not None:
            _format = query_options.format
        data_service_version = "3.0"
        content_type = kwargs.pop("content_type", "application/json;odata=nometadata")
        accept = "application/json;odata=minimalmetadata"

        # Construct URL
        url = self._batch_create_entity.metadata["url"]  # type: ignore
        path_format_arguments = {
            "url": self._serialize.url(
                "self._config.url", self._config.url, "str", skip_quote=True
            ),
            "table": self._serialize.url("table", table, "str"),
        }
        url = self._client._client.format_url(  # pylint: disable=protected-access
            url, **path_format_arguments
        )

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters["timeout"] = self._serialize.query(
                "timeout", timeout, "int", minimum=0
            )
        if _format is not None:
            query_parameters["$format"] = self._serialize.query(
                "format", _format, "str"
            )

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters["x-ms-version"] = self._serialize.header(
            "self._config.version", self._config.version, "str"
        )
        if request_id_parameter is not None:
            header_parameters["x-ms-client-request-id"] = self._serialize.header(
                "request_id_parameter", request_id_parameter, "str"
            )
        header_parameters["DataServiceVersion"] = self._serialize.header(
            "data_service_version", data_service_version, "str"
        )
        if response_preference is not None:
            header_parameters["Prefer"] = self._serialize.header(
                "response_preference", response_preference, "str"
            )
        header_parameters["Content-Type"] = self._serialize.header(
            "content_type", content_type, "str"
        )
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
        self._requests.append(request)

    _batch_create_entity.metadata = {"url": "/{table}"}  # type: ignore

    def update_entity(
        self,
        entity,  # type: Union[TableEntity, Dict[str,str]]
        mode=UpdateMode.MERGE,  # type: UpdateMode
        **kwargs  # type: Any
    ):
        # (...) -> None

        """Adds an update operation to the current batch.

        :param entity: The properties for the table entity.
        :type entity: TableEntity or dict[str,str]
        :param mode: Merge or Replace entity
        :type mode: ~azure.data.tables.UpdateMode
        :keyword str etag: Etag of the entity
        :keyword ~azure.core.MatchConditions match_condition: MatchCondition
        :return: None
        :raises ValueError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_batching.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        self._verify_partition_key(entity)

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
        if mode is UpdateMode.REPLACE:
            self._batch_update_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                if_match=if_match or "*",
                table_entity_properties=entity,
                **kwargs
            )
        elif mode is UpdateMode.MERGE:
            self._batch_merge_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                if_match=if_match or "*",
                table_entity_properties=entity,
                **kwargs
            )
        self._entities.append(entity)

    def _batch_update_entity(
        self,
        table,  # type: str
        partition_key,  # type: str
        row_key,  # type: str
        timeout=None,  # type: Optional[int]
        request_id_parameter=None,  # type: Optional[str]
        if_match=None,  # type: Optional[str]
        table_entity_properties=None,  # type: Optional[Dict[str, object]]
        query_options=None,  # type: Optional["models.QueryOptions"]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Update entity in a table.

        :param table: The name of the table.
        :type table: str
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param timeout: The timeout parameter is expressed in seconds.
        :type timeout: int
        :param request_id_parameter: Provides a client-generated, opaque value with a 1 KB character
         limit that is recorded in the analytics logs when analytics logging is enabled.
        :type request_id_parameter: str
        :param if_match: Match condition for an entity to be updated. If specified and a matching
         entity is not found, an error will be raised. To force an unconditional update, set to the
         wildcard character (*). If not specified, an insert will be performed when no existing entity
         is found to update and a replace will be performed if an existing entity is found.
        :type if_match: str
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, object]
        :param query_options: Parameter group.
        :type query_options: ~azure.data.tables.models.QueryOptions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        _format = None
        if query_options is not None:
            _format = query_options.format
        data_service_version = "3.0"
        content_type = kwargs.pop("content_type", "application/json")
        accept = "application/json"

        # Construct URL
        url = self._batch_update_entity.metadata["url"]  # type: ignore
        path_format_arguments = {
            "url": self._serialize.url(
                "self._config.url", self._config.url, "str", skip_quote=True
            ),
            "table": self._serialize.url("table", table, "str"),
            "partitionKey": self._serialize.url("partition_key", partition_key, "str"),
            "rowKey": self._serialize.url("row_key", row_key, "str"),
        }
        url = self._client._client.format_url(  # pylint: disable=protected-access
            url, **path_format_arguments
        )

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters["timeout"] = self._serialize.query(
                "timeout", timeout, "int", minimum=0
            )
        if _format is not None:
            query_parameters["$format"] = self._serialize.query(
                "format", _format, "str"
            )

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters["x-ms-version"] = self._serialize.header(
            "self._config.version", self._config.version, "str"
        )
        if request_id_parameter is not None:
            header_parameters["x-ms-client-request-id"] = self._serialize.header(
                "request_id_parameter", request_id_parameter, "str"
            )
        header_parameters["DataServiceVersion"] = self._serialize.header(
            "data_service_version", data_service_version, "str"
        )
        if if_match is not None:
            header_parameters["If-Match"] = self._serialize.header(
                "if_match", if_match, "str"
            )
        header_parameters["Content-Type"] = self._serialize.header(
            "content_type", content_type, "str"
        )
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
        self._requests.append(request)

    _batch_update_entity.metadata = {
        "url": "/{table}(PartitionKey='{partitionKey}',RowKey='{rowKey}')"
    }  # type: ignore

    def _batch_merge_entity(
        self,
        table,  # type: str
        partition_key,  # type: str
        row_key,  # type: str
        timeout=None,  # type: Optional[int]
        request_id_parameter=None,  # type: Optional[str]
        if_match=None,  # type: Optional[str]
        table_entity_properties=None,  # type: Optional[Dict[str, object]]
        query_options=None,  # type: Optional["models.QueryOptions"]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Merge entity in a table.

        :param table: The name of the table.
        :type table: str
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param timeout: The timeout parameter is expressed in seconds.
        :type timeout: int
        :param request_id_parameter: Provides a client-generated, opaque value with a 1 KB character
         limit that is recorded in the analytics logs when analytics logging is enabled.
        :type request_id_parameter: str
        :param if_match: Match condition for an entity to be updated. If specified and a matching
         entity is not found, an error will be raised. To force an unconditional update, set to the
         wildcard character (*). If not specified, an insert will be performed when no existing entity
         is found to update and a merge will be performed if an existing entity is found.
        :type if_match: str
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, object]
        :param query_options: Parameter group.
        :type query_options: ~azure.data.tables.models.QueryOptions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        _format = None
        if query_options is not None:
            _format = query_options.format
        data_service_version = "3.0"
        content_type = kwargs.pop("content_type", "application/json")
        accept = "application/json"

        # Construct URL
        url = self._batch_merge_entity.metadata["url"]  # type: ignore
        path_format_arguments = {
            "url": self._serialize.url(
                "self._config.url", self._config.url, "str", skip_quote=True
            ),
            "table": self._serialize.url("table", table, "str"),
            "partitionKey": self._serialize.url("partition_key", partition_key, "str"),
            "rowKey": self._serialize.url("row_key", row_key, "str"),
        }
        url = self._client._client.format_url(  # pylint: disable=protected-access
            url, **path_format_arguments
        )

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters["timeout"] = self._serialize.query(
                "timeout", timeout, "int", minimum=0
            )
        if _format is not None:
            query_parameters["$format"] = self._serialize.query(
                "format", _format, "str"
            )

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters["x-ms-version"] = self._serialize.header(
            "self._config.version", self._config.version, "str"
        )
        if request_id_parameter is not None:
            header_parameters["x-ms-client-request-id"] = self._serialize.header(
                "request_id_parameter", request_id_parameter, "str"
            )
        header_parameters["DataServiceVersion"] = self._serialize.header(
            "data_service_version", data_service_version, "str"
        )
        if if_match is not None:
            header_parameters["If-Match"] = self._serialize.header(
                "if_match", if_match, "str"
            )
        header_parameters["Content-Type"] = self._serialize.header(
            "content_type", content_type, "str"
        )
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
        self._requests.append(request)

    _batch_merge_entity.metadata = {
        "url": "/{table}(PartitionKey='{partitionKey}',RowKey='{rowKey}')"
    }

    def delete_entity(
        self,
        partition_key,  # type: str
        row_key,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Adds a delete operation to the current branch.

        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :keyword str etag: Etag of the entity
        :keyword ~azure.core.MatchConditions match_condition: MatchCondition
        :raises ValueError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_batching.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        if self._partition_key:
            if partition_key != self._partition_key:
                raise ValueError("Partition Keys must all be the same")
        else:
            self._partition_key = partition_key

        if_match, _ = _get_match_headers(
            kwargs=dict(
                kwargs,
                etag=kwargs.pop("etag", None),
                match_condition=kwargs.pop("match_condition", None),
            ),
            etag_param="etag",
            match_param="match_condition",
        )

        self._batch_delete_entity(
            table=self.table_name,
            partition_key=partition_key,
            row_key=row_key,
            if_match=if_match or "*",
            **kwargs
        )

        temp_entity = {"PartitionKey": partition_key, "RowKey": row_key}
        self._entities.append(_add_entity_properties(temp_entity))

    def _batch_delete_entity(
        self,
        table,  # type: str
        partition_key,  # type: str
        row_key,  # type: str
        if_match,  # type: str
        timeout=None,  # type: Optional[int]
        request_id_parameter=None,  # type: Optional[str]
        query_options=None,  # type: Optional["models.QueryOptions"]
    ):
        # type: (...) -> None
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
        :type timeout: int
        :param request_id_parameter: Provides a client-generated, opaque value with a 1 KB character
         limit that is recorded in the analytics logs when analytics logging is enabled.
        :type request_id_parameter: str
        :param query_options: Parameter group.
        :type query_options: ~azure.data.tables.models.QueryOptions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        _format = None
        if query_options is not None:
            _format = query_options.format
        data_service_version = "3.0"
        accept = "application/json;odata=minimalmetadata"

        # Construct URL
        url = self._batch_delete_entity.metadata["url"]  # type: ignore
        path_format_arguments = {
            "url": self._serialize.url(
                "self._config.url", self._config.url, "str", skip_quote=True
            ),
            "table": self._serialize.url("table", table, "str"),
            "partitionKey": self._serialize.url("partition_key", partition_key, "str"),
            "rowKey": self._serialize.url("row_key", row_key, "str"),
        }
        url = self._client._client.format_url(  # pylint: disable=protected-access
            url, **path_format_arguments
        )

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters["timeout"] = self._serialize.query(
                "timeout", timeout, "int", minimum=0
            )
        if _format is not None:
            query_parameters["$format"] = self._serialize.query(
                "format", _format, "str"
            )

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters["x-ms-version"] = self._serialize.header(
            "self._config.version", self._config.version, "str"
        )
        if request_id_parameter is not None:
            header_parameters["x-ms-client-request-id"] = self._serialize.header(
                "request_id_parameter", request_id_parameter, "str"
            )
        header_parameters["DataServiceVersion"] = self._serialize.header(
            "data_service_version", data_service_version, "str"
        )
        header_parameters["If-Match"] = self._serialize.header(
            "if_match", if_match, "str"
        )
        header_parameters["Accept"] = self._serialize.header("accept", accept, "str")

        request = self._client._client.delete(  # pylint: disable=protected-access
            url, query_parameters, header_parameters
        )
        self._requests.append(request)

    _batch_delete_entity.metadata = {
        "url": "/{table}(PartitionKey='{partitionKey}',RowKey='{rowKey}')"
    }

    def upsert_entity(
        self,
        entity,  # type: Union[TableEntity, Dict[str,str]]
        mode=UpdateMode.MERGE,  # type: UpdateMode
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Adds an upsert (update/merge) operation to the batch.

        :param entity: The properties for the table entity.
        :type entity: TableEntity or dict[str,str]
        :param mode: Merge or Replace and Insert on fail
        :type mode: ~azure.data.tables.UpdateMode
        :raises ValueError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_batching.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        self._verify_partition_key(entity)

        partition_key = entity["PartitionKey"]
        row_key = entity["RowKey"]
        entity = _add_entity_properties(entity)

        if mode is UpdateMode.MERGE:
            self._batch_merge_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=entity,
                **kwargs
            )
        elif mode is UpdateMode.REPLACE:
            self._batch_update_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=entity,
                **kwargs
            )
        self._entities.append(entity)

    def __enter__(self):
        # type: (...) -> TableBatchOperations
        return self

    def __exit__(
        self,
        *args,  # type: Any
        **kwargs  # type: Any
    ):
        # (...) -> None
        self._table_client._batch_send(*self._requests, **kwargs)
