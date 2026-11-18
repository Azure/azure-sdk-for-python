# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Async database ``replace_throughput`` on Rust reports the new shared throughput faithfully."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from common._rust_checks import run_on_rust_async
from common.throughput_fixtures import owned_database

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def database_id():
    """A database with 1000 RU/s of shared throughput, deleted after the test."""
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        with owned_database(client, "rust_repl_db_a_" + uuid.uuid4().hex, offer_throughput=1000) as database:
            yield database.id


async def test_replace_database_throughput_hook_cannot_change_result_async_rust(database_id):
    """The hook runs once; editing its headers or offer body changes neither the returned nor stored 2000 RU/s."""
    calls = []

    def hook(headers, offer):
        calls.append(offer["content"]["offerThroughput"])
        headers.clear()
        offer["content"]["offerThroughput"] = 999

    async with AsyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.get_database_client(database_id)
        updated = await run_on_rust_async(client, lambda: database.replace_throughput(2000, response_hook=hook))

        assert calls == [2000]
        assert updated.offer_throughput == 2000
        assert updated.properties["content"]["offerThroughput"] == 2000
        assert updated.get_response_headers()
        assert (await database.get_throughput()).offer_throughput == 2000
