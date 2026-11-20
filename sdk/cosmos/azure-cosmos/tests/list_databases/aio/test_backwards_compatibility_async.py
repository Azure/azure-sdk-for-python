# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async listing assertions adapted from the legacy session-token compatibility test."""

import unittest
import uuid

import pytest

from config import settings
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError


@pytest.mark.cosmosEmulator
class TestBackwardsCompatibilityAsync(unittest.IsolatedAsyncioTestCase):
    configs = settings.TestSettings

    async def asyncSetUp(self):
        self.client = CosmosClient(
            self.configs.host,
            self.configs.masterKey,
            _backend="rust",
        )
        self.addAsyncCleanup(self.client.close)

    async def _delete_test_database(self, database_id):
        try:
            await self.client.delete_database(database_id)
        except CosmosHttpResponseError as error:
            if error.status_code != 404:
                raise

    async def test_list_databases_session_token_compatibility_async_rust(self):
        """Reject the removed listing option and still list this test's database."""
        # Source: tests/test_backwards_compatibility_async.py::TestBackwardsCompatibilityAsync.test_session_token_compatibility_async
        database = await self.client.create_database(settings.unique_database_id("backcompat-list"))
        self.addAsyncCleanup(self._delete_test_database, database.id)
        for token in (str(uuid.uuid4()), None):
            with self.subTest(session_token=token):
                with pytest.raises(
                    TypeError, match=r"list_databases\(\) does not support the 'session_token' option"
                ):
                    self.client.list_databases(session_token=token)
        database_ids = {db["id"] async for db in self.client.list_databases()}
        assert database.id in database_ids
