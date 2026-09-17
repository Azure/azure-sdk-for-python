# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import inspect
from collections import UserDict
from types import MappingProxyType
from typing import Any, Mapping, Union, get_type_hints
from unittest.mock import MagicMock

import pytest

from azure.cosmos import CosmosClient, DatabaseProxy
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.aio import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos._helpers._item_context import ItemClientContext


@pytest.fixture(
    params=[(CosmosClient, DatabaseProxy), (AsyncCosmosClient, AsyncDatabaseProxy)],
    ids=["sync", "aio"],
)
def client_and_proxy_type(request):
    client_type, proxy_type = request.param
    client = client_type.__new__(client_type)
    client.client_connection = MagicMock()
    client.client_connection.url_connection = "https://example.invalid"
    client._item_context = ItemClientContext(MagicMock())
    yield client, proxy_type

    assert client.client_connection.mock_calls == []
    assert client._item_context.backend.mock_calls == []


@pytest.mark.parametrize("mapping_type", [dict, UserDict, MappingProxyType])
@pytest.mark.parametrize("database_id", ["sales", 123, 0, None, "00123"])
def test_properties_id_is_converted_to_string(client_and_proxy_type, database_id, mapping_type):
    client, proxy_type = client_and_proxy_type
    properties = mapping_type({"id": database_id, "_rid": "unused"})

    database = client.get_database_client(database=properties)

    assert isinstance(database, proxy_type)
    assert not inspect.isawaitable(database)
    assert database.id == str(database_id)
    assert database.database_link == f"dbs/{database_id}"
    assert database.client_connection is client.client_connection
    assert database._properties is None
    assert properties == {"id": database_id, "_rid": "unused"}
    assert client.client_connection.mock_calls == []


@pytest.mark.parametrize("database_id", ["Sales", "", "00123"])
def test_string_name_is_preserved(client_and_proxy_type, database_id):
    client, proxy_type = client_and_proxy_type

    database = client.get_database_client(database_id)
    another_database = client.get_database_client(database_id)

    assert isinstance(database, proxy_type)
    assert database is not another_database
    assert database.id == database_id
    assert database.database_link == f"dbs/{database_id}"
    assert database.client_connection is client.client_connection
    assert database._properties is None
    assert client.client_connection.mock_calls == []


def test_existing_proxy_creates_new_proxy_on_calling_client(client_and_proxy_type):
    client, proxy_type = client_and_proxy_type
    original_connection = MagicMock()
    original_context = ItemClientContext(MagicMock())
    original_properties = {"id": "sales", "_rid": "unused"}
    original = proxy_type(
        original_connection, "sales", properties=original_properties, _item_context=original_context
    )

    database = client.get_database_client(original)

    assert isinstance(database, proxy_type)
    assert database is not original
    assert database.id == original.id
    assert database.client_connection is client.client_connection
    assert database._item_context is client._item_context
    assert database._properties is None
    assert original.client_connection is original_connection
    assert original._item_context is original_context
    assert original._properties is original_properties
    assert client.client_connection.mock_calls == []
    assert original_connection.mock_calls == []
    assert original_context.backend.mock_calls == []


def test_missing_id_still_raises_key_error(client_and_proxy_type):
    client, _ = client_and_proxy_type

    with pytest.raises(KeyError, match="id"):
        client.get_database_client({})

    assert client.client_connection.mock_calls == []


@pytest.mark.parametrize("input_form", ["name", "properties", "proxy"])
def test_calling_client_context_reaches_container(client_and_proxy_type, input_form):
    client, proxy_type = client_and_proxy_type
    if input_form == "name":
        source = "sales"
    elif input_form == "properties":
        source = {"id": "sales"}
    else:
        source = proxy_type(MagicMock(), "sales", _item_context=ItemClientContext(MagicMock()))

    database = client.get_database_client(source)
    container = database.get_container_client("orders")

    assert not inspect.isawaitable(database)
    assert not inspect.isawaitable(container)
    assert database._item_context is client._item_context
    assert container._item_context is client._item_context
    assert container.client_connection is client.client_connection


@pytest.mark.parametrize("database", [None, 123, []])
def test_invalid_top_level_input_still_raises_type_error(client_and_proxy_type, database):
    client, _ = client_and_proxy_type

    with pytest.raises(TypeError):
        client.get_database_client(database)


def test_opposite_proxy_family_is_not_accepted(client_and_proxy_type):
    client, proxy_type = client_and_proxy_type
    other_proxy_type = AsyncDatabaseProxy if proxy_type is DatabaseProxy else DatabaseProxy
    other_connection = MagicMock()
    other_context = ItemClientContext(MagicMock())
    other_database = other_proxy_type(other_connection, "sales", _item_context=other_context)

    with pytest.raises(TypeError):
        client.get_database_client(other_database)

    assert other_connection.mock_calls == []
    assert other_context.backend.mock_calls == []


def test_public_signature_describes_mapping_and_local_return(client_and_proxy_type):
    client, proxy_type = client_and_proxy_type
    method = type(client).get_database_client
    annotations = get_type_hints(method)
    parameters = inspect.signature(method).parameters

    assert list(parameters) == ["self", "database"]
    assert parameters["database"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert parameters["database"].default is inspect.Parameter.empty
    assert annotations["database"] == Union[str, proxy_type, Mapping[str, Any]]
    assert annotations["return"] is proxy_type
    assert not inspect.iscoroutinefunction(method)
