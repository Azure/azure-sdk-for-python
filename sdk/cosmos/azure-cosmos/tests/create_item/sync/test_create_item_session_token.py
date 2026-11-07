# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``create_item(session_token=...)`` behavior on the Rust backend."""

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos._backend import binding_adapter
from azure.cosmos._backend.operations import OP_CREATE_ITEM
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common._rust_checks import run_on_rust


@pytest.fixture
def container_ids():
    """Own a database with one ``/pk`` container and delete it afterwards."""
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.create_database("create_session_" + uuid.uuid4().hex)
        try:
            database.create_container("orders", partition_key=PartitionKey(path="/pk"))
            yield database.id, "orders"
        finally:
            client.delete_database(database.id)
            with pytest.raises(CosmosResourceNotFoundError):
                database.read()


def test_create_forwards_service_issued_session_token_unchanged_rust(container_ids, monkeypatch):
    """A service-issued session token passed to create_item reaches the Rust driver unchanged.

    A fresh client creates an item with the token another client received; the create succeeds and
    exactly one native create call carried the same token in its typed session setting.
    """
    database_id, container_id = container_ids
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as seeder:
        container = seeder.get_database_client(database_id).get_container_client(container_id)
        seed_body = {"id": uuid.uuid4().hex, "pk": "a"}
        seed = container.create_item(body=seed_body)
        assert seed["id"] == seed_body["id"] and seed["pk"] == "a"
        token = seed.get_response_headers()["x-ms-session-token"]
    assert token, "Seed create must return a service-issued token"

    select = binding_adapter._binding_function_for_op
    native_create = select(OP_CREATE_ITEM)
    native_ids = []

    def capture(handle, prepared, **kwargs):
        assert prepared.settings.session_token == token, "Rust must receive the unchanged token"
        native_ids.append(prepared.item_id)
        return native_create(handle, prepared, **kwargs)

    monkeypatch.setattr(
        binding_adapter, "_binding_function_for_op",
        lambda operation: capture if operation == OP_CREATE_ITEM else select(operation),
    )
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        container = client.get_database_client(database_id).get_container_client(container_id)
        created = run_on_rust(client, lambda: container.create_item(body=dict(body), session_token=token))

    assert created["id"] == body["id"]
    assert created["pk"] == "a"
    assert native_ids == [body["id"]], "Expected one real native create"
