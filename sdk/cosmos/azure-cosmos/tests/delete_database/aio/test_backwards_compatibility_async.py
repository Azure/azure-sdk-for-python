# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retain the async database-deletion part of the legacy ETag compatibility sweep."""

import unittest
import uuid

import pytest

from azure.core import MatchConditions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from common.throughput_fixtures import owned_database_async
from config.settings import TestSettings, unique_database_id


@pytest.mark.cosmosEmulator
class TestBackwardsCompatibilityAsync(unittest.IsolatedAsyncioTestCase):
    async def test_delete_database_etag_match_condition_compatibility_async_rust(self):
        # Source: tests/test_backwards_compatibility_async.py::TestBackwardsCompatibilityAsync.test_etag_match_condition_compatibility_async
        async with CosmosClient(TestSettings.host, TestSettings.masterKey, _backend="rust") as client:
            # Creation omits the removed options so the original delete and 404 checks still run.
            async with owned_database_async(client, unique_database_id("delete-backcompat")) as database:
                assert database is not None
                await client.delete_database(
                    database.id, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified
                )
                try:
                    await database.read()
                    pytest.fail("Database read should have failed")
                except CosmosHttpResponseError as error:
                    assert error.status_code == 404
