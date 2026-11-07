# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Async conditional ``delete_container`` on Rust keeps the service's precondition behavior."""
import os
import uuid
from unittest.mock import patch

import pytest
from azure.core import MatchConditions

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust_async

pytestmark = [pytest.mark.asyncio]


@pytest.fixture(scope="module")
def owned_database():
    name = "rust_delete_container_cond_a_" + uuid.uuid4().hex
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as admin:
        try:
            yield admin.create_database(name)
        finally:
            try:
                admin.delete_database(name)
            except exceptions.CosmosResourceNotFoundError:
                pass


async def _delete(database_id, name, **options):
    async with AsyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.get_database_client(database_id)
        with patch.object(client.client_connection, "DeleteContainer",
                          side_effect=AssertionError("Rust deletion used legacy Python")):
            return await run_on_rust_async(
                client, lambda: database.delete_container(name, timeout=30, **options)
            )


async def test_delete_container_with_stale_etag_raises_precondition_failed_async_rust(owned_database):
    """A delete with a stale If-Match etag fails with 412 and leaves the container in place."""
    name = "conditional_" + uuid.uuid4().hex
    owned_database.create_container(name, PartitionKey(path="/id"))

    with pytest.raises(exceptions.CosmosHttpResponseError) as raised:
        await _delete(
            owned_database.id, name, etag='"deliberately-stale"', match_condition=MatchConditions.IfNotModified
        )

    assert raised.value.status_code == 412
    assert owned_database.get_container_client(name).read()["id"] == name


async def test_delete_container_with_if_missing_deletes_container_async_rust(owned_database):
    """A delete with IfMissing succeeds (204) and removes the container."""
    name = "conditional_" + uuid.uuid4().hex
    owned_database.create_container(name, PartitionKey(path="/id"))

    assert await _delete(owned_database.id, name, match_condition=MatchConditions.IfMissing) is None

    with pytest.raises(exceptions.CosmosResourceNotFoundError):
        owned_database.get_container_client(name).read()
