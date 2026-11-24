# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Concurrent callers using real service responses, with a forced read/create race."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextvars import ContextVar
from threading import Barrier
from unittest.mock import patch

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos._helpers._container_operations import ContainerHelper
from azure.cosmos.aio._helpers._container_operations import AsyncContainerHelper
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from config.clients import create_data_client, create_data_client_async
from config.settings import unique_database_id


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_concurrent_container_creation_returns_same_resource_rust(asynchronous):
    database_id = unique_database_id("ContainerRace")
    initial_read = ContextVar("initial_read", default=False)

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
            is_initial_read = initial_read.get()
            initial_read.set(False)
            try:
                return await original_read(helper, *args, **kwargs)
            except CosmosResourceNotFoundError:
                if is_initial_read:
                    missing_reads += 1
                    if missing_reads == 8:
                        gate.set()
                    await asyncio.wait_for(gate.wait(), 15)
                raise

        async with create_data_client_async(_backend="rust") as client:
            database = await client.create_database(database_id)
            try:
                async def create():
                    hooks = []
                    initial_read.set(True)
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
        is_initial_read = initial_read.get()
        initial_read.set(False)
        try:
            return original_read(helper, *args, **kwargs)
        except CosmosResourceNotFoundError:
            if is_initial_read:
                gate.wait(timeout=15)
            raise

    with create_data_client(_backend="rust") as client:
        database = client.create_database(database_id)
        try:
            def create():
                hooks = []
                initial_read.set(True)
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
