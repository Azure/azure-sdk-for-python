# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test.
"""

import json
import os.path
import time
import unittest
import urllib.parse as urllib
import uuid

import pytest
import requests
from azure.core import MatchConditions
from azure.core.exceptions import AzureError, ServiceResponseError
from azure.core.pipeline.transport import RequestsTransport, RequestsTransportResponse
from urllib3.util.retry import Retry

import azure.cosmos._base as base
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import _retry_utility
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.partition_key import PartitionKey


class TimeoutTransport(RequestsTransport):

    def __init__(self, response):
        self._response = response
        super(TimeoutTransport, self).__init__()

    def send(self, *args, **kwargs):
        if kwargs.pop("passthrough", False):
            return super(TimeoutTransport, self).send(*args, **kwargs)

        time.sleep(5)
        if isinstance(self._response, Exception):
            raise self._response
        output = requests.Response()
        output.status_code = self._response
        response = RequestsTransportResponse(None, output)
        return response


@pytest.mark.cosmosLong
class TestCRUDDatabaseOperations(unittest.TestCase):
    """Python CRUD Tests.
    """

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []
    client: cosmos_client.CosmosClient = None

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            self.assertEqual(inst.status_code, status_code)

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.databaseForTest = cls.client.get_database_client(cls.configs.TEST_DATABASE_ID)

    def test_database_crud(self):
        database_id = str(uuid.uuid4())
        created_db = self.client.create_database(database_id)
        self.assertEqual(created_db.id, database_id)
        # Read databases after creation.
        databases = list(self.client.query_databases({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [
                {'name': '@id', 'value': database_id}
            ]
        }))
        self.assertTrue(databases, 'number of results for the query should be > 0')

        # read database.
        self.client.get_database_client(created_db.id).read()

        # delete database.
        self.client.delete_database(created_db.id)
        # read database after deletion
        read_db = self.client.get_database_client(created_db.id)
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           read_db.read)

        database_proxy = self.client.create_database_if_not_exists(id=database_id, offer_throughput=5000)
        self.assertEqual(database_id, database_proxy.id)
        self.assertEqual(5000, database_proxy.read_offer().offer_throughput)

        database_proxy = self.client.create_database_if_not_exists(id=database_id, offer_throughput=6000)
        self.assertEqual(database_id, database_proxy.id)
        self.assertEqual(5000, database_proxy.read_offer().offer_throughput)

        self.client.delete_database(database_id)

    def test_database_level_offer_throughput(self):
        # Create a database with throughput
        offer_throughput = 1000
        database_id = str(uuid.uuid4())
        created_db = self.client.create_database(
            id=database_id,
            offer_throughput=offer_throughput
        )
        self.assertEqual(created_db.id, database_id)

        # Verify offer throughput for database
        offer = created_db.read_offer()
        self.assertEqual(offer.offer_throughput, offer_throughput)

        # Update database offer throughput
        new_offer_throughput = 2000
        offer = created_db.replace_throughput(new_offer_throughput)
        self.assertEqual(offer.offer_throughput, new_offer_throughput)
        self.client.delete_database(created_db.id)

    def test_sql_query_crud(self):
        # create two databases.
        db1 = self.client.create_database('database 1' + str(uuid.uuid4()))
        db2 = self.client.create_database('database 2' + str(uuid.uuid4()))

        # query with parameters.
        databases = list(self.client.query_databases({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [
                {'name': '@id', 'value': db1.id}
            ]
        }))
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')

        # query without parameters.
        databases = list(self.client.query_databases({
            'query': 'SELECT * FROM root r WHERE r.id="database non-existing"'
        }))
        self.assertEqual(0, len(databases), 'Unexpected number of query results.')

        # query with a string.
        databases = list(self.client.query_databases('SELECT * FROM root r WHERE r.id="' + db2.id + '"'))  # nosec
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')
        self.client.delete_database(db1.id)
        self.client.delete_database(db2.id)

    def test_database_account_functionality(self):
        # Validate database account functionality.
        database_account = self.client.get_database_account()
        self.assertEqual(database_account.DatabasesLink, '/dbs/')
        self.assertEqual(database_account.MediaLink, '/media/')
        if (HttpHeaders.MaxMediaStorageUsageInMB in
                self.client.client_connection.last_response_headers):
            self.assertEqual(
                database_account.MaxMediaStorageUsageInMB,
                self.client.client_connection.last_response_headers[
                    HttpHeaders.MaxMediaStorageUsageInMB])
        if (HttpHeaders.CurrentMediaStorageUsageInMB in
                self.client.client_connection.last_response_headers):
            self.assertEqual(
                database_account.CurrentMediaStorageUsageInMB,
                self.client.client_connection.last_response_headers[
                    HttpHeaders.CurrentMediaStorageUsageInMB])
        self.assertIsNotNone(database_account.ConsistencyPolicy['defaultConsistencyLevel'])

    def test_id_validation(self):
        # Id shouldn't end with space.
        try:
            self.client.create_database(id='id_with_space ')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id ends with a space or newline.', e.args[0])
        # Id shouldn't contain '/'.

        try:
            self.client.create_database(id='id_with_illegal/_char')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])
        # Id shouldn't contain '\\'.

        try:
            self.client.create_database(id='id_with_illegal\\_char')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])
        # Id shouldn't contain '?'.

        try:
            self.client.create_database(id='id_with_illegal?_char')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])
        # Id shouldn't contain '#'.

        try:
            self.client.create_database(id='id_with_illegal#_char')
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual('Id contains illegal chars.', e.args[0])

        # Id can begin with space
        db = self.client.create_database(id=' id_begin_space' + str(uuid.uuid4()))
        self.assertTrue(True)

        self.client.delete_database(db.id)



if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True:  # raised by sys.exit(True) when tests failed
            raise