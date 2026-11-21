# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Concurrent callers using real service responses, with a forced read/create race."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos._helpers._container_operations import ContainerHelper
from azure.cosmos.aio._helpers._container_operations import AsyncContainerHelper
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from config.clients import create_data_client, create_data_client_async
from config.settings import TestSettings, unique_database_id


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
@pytest.mark.skipif(
    TestSettings.is_emulator,
    reason=(
        "emulator-gap: concurrent creates race while reserving an internal server; "
        "ServiceStateManager.SetServiceStateTransactionallyAsync fails with "
        "'The property check failed' (0x80071BD5) and returns HTTP 500. "
        "Reproduced without either SDK; re-enable after the emulator allocation race is fixed."
    ),
)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("use_legacy", [False, True], ids=["rust", "core-python"])
def test_concurrent_container_creation_returns_same_resource_rust(asynchronous, use_legacy):
    database_id = unique_database_id("ContainerRace")
    backend = "core-python" if use_legacy else "rust"

    def options(hooks):
        def hook(headers, properties):
            hooks.append((dict(headers), dict(properties)))
        return dict(return_properties=True, response_hook=hook, timeout=30)

    def verify(result, hooks):
        proxy, properties = result
        assert proxy.id == properties["id"] == "orders"
        assert properties["partitionKey"]["paths"] == ["/pk"]
        assert len(hooks) == 1
        assert hooks[0][1]["_rid"] == properties["_rid"]
        assert hooks[0][0]["x-ms-activity-id"] == properties.get_response_headers()["x-ms-activity-id"]
        return properties["_rid"]

    async def run_async():
        gate = asyncio.Event()
        missing_reads = 0
        original_read = AsyncContainerHelper.read_container

        async def read_then_wait(helper, *args, **kwargs):
            nonlocal missing_reads
            try:
                return await original_read(helper, *args, **kwargs)
            except CosmosResourceNotFoundError:
                missing_reads += 1
                if missing_reads == 8:
                    gate.set()
                await asyncio.wait_for(gate.wait(), 15)
                raise

        async with create_data_client_async(_backend=backend) as client:
            database = await client.create_database(database_id)
            try:
                async def create():
                    hooks = []
                    result = await database.create_container_if_not_exists(
                        "orders", PartitionKey(path="/pk"), **options(hooks)
                    )
                    return verify(result, hooks)

                with patch.object(AsyncContainerHelper, "read_container", read_then_wait):
                    results = await asyncio.gather(*[create() for _ in range(8)], return_exceptions=True)
                assert missing_reads == 8
                assert all(isinstance(result, str) for result in results), results
                assert len(set(results)) == 1
            finally:
                await client.delete_database(database_id)

    if asynchronous:
        asyncio.run(run_async())
        return

    gate = Barrier(8)
    original_read = ContainerHelper.read_container

    def read_then_wait(helper, *args, **kwargs):
        try:
            return original_read(helper, *args, **kwargs)
        except CosmosResourceNotFoundError:
            gate.wait(timeout=15)
            raise

    with create_data_client(_backend=backend) as client:
        database = client.create_database(database_id)
        try:
            def create():
                hooks = []
                result = database.create_container_if_not_exists(
                    "orders", PartitionKey(path="/pk"), **options(hooks)
                )
                return verify(result, hooks)

            with patch.object(ContainerHelper, "read_container", read_then_wait):
                with ThreadPoolExecutor(max_workers=8) as pool:
                    results = list(pool.map(lambda _: create(), range(8)))
            assert len(set(results)) == 1
        finally:
            client.delete_database(database_id)
