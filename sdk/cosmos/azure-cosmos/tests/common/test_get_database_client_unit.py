# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import inspect
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
    client._item_context = ItemClientContext(MagicMock())
    return client, proxy_type


@pytest.mark.parametrize("database_id", ["sales", 123, 0, None, "00123"])
def test_properties_id_is_converted_to_string(client_and_proxy_type, database_id):
    client, proxy_type = client_and_proxy_type
    properties = {"id": database_id, "_rid": "unused"}

    database = client.get_database_client(database=properties)

    assert isinstance(database, proxy_type)
    assert not inspect.isawaitable(database)
    assert database.id == str(database_id)
    assert database.database_link == f"dbs/{database_id}"
    assert database.client_connection is client.client_connection
    assert properties == {"id": database_id, "_rid": "unused"}
    assert client.client_connection.mock_calls == []


def test_string_name_is_preserved(client_and_proxy_type):
    client, proxy_type = client_and_proxy_type

    database = client.get_database_client("Sales")

    assert isinstance(database, proxy_type)
    assert database.id == "Sales"
    assert database.database_link == "dbs/Sales"
    assert client.client_connection.mock_calls == []


def test_existing_proxy_creates_new_proxy_on_calling_client(client_and_proxy_type):
    client, proxy_type = client_and_proxy_type
    original_connection = MagicMock()
    original = proxy_type(original_connection, "sales")

    database = client.get_database_client(original)

    assert isinstance(database, proxy_type)
    assert database is not original
    assert database.id == original.id
    assert database.client_connection is client.client_connection
    assert original.client_connection is original_connection
    assert client.client_connection.mock_calls == []
    assert original_connection.mock_calls == []


def test_missing_id_still_raises_key_error(client_and_proxy_type):
    client, _ = client_and_proxy_type

    with pytest.raises(KeyError, match="id"):
        client.get_database_client({})

    assert client.client_connection.mock_calls == []
