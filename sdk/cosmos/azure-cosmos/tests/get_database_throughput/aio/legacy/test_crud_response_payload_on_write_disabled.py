# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async throughput assertions with write responses disabled."""

import os
import unittest
import uuid

import pytest

from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError


@pytest.mark.cosmosEmulator
class TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.key_client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust", no_response_on_write=True,
        )
        self.database_id = "get_db_noresponse_a_" + uuid.uuid4().hex
        self.addAsyncCleanup(self.key_client.close)
        self.addAsyncCleanup(self._delete_database)

    async def _delete_database(self):
        try:
            await self.key_client.delete_database(self.database_id)
        except CosmosResourceNotFoundError:
            pass

    async def test_database_crud_async_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_database_crud_async
        database_id = self.database_id
        database_proxy = await self.key_client.create_database_if_not_exists(id=database_id, offer_throughput=5000)
        assert database_id == database_proxy.id
        db_throughput = await database_proxy.get_throughput()
        assert 5000 == db_throughput.offer_throughput
        database_proxy = await self.key_client.create_database_if_not_exists(id=database_id, offer_throughput=6000)
        assert database_id == database_proxy.id
        db_throughput = await database_proxy.get_throughput()
        assert 5000 == db_throughput.offer_throughput

    async def test_database_level_offer_throughput_async_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_database_level_offer_throughput_async
        offer_throughput = 1000
        database_id = self.database_id
        created_db = await self.key_client.create_database(id=database_id, offer_throughput=offer_throughput)
        assert created_db.id == database_id
        offer = await created_db.get_throughput()
        assert offer.offer_throughput == offer_throughput
        new_offer_throughput = 2000
        offer = await created_db.replace_throughput(new_offer_throughput)
        assert offer.offer_throughput == new_offer_throughput
