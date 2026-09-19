# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Unit coverage for getting a database client from a Cosmos client (no network).

Getting a database client is purely local. It does not check that the database
exists, and it must not make a single request -- customers call it in loops, in
constructors, and on every request of a web application, so a hidden lookup here
would be a per-call cost nobody expects.

Every test proves that by asserting the connection and the engine were never
touched at all.

The other theme is that the returned client always belongs to the client it was
asked of. A database client obtained from elsewhere can be handed in, but what
comes back is a fresh one wired to *this* client's connection, and the original
is left exactly as it was.
"""

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
    """Build a bare sync or async Cosmos client that has no working connection.

    The client is created without running its constructor, so nothing connects
    and no credentials are needed. Its connection and engine are stand-ins that
    record every call made against them.

    After each test the fixture asserts both recorded nothing. That single check
    is what proves getting a database client never reaches the service, and it
    applies to failing tests as much as passing ones.
    """
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
    """A database described by its properties yields a client named by the string form
    of its id, without editing what the caller passed.

    The properties are given as three kinds of mapping, including a read-only
    one, so the call must read them rather than modify them in place.

    The ids include values that are not strings at all -- a number, zero, and
    ``None`` -- and each is converted rather than rejected. Zero is the trap:
    code testing the id for truth would treat it as missing. The id ``"00123"``
    guards the opposite mistake, since converting it through a number would lose
    the leading zeros and address a different database.

    The link is built from that id, no properties are cached on the new client,
    and the caller's mapping comes back untouched.
    """
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
    """A database name is used exactly as given, and each call returns a separate
    client.

    The name keeps its capitalization and its leading zeros, because database
    names are matched exactly and altering one addresses a different database.
    An empty name is accepted too -- this call does not validate names, and the
    service is the one that decides.

    Two calls with the same name return two different objects rather than a
    shared one. A shared instance would let state set on one caller's client
    surface in another's.
    """
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
    """Handing in a database client from elsewhere returns a new one wired to this
    client, and leaves the original alone.

    The original belongs to a different connection and carries its own cached
    properties. What comes back keeps only the name: it uses this client's
    connection and shared context, and starts with no cached properties, so it
    cannot serve up settings that were read through some other client.

    The original is then checked field by field -- its connection, its context,
    and its properties are all still its own. Customers pass these objects
    around, and quietly rewiring one to a different connection would redirect
    work they had already set up.
    """
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
    """Properties with no id raise ``KeyError`` naming the missing key.

    It is a ``KeyError`` rather than something friendlier because that is what
    earlier versions raised, and customers catch it. Changing the type here
    would break code that already handles this case.
    """
    client, _ = client_and_proxy_type

    with pytest.raises(KeyError, match="id"):
        client.get_database_client({})

    assert client.client_connection.mock_calls == []


@pytest.mark.parametrize("input_form", ["name", "properties", "proxy"])
def test_calling_client_context_reaches_container(client_and_proxy_type, input_form):
    """The client's shared context carries down through the database to the container.

    Whether the database was named, described by properties, or handed in as an
    existing client, the container reached through it ends up on this client's
    connection and shared context.

    That context is how item operations find the engine the customer configured.
    If it were lost anywhere along the chain, reading an item through a container
    obtained this way could run on a different engine than the one chosen at
    startup.

    Neither step is something to wait on, even on the async client -- both are
    local.
    """
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
    """Something that is not a name, properties, or a database client is a ``TypeError``.

    ``None``, a number, and a list are all rejected. ``None`` is the one worth
    naming: it usually means a variable that was never set, and accepting it
    would produce a client addressing a database literally called "None".
    """
    client, _ = client_and_proxy_type

    with pytest.raises(TypeError):
        client.get_database_client(database)


def test_opposite_proxy_family_is_not_accepted(client_and_proxy_type):
    """A database client from the other client family is refused.

    Handing an async database client to a sync client, or the reverse, raises
    ``TypeError``. The two look alike but their methods differ in whether they
    must be waited on, so quietly accepting one would produce an object whose
    calls fail later, far from the mistake.

    The rejected client's own connection and engine are confirmed untouched.
    """
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
    """The published signature matches what the call actually does.

    It takes one required argument, which may be passed by position or by name,
    and its declared type lists all three accepted forms -- a name, a database
    client, or any mapping of properties. Accepting a general mapping matters
    because customers pass dictionary-like objects, not only plain dictionaries.

    It returns the matching client type, and on the async client it is
    deliberately *not* something to wait on. Declaring it that way would suggest
    a request happens here, which is exactly what this call avoids.
    """
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
