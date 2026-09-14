# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import inspect
from collections import UserDict
from collections.abc import Mapping
from typing import get_args, get_origin, get_type_hints
from unittest.mock import MagicMock

import pytest

from azure.cosmos import ContainerProxy, DatabaseProxy
from azure.cosmos.aio import ContainerProxy as AsyncContainerProxy
from azure.cosmos.aio import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos._helpers._item_context import ItemClientContext


@pytest.fixture(
    params=[(DatabaseProxy, ContainerProxy), (AsyncDatabaseProxy, AsyncContainerProxy)],
    ids=["sync", "aio"],
)
def database_and_proxy_type(request, backend_name):
    database_type, proxy_type = request.param
    connection = MagicMock()
    backend = MagicMock()
    backend.name = backend_name
    context = ItemClientContext(backend)
    database = database_type(connection, "sales", _item_context=context)
    yield database, proxy_type
    assert connection.mock_calls == []
    assert backend.mock_calls == []
    assert not context.response_state.last_response_headers


@pytest.fixture(params=["core-python", "rust"])
def backend_name(request):
    return request.param


@pytest.mark.parametrize("mapping_type", [dict, UserDict])
@pytest.mark.parametrize("container_id", ["orders", 123, 0, None, False, 1.5, "00123"])
def test_properties_id_is_converted_to_string(database_and_proxy_type, mapping_type, container_id):
    database, proxy_type = database_and_proxy_type
    properties = mapping_type(id=container_id, _rid="unused", partitionKey={"paths": ["/tenant"]})
    original = dict(properties)

    container = database.get_container_client(container=properties)

    assert isinstance(container, proxy_type)
    assert not inspect.isawaitable(container)
    assert container.id == str(container_id)
    assert isinstance(container.id, str)
    assert container.container_link == f"dbs/sales/colls/{container_id}"
    assert container.client_connection is database.client_connection
    assert container._item_context is database._item_context
    assert properties == original


@pytest.mark.parametrize("name", ["Orders", "00123", "does-not-exist"])
def test_string_name_is_preserved_without_checking_existence(database_and_proxy_type, name):
    database, proxy_type = database_and_proxy_type

    container = database.get_container_client(name)

    assert isinstance(container, proxy_type)
    assert container.id == name
    assert container.container_link == f"dbs/sales/colls/{name}"
    assert container._item_context is database._item_context
    assert not inspect.isawaitable(container)
    assert not inspect.iscoroutinefunction(database.get_container_client)


def test_existing_proxy_creates_new_proxy_under_current_database(database_and_proxy_type):
    database, proxy_type = database_and_proxy_type
    original_connection = MagicMock()
    original_context = ItemClientContext(MagicMock())
    original = proxy_type(original_connection, "dbs/other", "orders", _item_context=original_context)

    container = database.get_container_client(original)

    assert isinstance(container, proxy_type)
    assert container is not original
    assert container.id == original.id
    assert container.container_link == "dbs/sales/colls/orders"
    assert container.client_connection is database.client_connection
    assert container._item_context is database._item_context
    assert original.container_link == "dbs/other/colls/orders"
    assert original.client_connection is original_connection
    assert original._item_context is original_context
    assert original_connection.mock_calls == []
    assert original_context.backend.mock_calls == []


@pytest.mark.parametrize("mapping_type", [dict, UserDict])
def test_missing_id_still_raises_key_error(database_and_proxy_type, mapping_type):
    database, _ = database_and_proxy_type

    with pytest.raises(KeyError, match="id"):
        database.get_container_client(mapping_type())


def test_id_conversion_errors_propagate(database_and_proxy_type):
    database, _ = database_and_proxy_type
    error = ValueError("cannot stringify ID")

    class InvalidId:
        def __str__(self):
            raise error

    with pytest.raises(ValueError) as raised:
        database.get_container_client({"id": InvalidId()})

    assert raised.value is error


@pytest.mark.parametrize("args, kwargs", [
    ((), {}),
    (("orders", "extra"), {}),
    (("orders",), {"container": "other"}),
    (("orders",), {"timeout": None}),
    (("orders",), {"initial_headers": None}),
    (("orders",), {"response_hook": None}),
    (("orders",), {"session_token": None}),
])
def test_invalid_arguments_fail_without_io(database_and_proxy_type, args, kwargs):
    database, _ = database_and_proxy_type

    with pytest.raises(TypeError):
        database.get_container_client(*args, **kwargs)


def test_annotation_accepts_general_properties_mappings(database_and_proxy_type):
    database, _ = database_and_proxy_type
    annotation = get_type_hints(database.get_container_client)["container"]
    assert any(get_origin(argument) is Mapping for argument in get_args(annotation))
