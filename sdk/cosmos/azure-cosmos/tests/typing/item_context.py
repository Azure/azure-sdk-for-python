# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Static regression checks for the item dependency handoff.

Run from the package root:
python -m mypy tests/typing/item_context.py --follow-imports=silent
    --ignore-missing-imports --warn-unused-ignores
"""
from typing import Optional, Union

from typing_extensions import assert_type

from azure.cosmos import CosmosClient
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._backend.contracts import BackendResponse, PreparedRequest, PreparedPageRequest, QueryScope
from azure.cosmos._backend.capabilities import OperationRouting
from azure.cosmos._backend.partition_key_input import BindingPartitionKey
from azure.cosmos._cosmos_client_connection import CosmosClientConnection
from azure.cosmos._helpers._item_context import ClientLastResponseHeaders, ItemClientContext
from azure.cosmos._helpers._item_operations import ItemHelper
from azure.cosmos._helpers._legacy_item_operations import LegacyItemHelper
from azure.cosmos.container import ContainerProxy
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection as AsyncCosmosClientConnection
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.aio._helpers._item_operations import AsyncItemHelper
from azure.cosmos.aio._helpers._legacy_item_operations import AsyncLegacyItemHelper


def check_client_propagation(client: CosmosClient, async_client: AsyncCosmosClient) -> None:
    assert_type(client._item_context, ItemClientContext[CosmosBackend])
    assert_type(async_client._item_context, ItemClientContext[AsyncCosmosBackend])
    database = client.get_database_client("db")
    async_database = async_client.get_database_client("db")
    assert_type(database._item_context, Optional[ItemClientContext[CosmosBackend]])
    assert_type(async_database._item_context, Optional[ItemClientContext[AsyncCosmosBackend]])
    container = database.get_container_client("orders")
    async_container = async_database.get_container_client("orders")
    assert_type(container._item_context, Optional[ItemClientContext[CosmosBackend]])
    assert_type(async_container._item_context, Optional[ItemClientContext[AsyncCosmosBackend]])
    assert_type(container._get_item_helper(), Union[ItemHelper, LegacyItemHelper])
    assert_type(async_container._get_item_helper(), Union[AsyncItemHelper, AsyncLegacyItemHelper])


def check_backend_separation(
    backend: CosmosBackend,
    async_backend: AsyncCosmosBackend,
    connection: CosmosClientConnection,
    async_connection: AsyncCosmosClientConnection,
) -> None:
    context = ItemClientContext(backend)
    async_context = ItemClientContext(async_backend)
    assert_type(context.backend, CosmosBackend)
    assert_type(async_context.backend, AsyncCosmosBackend)
    assert_type(context.response_state, ClientLastResponseHeaders)
    assert_type(async_context.response_state, ClientLastResponseHeaders)
    DatabaseProxy(connection, "db", _item_context=context)
    AsyncDatabaseProxy(async_connection, "db", _item_context=async_context)
    ContainerProxy(connection, "dbs/db", "orders", _item_context=context)
    AsyncContainerProxy(async_connection, "dbs/db", "orders", _item_context=async_context)
    ItemHelper(context.backend)
    AsyncItemHelper(async_context.backend)

    # These ignores must remain necessary: mixing the two modes is a type error.
    DatabaseProxy(connection, "db", _item_context=async_context)  # type: ignore[arg-type]
    AsyncDatabaseProxy(async_connection, "db", _item_context=context)  # type: ignore[arg-type]
    ContainerProxy(connection, "dbs/db", "orders", _item_context=async_context)  # type: ignore[arg-type]
    AsyncContainerProxy(async_connection, "dbs/db", "orders", _item_context=context)  # type: ignore[arg-type]
    ItemHelper(async_context.backend)  # type: ignore[arg-type]
    AsyncItemHelper(context.backend)  # type: ignore[arg-type]
    ItemClientContext(object())  # type: ignore[type-var]

    ItemHelper(backend).create_item(deadline=None, container_link="dbs/d/colls/c", body={"id": "item"})
    awaitable = AsyncItemHelper(async_backend).create_item(
        deadline=None, container_link="dbs/d/colls/c", body={"id": "item"}
    )
    awaitable.close()
    ItemHelper(backend).create_item(body={"id": "item"})  # type: ignore[call-arg]
    ItemHelper(backend).create_item(deadline="10", body={"id": "item"})  # type: ignore[arg-type]


async def check_request_builder_types(backend: CosmosBackend, async_backend: AsyncCosmosBackend) -> None:
    await AsyncItemHelper(async_backend).create_item(body={"id": "item"})  # type: ignore[call-arg]
    await AsyncItemHelper(async_backend).create_item(deadline="10", body={"id": "item"})  # type: ignore[arg-type]
    def build_request() -> PreparedRequest:
        return PreparedRequest(
            op="read_item", container_link="dbs/d/colls/c", body_bytes=b"",
            partition_key=BindingPartitionKey("components", ("p",)), item_id="item",
        )

    async def build_request_awaitable() -> PreparedRequest:
        return build_request()

    assert_type(backend.execute(build_request(), deadline=10.0), BackendResponse)
    assert_type(await async_backend.execute(build_request(), deadline=10.0), BackendResponse)
    backend.execute(None)  # type: ignore[arg-type]
    await async_backend.execute(None)  # type: ignore[arg-type]
    backend.execute(build_request(), deadline="10")  # type: ignore[arg-type]
    await async_backend.execute(build_request(), deadline="10")  # type: ignore[arg-type]
    routing = OperationRouting("read_item")
    backend.run_operation(build_request=build_request, routing=routing, process_response=lambda response: response)
    await async_backend.run_operation(build_request=build_request, routing=routing, process_response=lambda response: response)
    # Coroutine builders must remain type errors on both backends.
    backend.run_operation(build_request=build_request_awaitable, routing=routing, process_response=lambda response: response)  # type: ignore[arg-type]
    await async_backend.run_operation(build_request=build_request_awaitable, routing=routing, process_response=lambda response: response)  # type: ignore[arg-type]
    PreparedPageRequest(op="query_items", container_link="c", cursor=backend.create_item_feed_cursor(), query_scope=QueryScope())
    PreparedPageRequest(op="query_items", container_link="c", cursor={})  # type: ignore[arg-type]
    PreparedPageRequest(op="query_items", container_link="c", query_scope={})  # type: ignore[arg-type]
    await async_backend.run_operation(build_request=build_request, routing=routing, process_response=lambda r: r, legacy_call=lambda: None)  # type: ignore[arg-type,return-value]
