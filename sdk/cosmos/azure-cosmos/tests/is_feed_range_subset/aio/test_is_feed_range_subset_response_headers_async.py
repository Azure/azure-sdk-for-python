# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Async ``is_feed_range_subset`` on Rust is a local check that leaves the last response headers alone."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient as SyncCosmosClient
from azure.cosmos import PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range

pytestmark = [pytest.mark.asyncio]


def _feed_range(range_min, range_max, is_min_inclusive=True, is_max_inclusive=False):
    """Build a public feed-range dict from explicit EPK bounds."""
    return FeedRangeInternalEpk(Range(range_min, range_max, is_min_inclusive, is_max_inclusive)).to_dict()


@pytest.fixture(scope="module")
def container_ids():
    database_id = "rust_is_feed_range_subset_a_" + uuid.uuid4().hex[:8]
    with SyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        try:
            database = client.create_database(database_id)
            database.create_container(id="ranges", partition_key=PartitionKey(path="/id"))
            yield database_id, "ranges"
        finally:
            try:
                client.delete_database(database_id)
            except exceptions.CosmosResourceNotFoundError:
                pass


async def test_is_feed_range_subset_leaves_last_response_headers_untouched_async_rust(container_ids):
    """The subset check makes no service call, so the previous operation's response headers stay as they were."""
    database_id, container_id = container_ids
    async with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        container = client.get_database_client(database_id).get_container_client(container_id)
        await container.upsert_item({"id": "warmup-" + uuid.uuid4().hex})
        before = dict(client.client_connection.last_response_headers or {})
        assert before, "warm-up did not populate last_response_headers"

        assert await container.is_feed_range_subset(_feed_range("", "FF"), _feed_range("3F", "7F")) is True

        after = dict(client.client_connection.last_response_headers or {})
    assert after == before
