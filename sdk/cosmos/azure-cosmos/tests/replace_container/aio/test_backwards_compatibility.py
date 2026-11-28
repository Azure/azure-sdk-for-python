# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async replacement-only assertions from main's multi-API compatibility tests."""

import uuid
from unittest.mock import patch

import pytest
from azure.core import MatchConditions
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from replace_container._container_setup import AsyncReplacementCase


@pytest.mark.cosmosEmulator
class TestBackwardsCompatibilityAsync(AsyncReplacementCase):
    def _create_key_client(self):
        return CosmosClient(self.host, self.key, _backend="rust")

    async def test_session_token_compatibility_async_rust(self):
        # Source: tests/test_backwards_compatibility_async.py::TestBackwardsCompatibilityAsync.test_session_token_compatibility_async
        # Contract change: an ignored session_token is now rejected, including None.
        database = self.client.get_database_client(self.database_id)
        with patch.object(getattr(self.client.client_connection, "_backend"), "execute") as execute:
            for token in (None, str(uuid.uuid4())):
                with pytest.raises(TypeError, match="session_token"):
                    await database.replace_container("orders", PartitionKey(path="/pk"), session_token=token)
            execute.assert_not_called()

    async def test_etag_match_condition_compatibility_async_rust(self):
        # Source: tests/test_backwards_compatibility_async.py::TestBackwardsCompatibilityAsync.test_etag_match_condition_compatibility_async
        self.created_database = self.key_db
        container2 = await self.key_db.create_container(str(uuid.uuid4()), PartitionKey(path="/pk"))
        container2_read = await container2.read()
        assert container2_read is not None
        replace_container = await self.created_database.replace_container(container2, PartitionKey(path="/pk"), default_ttl=30,
                                                             etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        replace_container_read = await replace_container.read()
        assert replace_container is not None
        assert replace_container_read != container2_read
        assert 'defaultTtl' in replace_container_read
