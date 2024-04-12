# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Union, Any, Mapping, Optional, List, Tuple

from azure.core import MatchConditions
from azure.core.rest import HttpRequest

from ._common_conversion import _transform_patch_to_cosmos_post
from ._models import UpdateMode, TransactionOperation
from ._serialize import _add_entity_properties, _prepare_key, _get_match_condition
from ._entity import TableEntity
from ._generated.operations._operations import (
    build_table_insert_entity_request,
    build_table_merge_entity_request,
    build_table_update_entity_request,
    build_table_delete_entity_request,
)
from ._generated._configuration import AzureTableConfiguration
from ._generated.aio._configuration import AzureTableConfiguration as AsyncAzureTableConfiguration


EntityType = Union[TableEntity, Mapping[str, Any]]
OperationType = Union[TransactionOperation, str]
TransactionOperationType = Union[Tuple[OperationType, EntityType], Tuple[OperationType, EntityType, Mapping[str, Any]]]


class TableBatchOperations(object):
    """
    This is the class that is used for batch operations for the data tables
    service.

    The Tables service supports batch transactions on entities that are in the
    same table and belong to the same partition group. Multiple operations are
    supported within a single transaction. The batch can include at most 100
    entities, and its total payload may be no more than 4 MB in size.

    :ivar str table_name: The name of the table.
    :ivar requests: A list of :class:`~azure.core.rest.HttpRequest` in a batch.
    :vartype requests: list[~azure.core.rest.HttpRequest]
    """

    def __init__(
        self,
        config: Union[AzureTableConfiguration, AsyncAzureTableConfiguration],
        endpoint: str,
        table_name: str,
        is_cosmos_endpoint: bool = False,
    ) -> None:
        """Create TableClient from a Credential.

        :param config: An AzureTableConfiguration object.
        :type config: ~azure.data.tables._generated._configuration.AzureTableConfiguration
        :param endpoint: The primary account URL.
        :type endpoint: str
        :param table_name: The name of the Table to perform operations on.
        :type table_name: str
        :param is_cosmos_endpoint: True if the client endpoint is for Tables Cosmos. False if not. Default is False.
        :type is_cosmos_endpoint: bool
        """
        self._config = config
        self._base_url = endpoint
        self._is_cosmos_endpoint = is_cosmos_endpoint
        self.table_name = table_name

        self._partition_key: Optional[str] = None
        self.requests: List[HttpRequest] = []

    def __len__(self) -> int:
        return len(self.requests)

    def _verify_partition_key(self, entity: EntityType) -> None:
        if "PartitionKey" not in entity or "RowKey" not in entity:
            raise ValueError("PartitionKey and/or RowKey were not provided in entity")
        if self._partition_key is None:
            self._partition_key = entity["PartitionKey"]
        elif entity["PartitionKey"] != self._partition_key:
            raise ValueError("Partition Keys in the batch must all be the same.")

    def add_operation(self, operation: TransactionOperationType) -> None:
        """Add a single operation to a batch.

        :param operation: An operation include operation type and entity, may with kwargs.
        :type operation: A tuple of ~azure.data.tables.TransactionOperation or str, and
            ~azure.data.tables.TableEntity or Mapping[str, Any]. Or a tuple of
            ~azure.data.tables.TransactionOperation or str, and
            ~azure.data.tables.TableEntity or Mapping[str, Any], and Mapping[str, Any]
        :return: None
        """
        if len(operation) == 3:
            operation_type, entity, kwargs = operation  # type: ignore[misc]
        else:
            operation_type, entity, kwargs = operation[0], operation[1], {}
        try:
            getattr(self, operation_type.lower())(entity, **kwargs)
        except AttributeError as exc:
            raise ValueError(f"Unrecognized operation: {operation_type}") from exc

    def create(self, entity: EntityType, **kwargs) -> None:
        """Adds an insert operation to the current batch.

        :param entity: The properties for the table entity.
        :type entity: ~azure.data.tables.TableEntity or dict[str, Any]
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
        entity = _add_entity_properties(entity)
        request = build_table_insert_entity_request(
            table=self.table_name, json=entity, version=self._config.version, **kwargs
        )
        request.url = self._base_url + request.url
        self.requests.append(request)

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

            .. literalinclude:: ../samples/sample_batching.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        self._verify_partition_key(entity)
        entity = _add_entity_properties(entity)
        partition_key = _prepare_key(entity["PartitionKey"])
        row_key = _prepare_key(entity["RowKey"])

        match_condition = kwargs.pop("match_condition", None)
        etag = kwargs.pop("etag", None)
        if match_condition and not etag and isinstance(entity, TableEntity):
            if hasattr(entity, "metadata"):
                etag = entity.metadata.get("etag")
        match_condition = _get_match_condition(
            etag=etag, match_condition=match_condition or MatchConditions.Unconditionally
        )
        if mode == UpdateMode.REPLACE:
            request = build_table_update_entity_request(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                etag=etag,
                match_condition=match_condition,
                json=entity,
                version=self._config.version,
                **kwargs,
            )
        elif mode == UpdateMode.MERGE:
            request = build_table_merge_entity_request(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                etag=etag,
                match_condition=match_condition,
                json=entity,
                version=self._config.version,
                **kwargs,
            )
            if self._is_cosmos_endpoint:
                _transform_patch_to_cosmos_post(request)
        else:
            raise ValueError(f"Mode type '{mode}' is not supported.")

        request.url = self._base_url + request.url
        self.requests.append(request)

    def delete(self, entity: EntityType, **kwargs) -> None:
        """Adds a delete operation to the current branch.

        param entity: The properties for the table entity.
        :type entity: ~azure.data.tables.TableEntity or dict[str, Any]
        :keyword str etag: Etag of the entity
        :keyword match_condition: MatchCondition
        :paramtype match_condition: ~azure.core.MatchCondition
        :return: None
        :raises: ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_batching.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        self._verify_partition_key(entity)
        match_condition = kwargs.pop("match_condition", None)
        etag = kwargs.pop("etag", None)
        if match_condition and not etag and isinstance(entity, TableEntity):
            etag = entity.metadata.get("etag")
        match_condition = _get_match_condition(
            etag=etag, match_condition=match_condition or MatchConditions.Unconditionally
        )
        request = build_table_delete_entity_request(
            table=self.table_name,
            partition_key=_prepare_key(entity["PartitionKey"]),
            row_key=_prepare_key(entity["RowKey"]),
            etag=etag,
            match_condition=match_condition,
            version=self._config.version,
            **kwargs,
        )
        request.url = self._base_url + request.url
        self.requests.append(request)

    def upsert(self, entity: EntityType, mode: Union[str, UpdateMode] = UpdateMode.MERGE, **kwargs) -> None:
        """Adds an upsert (update/merge) operation to the batch.

        :param entity: The properties for the table entity.
        :type entity: ~azure.data.tables.TableEntity or dict[str, Any]
        :param mode: Merge or Replace entity
        :type mode: ~azure.data.tables.UpdateMode
        :return: None
        :raises: ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_batching.py
                :start-after: [START batching]
                :end-before: [END batching]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        self._verify_partition_key(entity)

        # TODO: This ordering is backwards. Tracked as part of issue #26318
        partition_key = _prepare_key(entity["PartitionKey"])
        row_key = _prepare_key(entity["RowKey"])
        entity = _add_entity_properties(entity)

        if mode == UpdateMode.REPLACE:
            request = build_table_update_entity_request(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                json=entity,
                version=self._config.version,
                **kwargs,
            )
        elif mode == UpdateMode.MERGE:
            request = build_table_merge_entity_request(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                json=entity,
                version=self._config.version,
                **kwargs,
            )
            if self._is_cosmos_endpoint:
                _transform_patch_to_cosmos_post(request)
        else:
            raise ValueError(f"Mode type '{mode}' is not supported.")

        request.url = self._base_url + request.url
        self.requests.append(request)
