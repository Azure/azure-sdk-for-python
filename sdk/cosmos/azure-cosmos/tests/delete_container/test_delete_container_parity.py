# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Delete only UUID-owned resources; check the exact Rust call, not setup."""
import asyncio
import os
import uuid
from contextlib import nullcontext
from unittest.mock import patch

import pytest
from azure.core import MatchConditions
from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.partition_key import PartitionKey
from common._parity_helpers import (
    run_target_operation, run_target_operation_async,
    skip_unless_emulator, skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture(scope="module")
def owned_database():
    name = "parity_delete_" + uuid.uuid4().hex
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python") as admin:
        try:
            yield admin.create_database(name)
        finally:
            try:
                admin.delete_database(name)
            except exceptions.CosmosResourceNotFoundError:
                pass


def _target(database, name, kind):
    if kind == "mapping":
        return {"id": name}
    if kind == "proxy":
        return database.get_container_client(name)
    return name


def _no_legacy_delete(client, backend):
    return (
        patch.object(client.client_connection, "DeleteContainer",
                     side_effect=AssertionError("Rust deletion used legacy Python"))
        if backend == "rust" else nullcontext()
    )


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("target_kind", ["name", "mapping", "proxy"])
def test_delete_owned_container_and_repeat_missing(owned_database, mode, backend, target_kind):
    name = "container_" + uuid.uuid4().hex
    owned_database.create_container(name, PartitionKey(path="/id"))
    calls = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            assert body is None
            assert headers["X-MS-ACTIVITY-ID"]
            headers["x-test-mutation"] = "isolated"
            calls.append(body)

    def sync_call():
        with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend) as client:
            database = client.get_database_client(owned_database.id)
            target = _target(database, name, target_kind)
            with _no_legacy_delete(client, backend):
                assert run_target_operation(
                    client, lambda: database.delete_container(target, response_hook=Hook(), timeout=30)
                ) is None
                assert "x-test-mutation" not in client.client_connection.last_response_headers
                with pytest.raises(exceptions.CosmosResourceNotFoundError):
                    run_target_operation(client, lambda: database.delete_container(target, timeout=30))

    async def async_call():
        async with AsyncCosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend
        ) as client:
            database = client.get_database_client(owned_database.id)
            target = _target(database, name, target_kind)
            with _no_legacy_delete(client, backend):
                assert await run_target_operation_async(
                    client, lambda: database.delete_container(target, response_hook=Hook(), timeout=30)
                ) is None
                assert "x-test-mutation" not in client.client_connection.last_response_headers
                with pytest.raises(exceptions.CosmosResourceNotFoundError):
                    await run_target_operation_async(client, lambda: database.delete_container(target, timeout=30))

    asyncio.run(async_call()) if mode == "async" else sync_call()
    assert calls == [None]
    with pytest.raises(exceptions.CosmosResourceNotFoundError):
        owned_database.get_container_client(name).read()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("condition", ["stale_etag", "if_missing"])
def test_conditional_delete_matches_legacy_service_behavior(owned_database, mode, condition):
    options = (
        {"etag": '"deliberately-stale"', "match_condition": MatchConditions.IfNotModified}
        if condition == "stale_etag" else {"match_condition": MatchConditions.IfMissing}
    )
    outcomes = {}
    for backend in ("core-python", "rust"):
        name = "conditional_" + uuid.uuid4().hex
        owned_database.create_container(name, PartitionKey(path="/id"))

        def sync_call():
            with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend) as client:
                database = client.get_database_client(owned_database.id)
                with _no_legacy_delete(client, backend):
                    return run_target_operation(client, lambda: database.delete_container(name, timeout=30, **options))

        async def async_call():
            async with AsyncCosmosClient(
                os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend
            ) as client:
                database = client.get_database_client(owned_database.id)
                with _no_legacy_delete(client, backend):
                    return await run_target_operation_async(
                        client, lambda: database.delete_container(name, timeout=30, **options)
                    )

        try:
            result = asyncio.run(async_call()) if mode == "async" else sync_call()
        except exceptions.CosmosHttpResponseError as error:
            assert error.status_code == 412
            assert owned_database.get_container_client(name).read()["id"] == name
            outcomes[backend] = "412, container retained"
        else:
            assert result is None
            with pytest.raises(exceptions.CosmosResourceNotFoundError):
                owned_database.get_container_client(name).read()
            outcomes[backend] = "204, container deleted"
    assert outcomes["rust"] == outcomes["core-python"]
    print("{} {}: {}".format(mode, condition, outcomes["rust"]))


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("warm", [False, True])
def test_rust_delete_after_metadata_resolution(owned_database, mode, warm):
    name = "resolution_" + uuid.uuid4().hex
    if warm:
        owned_database.create_container(name, PartitionKey(path="/id"))
    hooks = []

    def hook(headers, body):
        hooks.append(body)

    def sync_call():
        with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
            database = client.get_database_client(owned_database.id)
            if warm:
                # An item operation resolves this container in the same Rust driver.
                item = database.get_container_client(name).create_item({"id": "warm", "value": 42})
                assert item["id"] == "warm" and item["value"] == 42
            with _no_legacy_delete(client, "rust"):
                return run_target_operation(
                    client, lambda: database.delete_container(name, response_hook=hook, timeout=30)
                )

    async def async_call():
        async with AsyncCosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust"
        ) as client:
            database = client.get_database_client(owned_database.id)
            if warm:
                item = await database.get_container_client(name).create_item({"id": "warm", "value": 42})
                assert item["id"] == "warm" and item["value"] == 42
            with _no_legacy_delete(client, "rust"):
                return await run_target_operation_async(
                    client, lambda: database.delete_container(name, response_hook=hook, timeout=30)
                )

    def call():
        return asyncio.run(async_call()) if mode == "async" else sync_call()

    if warm:
        assert call() is None
        assert hooks == [None]
    else:
        with pytest.raises(exceptions.CosmosResourceNotFoundError):
            call()
        assert hooks == []
    with pytest.raises(exceptions.CosmosResourceNotFoundError):
        owned_database.get_container_client(name).read()
