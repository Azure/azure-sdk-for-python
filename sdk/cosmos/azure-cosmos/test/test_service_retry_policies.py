# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import test_config
from azure.cosmos import CosmosClient, PartitionKey, _retry_utility
from azure.core.exceptions import ServiceRequestError, ServiceResponseError

from azure.cosmos._location_cache import RegionalEndpoint


@pytest.mark.cosmosEmulator
class TestServiceRetryPolicies(unittest.TestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = "test_service_retries_db" + str(uuid.uuid4())
    TEST_CONTAINER_ID = "test_service_retries_container" + str(uuid.uuid4())
    REGION1 = "West US"
    REGION2 = "East US"
    REGION3 = "West US 2"
    REGIONAL_ENDPOINT = RegionalEndpoint(host, host)

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.created_database = cls.client.create_database_if_not_exists(cls.TEST_DATABASE_ID)
        cls.created_container = cls.created_database.create_container_if_not_exists(cls.TEST_CONTAINER_ID,
                                                                                    PartitionKey(path="/id"))

    def test_service_request_retry(self):
        mock_client = CosmosClient(self.host, self.masterKey)
        db = mock_client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_ID)

        created_item = container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
        # Save the original function
        self.original_execute_function = _retry_utility.ExecuteFunction

        # Change the location cache to have 3 preferred read regions and 3 available read endpoints by location
        original_location_cache = mock_client.client_connection._global_endpoint_manager.location_cache
        original_location_cache.available_read_locations = [self.REGION1, self.REGION2, self.REGION3]
        original_location_cache.available_read_regional_endpoints_by_locations = {self.REGION1: self.REGIONAL_ENDPOINT,
                                                                                  self.REGION2: self.REGIONAL_ENDPOINT,
                                                                                  self.REGION3: self.REGIONAL_ENDPOINT}
        original_location_cache.read_regional_endpoints = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT,
                                                           self.REGIONAL_ENDPOINT]
        try:
            # Mock the function to return the ServiceRequestException we retry
            mf = self.MockExecuteServiceRequestException()
            _retry_utility.ExecuteFunction = mf
            container.read_item(created_item['id'], created_item['pk'])
            pytest.fail("Exception was not raised.")
        except ServiceRequestError:
            assert mf.counter == 3
        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function

        # Now we change the location cache to have only 1 preferred read region
        original_location_cache.available_read_locations = [self.REGION1]
        original_location_cache.read_regional_endpoints = [self.REGIONAL_ENDPOINT]
        try:
            # Reset the function to reset the counter
            mf = self.MockExecuteServiceRequestException()
            _retry_utility.ExecuteFunction = mf
            container.read_item(created_item['id'], created_item['pk'])
            pytest.fail("Exception was not raised.")
        except ServiceRequestError:
            assert mf.counter == 1
        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function

        # Now we try it out with a write request
        original_location_cache.available_write_locations = [self.REGION1, self.REGION2]
        original_location_cache.write_regional_endpoints = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT]
        original_location_cache.available_write_regional_endpoints_by_locations = {self.REGION1: self.REGIONAL_ENDPOINT,
                                                                                   self.REGION2: self.REGIONAL_ENDPOINT}
        try:
            # Reset the function to reset the counter
            mf = self.MockExecuteServiceRequestException()
            _retry_utility.ExecuteFunction = mf
            container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
            pytest.fail("Exception was not raised.")
        except ServiceRequestError:
            # Should retry twice in each region
            assert mf.counter == 2
        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function


    def test_service_response_read_timeout_retry(self):
        mock_client = CosmosClient(self.host, self.masterKey)
        db = mock_client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_ID)

        created_item = container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
        # Save the original function
        self.original_execute_function = _retry_utility.ExecuteFunction

        # Change the location cache to have 3 preferred read regions and 3 available read endpoints by location
        original_location_cache = mock_client.client_connection._global_endpoint_manager.location_cache
        original_location_cache.available_read_locations = [self.REGION1, self.REGION2, self.REGION3]
        original_location_cache.available_read_regional_endpoints_by_locations = {self.REGION1: self.REGIONAL_ENDPOINT,
                                                                                  self.REGION2: self.REGIONAL_ENDPOINT,
                                                                                  self.REGION3: self.REGIONAL_ENDPOINT}
        original_location_cache.read_regional_endpoints = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT,
                                                           self.REGIONAL_ENDPOINT]
        try:
            # Mock the function to return the ReadTimeout we retry
            mf = self.MockExecuteServiceResponseException(Exception)
            _retry_utility.ExecuteFunction = mf
            container.read_item(created_item['id'], created_item['pk'])
            pytest.fail("Exception was not raised.")
        except ServiceResponseError:
            assert mf.counter == 3
        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function

        # Now we change the location cache to have only 1 preferred read region
        original_location_cache.available_read_locations = [self.REGION1]
        original_location_cache.read_regional_endpoints = [self.REGIONAL_ENDPOINT]
        try:
            # Reset the function to reset the counter
            mf = self.MockExecuteServiceResponseException(Exception)
            _retry_utility.ExecuteFunction = mf
            container.read_item(created_item['id'], created_item['pk'])
            pytest.fail("Exception was not raised.")
        except ServiceResponseError:
            assert mf.counter == 1
        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function

        # Now we try it out with a write request
        original_location_cache.available_write_locations = [self.REGION1, self.REGION2]
        original_location_cache.write_regional_endpoints = [self.REGIONAL_ENDPOINT, self.REGIONAL_ENDPOINT]
        original_location_cache.available_write_regional_endpoints_by_locations = {self.REGION1: self.REGIONAL_ENDPOINT,
                                                                                   self.REGION2: self.REGIONAL_ENDPOINT}
        try:
            # Reset the function to reset the counter
            mf = self.MockExecuteServiceResponseException(Exception)
            _retry_utility.ExecuteFunction = mf
            # Even though we have 2 preferred write endpoints,
            # we will only run the exception once due to no retries on write requests
            container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
            pytest.fail("Exception was not raised.")
        except ServiceResponseError:
            assert mf.counter == 1
        finally:
            _retry_utility.ExecuteFunction = self.original_execute_function


    class MockExecuteServiceRequestException(object):
        def __init__(self):
            self.counter = 0

        def __call__(self, func, *args, **kwargs):
            self.counter = self.counter + 1
            exception = ServiceRequestError("mock exception")
            exception.exc_type = Exception
            raise exception

    class MockExecuteServiceResponseException(object):
        def __init__(self, err_type):
            self.err_type = err_type
            self.counter = 0

        def __call__(self, func, *args, **kwargs):
            self.counter = self.counter + 1
            exception = ServiceResponseError("mock exception")
            exception.exc_type = self.err_type
            raise exception