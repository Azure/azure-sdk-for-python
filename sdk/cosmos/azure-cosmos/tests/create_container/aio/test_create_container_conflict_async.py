# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Async ``create_container`` on Rust reports a taken container id as a typed 409 conflict."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust_async

pytestmark = [pytest.mark.asyncio]


@pytest.fixture(scope="module")
def database_id():
    """A throwaway database, deleted after the module along with everything created in it."""
    name = "rust_create_container_conflict_a_" + uuid.uuid4().hex[:8]
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        try:
            client.create_database(id=name)
            yield name
        finally:
            try:
                client.delete_database(name)
            except exceptions.CosmosResourceNotFoundError:
                pass


async def test_create_existing_container_raises_conflict_async_rust(database_id):
    """Creating a container whose id is already taken raises CosmosResourceExistsError with status 409."""
    taken_id = "already_taken_" + uuid.uuid4().hex[:8]
    async with AsyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.get_database_client(database_id)
        await database.create_container(id=taken_id, partition_key=PartitionKey(path="/pk", kind="Hash"))

        with pytest.raises(exceptions.CosmosResourceExistsError) as raised:
            await run_on_rust_async(client, lambda: database.create_container(
                id=taken_id, partition_key=PartitionKey(path="/pk", kind="Hash")
            ))

    assert raised.value.status_code == 409
