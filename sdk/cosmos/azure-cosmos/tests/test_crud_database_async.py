# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test.
"""
import json
import logging
import os.path
import time
import unittest
import urllib.parse as urllib
import uuid

import pytest
import requests
from azure.core import MatchConditions
from azure.core.exceptions import AzureError, ServiceResponseError
from azure.core.pipeline.transport import AsyncioRequestsTransport, AsyncioRequestsTransportResponse

import azure.cosmos._base as base
import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos.aio import CosmosClient, _retry_utility_async, DatabaseProxy
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.partition_key import PartitionKey


class TimeoutTransport(AsyncioRequestsTransport):

    def __init__(self, response):
        self._response = response
        super(TimeoutTransport, self).__init__()

    async def send(self, *args, **kwargs):
        if kwargs.pop("passthrough", False):
            return super(TimeoutTransport, self).send(*args, **kwargs)

        time.sleep(5)
        if isinstance(self._response, Exception):
            raise self._response
        current_response = await self._response
        output = requests.Response()
        output.status_code = current_response
        response = AsyncioRequestsTransportResponse(None, output)
        return response


@pytest.mark.cosmosLong
class TestCRUDDatabaseOperationsAsync(unittest.IsolatedAsyncioTestCase):
    """Python CRUD Tests.
    """
    client: CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []
    database_for_test: DatabaseProxy = None

    async def __assert_http_failure_with_status(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            await func(*args, **kwargs)
            self.fail('function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            assert inst.status_code == status_code

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.database_for_test = self.client.get_database_client(self.configs.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_database_crud_async(self):
        database_id = str(uuid.uuid4())
        created_db = await self.client.create_database(database_id)
        assert created_db.id == database_id
        # query databases.
        databases = [database async for database in self.client.query_databases(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': database_id}
            ]
        )]

        assert len(databases) > 0

        # read database.
        self.client.get_database_client(created_db.id)
        await created_db.read()

        # delete database.
        await self.client.delete_database(created_db.id)
        # read database after deletion
        read_db = self.client.get_database_client(created_db.id)
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND, read_db.read)

        database_proxy = await self.client.create_database_if_not_exists(id=database_id, offer_throughput=5000)
        assert database_id == database_proxy.id
        db_throughput = await database_proxy.get_throughput()
        assert 5000 == db_throughput.offer_throughput

        database_proxy = await self.client.create_database_if_not_exists(id=database_id, offer_throughput=6000)
        assert database_id == database_proxy.id
        db_throughput = await database_proxy.get_throughput()
        assert 5000 == db_throughput.offer_throughput

        # delete database.
        await self.client.delete_database(database_id)

    async def test_database_level_offer_throughput_async(self):
        # Create a database with throughput
        offer_throughput = 1000
        database_id = str(uuid.uuid4())
        created_db = await self.client.create_database(
            id=database_id,
            offer_throughput=offer_throughput
        )
        assert created_db.id == database_id

        # Verify offer throughput for database
        offer = await created_db.get_throughput()
        assert offer.offer_throughput == offer_throughput

        # Update database offer throughput
        new_offer_throughput = 2000
        offer = await created_db.replace_throughput(new_offer_throughput)
        assert offer.offer_throughput == new_offer_throughput

        await self.client.delete_database(database_id)

    async def test_sql_query_crud_async(self):
        # create two databases.
        db1 = await self.client.create_database('database 1' + str(uuid.uuid4()))
        db2 = await self.client.create_database('database 2' + str(uuid.uuid4()))

        # query with parameters.
        databases = [database async for database in self.client.query_databases(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': db1.id}
            ]
        )]
        assert 1 == len(databases)

        # query without parameters.
        databases = [database async for database in self.client.query_databases(
            query='SELECT * FROM root r WHERE r.id="database non-existing"'
        )]
        assert 0 == len(databases)

        # query with a string.
        query_string = 'SELECT * FROM root r WHERE r.id="' + db2.id + '"'
        databases = [database async for database in
                     self.client.query_databases(query=query_string)]
        assert 1 == len(databases)

        await self.client.delete_database(db1.id)
        await self.client.delete_database(db2.id)

    async def test_database_account_functionality_async(self):
        # Validate database account functionality.
        database_account = await self.client._get_database_account()
        assert database_account.DatabasesLink == '/dbs/'
        assert database_account.MediaLink == '/media/'
        if (HttpHeaders.MaxMediaStorageUsageInMB in
                self.client.client_connection.last_response_headers):
            assert database_account.MaxMediaStorageUsageInMB == self.client.client_connection.last_response_headers[
                HttpHeaders.MaxMediaStorageUsageInMB]
        if (HttpHeaders.CurrentMediaStorageUsageInMB in
                self.client.client_connection.last_response_headers):
            assert database_account.CurrentMediaStorageUsageInMB == self.client.client_connection.last_response_headers[
                HttpHeaders.CurrentMediaStorageUsageInMB]
        assert database_account.ConsistencyPolicy['defaultConsistencyLevel'] is not None



if __name__ == '__main__':
    unittest.main()
