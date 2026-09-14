# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import inspect
import os
import uuid
from contextlib import AsyncExitStack, ExitStack, asynccontextmanager
from unittest.mock import MagicMock, patch

import pytest
from azure.core import MatchConditions
from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.partition_key import PartitionKey
from common._parity_helpers import (
    run_target_operation, run_target_operation_async,
    skip_unless_emulator, skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding(), pytest.mark.asyncio]
PK = PartitionKey(path="/pk")


@pytest.fixture(scope="module")
def owned_database():
    name = "parity_replace_" + uuid.uuid4().hex
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python") as admin:
        try:
            yield admin.create_database(name)
        finally:
            try:
                admin.delete_database(name)
            except exceptions.CosmosResourceNotFoundError:
                pass


@asynccontextmanager
async def replacement_client(database_id, mode, backend):
    async with AsyncExitStack() as stack:
        arguments = (os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
        if mode == "async":
            client = await stack.enter_async_context(AsyncCosmosClient(*arguments, _backend=backend))
        else:
            client = stack.enter_context(CosmosClient(*arguments, _backend=backend))
        database = client.get_database_client(database_id)

        async def replace(target, **kwargs):
            with ExitStack() as guards:
                if backend == "rust":
                    for method in ("ReplaceContainer", "ReadContainer"):
                        guards.enter_context(patch.object(
                            client.client_connection, method,
                            side_effect=AssertionError("Rust replacement entered legacy " + method),
                        ))
                if mode == "async":
                    return await run_target_operation_async(
                        client, lambda: database.replace_container(target, PK, **kwargs),
                    )
                return run_target_operation(client, lambda: database.replace_container(target, PK, **kwargs))

        yield client, database, replace


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("target_kind", ["name", "mapping", "proxy"])
async def test_replace_properties_and_keep_items(owned_database, mode, backend, target_kind):
    name = "properties_" + uuid.uuid4().hex
    original = owned_database.create_container(
        name, PK, indexing_policy={"indexingMode": "none"},
    )
    original.create_item({"id": "kept", "pk": "p", "value": 42})
    snapshots = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, body):
            assert headers["x-ms-activity-id"]
            assert float(headers["x-ms-request-charge"]) > 0
            assert body["id"] == name and body["defaultTtl"] == 3600
            if backend == "rust":
                assert headers["x-ms-cosmos-sdk-diagnostics"]
            snapshots.append(dict(headers))
            headers["etag"] = "changed"
            body["id"] = "wrong"
            body["indexingPolicy"]["indexingMode"] = "none"

    async with replacement_client(owned_database.id, mode, backend) as (client, database, replace):
        target = ({"id": name, "indexingPolicy": {"indexingMode": "none"}} if target_kind == "mapping"
                  else database.get_container_client(name) if target_kind == "proxy" else name)
        proxy, properties = await replace(
            target, default_ttl=3600, return_properties=True, response_hook=Hook(),
            timeout=30, read_timeout=None, initial_headers={"x-company-trace": "replacement"},
        )
        assert proxy.id == name and properties["id"] == name
        assert properties["indexingPolicy"]["indexingMode"] == "consistent"
        assert properties.get_response_headers()["etag"] != "changed"
        assert client.client_connection.last_response_headers["etag"] != "changed"
        stored = original.read()
        assert stored["defaultTtl"] == 3600 and stored["indexingPolicy"]["indexingMode"] == "consistent"
        proxy = await replace(name, default_ttl=None, timeout=30)
        assert proxy.id == name and not isinstance(proxy, tuple)
        assert "defaultTtl" not in original.read()
    assert len(snapshots) == 1
    assert original.read_item("kept", partition_key="p")["value"] == 42


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("warm", [False, True])
async def test_conditions_with_cold_and_warm_metadata(owned_database, mode, backend, warm):
    name = "conditional_" + uuid.uuid4().hex
    original = owned_database.create_container(name, PK, default_ttl=60)
    hook = MagicMock()
    async with replacement_client(owned_database.id, mode, backend) as (_, database, replace):
        if warm:
            result = database.get_container_client(name).create_item({"id": "warm", "pk": "p"})
            if inspect.isawaitable(result):
                result = await result
            assert result["id"] == "warm"
        with pytest.raises(exceptions.CosmosHttpResponseError) as raised:
            await replace(
                name, default_ttl=3600, etag='"stale"', match_condition=MatchConditions.IfNotModified,
                response_hook=hook, timeout=30,
            )
        assert raised.value.status_code == 412
        hook.assert_not_called()
        current = original.read()
        assert current["defaultTtl"] == 60
        _, properties = await replace(
            name, default_ttl=3600, etag=current["_etag"], match_condition=MatchConditions.IfNotModified,
            return_properties=True, response_hook=hook, timeout=30,
        )
        assert properties["defaultTtl"] == 3600
        hook.assert_called_once()
    assert original.read()["defaultTtl"] == 3600


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("backend", ["core-python", "rust"])
async def test_missing_container_does_not_invoke_success_hook(owned_database, mode, backend):
    hook = MagicMock()
    async with replacement_client(owned_database.id, mode, backend) as (_, _, replace):
        with pytest.raises(exceptions.CosmosResourceNotFoundError):
            await replace("missing_" + uuid.uuid4().hex, response_hook=hook, timeout=30)
    hook.assert_not_called()
