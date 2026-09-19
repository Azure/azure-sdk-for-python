# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Unit coverage for getting a container client from a database client (no network).

Like its database counterpart, this is purely local. It does not check that the
container exists and must not make a request, because customers call it on every
operation. Every test proves that by asserting the connection and the engine
recorded nothing at all.

It runs under both engine names, since the container client carries the context
that decides which engine its item operations will use, and that must survive
being passed along whichever engine is configured.

The recurring guarantee is ownership: whatever form the container is named in,
the client that comes back belongs to *this* database, and anything handed in is
left untouched.
"""

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
    """Build a sync or async database client whose connection and engine are stand-ins.

    After each test the fixture asserts three things: the connection recorded no
    calls, the engine recorded none either, and no response headers were left
    behind. Together they prove the call was entirely local -- not just that it
    sent nothing, but that it did not even touch the shared state a real request
    would update.
    """
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
    """Run every test under both engine names, so neither changes this local behavior."""
    return request.param


@pytest.mark.parametrize("mapping_type", [dict, UserDict])
@pytest.mark.parametrize("container_id", ["orders", 123, 0, None, False, 1.5, "00123"])
def test_properties_id_is_converted_to_string(database_and_proxy_type, mapping_type, container_id):
    """A container described by its properties yields a client named by the string form
    of its id, without editing what the caller passed.

    The ids cover several values that are not strings: a number, zero, ``None``,
    ``False``, and a decimal. Zero and ``False`` are the traps, since code
    testing the id for truth would read both as missing. The id ``"00123"``
    guards the opposite mistake -- converting it through a number would drop the
    leading zeros and address a different container.

    The resulting client is nested under this database's name, carries the
    database's connection and shared context, and the caller's properties come
    back unchanged even though they include a nested partition key.
    """
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
    """A container name is used exactly as given, and existence is never checked.

    One of the names is deliberately a container that does not exist, and the
    call still succeeds. Getting a client is not a lookup: the failure, if any,
    belongs to the first real operation. Checking here would cost a request
    every time a customer reached for a container.

    Capitalization and leading zeros are preserved, since names are matched
    exactly. On the async client this is not something to wait on, and the
    method is not declared as such either.
    """
    database, proxy_type = database_and_proxy_type

    container = database.get_container_client(name)

    assert isinstance(container, proxy_type)
    assert container.id == name
    assert container.container_link == f"dbs/sales/colls/{name}"
    assert container._item_context is database._item_context
    assert not inspect.isawaitable(container)
    assert not inspect.iscoroutinefunction(database.get_container_client)


def test_existing_proxy_creates_new_proxy_under_current_database(database_and_proxy_type):
    """A container client from another database is re-homed under this one, and the
    original keeps pointing where it did.

    The original belongs to a different database and connection. What comes back
    keeps only the container name and is addressed under *this* database, using
    this database's connection and shared context.

    That is the guarantee that matters: passing in a container client from
    somewhere else cannot make this call reach into another database. The
    original is then checked to still address its own database, with its own
    connection and context untouched.
    """
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
    """Properties with no id raise ``KeyError`` naming the missing key, for both a
    plain dictionary and a dictionary-like mapping.

    It stays a ``KeyError`` because that is what earlier versions raised and
    customers already catch it.
    """
    database, _ = database_and_proxy_type

    with pytest.raises(KeyError, match="id"):
        database.get_container_client(mapping_type())


def test_id_conversion_errors_propagate(database_and_proxy_type):
    """An error raised while converting the id reaches the caller unchanged.

    The id is an object that fails when turned into text. That exact exception
    comes back, rather than being swallowed or replaced with a vaguer one, so a
    customer sees the real reason their value could not be used.
    """
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
    """Calls that do not match the signature fail, and request options are not
    accepted at all.

    Beyond the obvious mistakes -- no container, an extra positional value, the
    container given twice -- four request options are refused: a timeout,
    initial headers, a response hook, and a session token.

    Refusing those is the point. They all look reasonable, and a customer
    passing one plainly believes this call talks to the service. Accepting and
    ignoring them would leave that belief in place; the error corrects it.
    """
    database, _ = database_and_proxy_type

    with pytest.raises(TypeError):
        database.get_container_client(*args, **kwargs)


def test_annotation_accepts_general_properties_mappings(database_and_proxy_type):
    """The declared type allows any mapping of properties, not only a plain dictionary.

    Customers pass dictionary-like objects -- results from other calls, custom
    mapping types -- and the call handles them. If the declared type said
    ``dict``, type checkers would flag correct code as wrong.
    """
    database, _ = database_and_proxy_type
    annotation = get_type_hints(database.get_container_client)["container"]
    assert any(get_origin(argument) is Mapping for argument in get_args(annotation))
