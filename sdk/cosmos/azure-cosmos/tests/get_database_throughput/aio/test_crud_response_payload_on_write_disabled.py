# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async database CRUD and throughput checks with write responses disabled."""

import os
import unittest
import uuid

import pytest

from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.cosmos.http_constants import StatusCodes
from config import settings


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

    @pytest.mark.cosmosLong
    @pytest.mark.cosmosAADLong
    async def test_database_crud_async_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_database_crud_async
        database_id = settings.unique_database_id()
        self.database_id = database_id
        created_db = await self.key_client.create_database(database_id)
        assert created_db.id == database_id
        databases = [
            database
            async for database in self.key_client.query_databases(
                query="SELECT * FROM root r WHERE r.id=@id", parameters=[{"name": "@id", "value": database_id}]
            )
        ]
        assert len(databases) > 0
        self.key_client.get_database_client(created_db.id)
        await created_db.read()
        await self.key_client.delete_database(created_db.id)
        read_db = self.key_client.get_database_client(created_db.id)
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND, read_db.read)
        database_proxy = await self.key_client.create_database_if_not_exists(id=database_id, offer_throughput=5000)
        assert database_id == database_proxy.id
        db_throughput = await database_proxy.get_throughput()
        assert 5000 == db_throughput.offer_throughput
        database_proxy = await self.key_client.create_database_if_not_exists(id=database_id, offer_throughput=6000)
        assert database_id == database_proxy.id
        db_throughput = await database_proxy.get_throughput()
        assert 5000 == db_throughput.offer_throughput

        await self.key_client.delete_database(database_id)

    async def __assert_http_failure_with_status(self, status_code, func, *args, **kwargs):
        try:
            await func(*args, **kwargs)
            self.fail("function should fail.")
        except exceptions.CosmosHttpResponseError as inst:
            assert inst.status_code == status_code

    @pytest.mark.cosmosEmulator
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
