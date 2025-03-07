# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import collections
import os
import time
import unittest
import uuid

from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos import (ContainerProxy, DatabaseProxy, documents, exceptions, ConnectionRetryPolicy,
                          http_constants, _retry_utility)
from azure.cosmos.aio import _retry_utility_async
from azure.core.exceptions import AzureError, ServiceRequestError, ServiceResponseError
from azure.core.pipeline.policies import AsyncRetryPolicy, RetryPolicy
from devtools_testutils.azure_recorded_testcase import get_credential
from devtools_testutils.helpers import is_live

try:
    import urllib3

    urllib3.disable_warnings()
except:
    print("no urllib3")


class TestConfig(object):
    local_host = 'https://localhost:8081/'
    # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="Cosmos DB Emulator Key")]
    masterKey = os.getenv('ACCOUNT_KEY',
                          'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==')
    host = os.getenv('ACCOUNT_HOST', local_host)
    connection_str = os.getenv('ACCOUNT_CONNECTION_STR', 'AccountEndpoint={};AccountKey={};'.format(host, masterKey))

    connectionPolicy = documents.ConnectionPolicy()
    connectionPolicy.DisableSSLVerification = True
    is_emulator = host == local_host
    is_live._cache = True if not is_emulator else False
    credential = masterKey if is_emulator else get_credential()
    credential_async = masterKey if is_emulator else get_credential(is_async=True)

    global_host = os.getenv('GLOBAL_ACCOUNT_HOST', host)
    write_location_host = os.getenv('WRITE_LOCATION_HOST', host)
    read_location_host = os.getenv('READ_LOCATION_HOST', host)
    read_location2_host = os.getenv('READ_LOCATION_HOST2', host)
    global_masterKey = os.getenv('GLOBAL_ACCOUNT_KEY', masterKey)

    write_location = os.getenv('WRITE_LOCATION', host)
    read_location = os.getenv('READ_LOCATION', host)
    read_location2 = os.getenv('READ_LOCATION2', host)

    THROUGHPUT_FOR_5_PARTITIONS = 30000
    THROUGHPUT_FOR_1_PARTITION = 400

    TEST_DATABASE_ID = os.getenv('COSMOS_TEST_DATABASE_ID', "Python SDK Test Database " + str(uuid.uuid4()))

    TEST_SINGLE_PARTITION_CONTAINER_ID = "Single Partition Test Container " + str(uuid.uuid4())
    TEST_MULTI_PARTITION_CONTAINER_ID = "Multi Partition Test Container " + str(uuid.uuid4())

    TEST_CONTAINER_PARTITION_KEY = "pk"

    @classmethod
    def create_database_if_not_exist(cls, client):
        # type: (CosmosClient) -> DatabaseProxy
        test_database = client.create_database_if_not_exists(cls.TEST_DATABASE_ID,
                                                             offer_throughput=cls.THROUGHPUT_FOR_1_PARTITION)
        return test_database

    @classmethod
    def create_single_partition_container_if_not_exist(cls, client):
        # type: (CosmosClient) -> ContainerProxy
        database = cls.create_database_if_not_exist(client)
        document_collection = database.create_container_if_not_exists(
            id=cls.TEST_SINGLE_PARTITION_CONTAINER_ID,
            partition_key=PartitionKey(path='/' + cls.TEST_CONTAINER_PARTITION_KEY, kind='Hash'),
            offer_throughput=cls.THROUGHPUT_FOR_1_PARTITION)
        return document_collection

    @classmethod
    def create_multi_partition_container_if_not_exist(cls, client):
        # type: (CosmosClient) -> ContainerProxy
        database = cls.create_database_if_not_exist(client)
        document_collection = database.create_container_if_not_exists(
            id=cls.TEST_MULTI_PARTITION_CONTAINER_ID,
            partition_key=PartitionKey(path='/' + cls.TEST_CONTAINER_PARTITION_KEY, kind='Hash'),
            offer_throughput=cls.THROUGHPUT_FOR_5_PARTITIONS)
        return document_collection

    @classmethod
    def try_delete_database(cls, client):
        # type: (CosmosClient) -> None
        try:
            client.delete_database(cls.TEST_DATABASE_ID)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code != StatusCodes.NOT_FOUND:
                raise e

    @classmethod
    def try_delete_database_with_id(cls, client, database_id):
        # type: (CosmosClient, str) -> None
        try:
            client.delete_database(database_id)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code != StatusCodes.NOT_FOUND:
                raise e

    @classmethod
    async def _validate_distinct_on_different_types_and_field_orders(cls, collection, query, expected_results):
        query_iterable = collection.query_items(query)
        results = [item async for item in query_iterable]
        for i in range(len(expected_results)):
            assert results[i] in expected_results

    @classmethod
    def _get_query_result_string(cls, query_result, fields):
        if type(query_result) is not dict:
            return str(query_result)
        res = str(query_result[fields[0]] if fields[0] in query_result else None)
        if len(fields) == 2:
            res = res + "," + str(query_result[fields[1]] if fields[1] in query_result else None)

        return res

    @classmethod
    async def _validate_distinct(cls, created_collection, query, results, is_select, fields):
        query_iterable = created_collection.query_items(query=query)
        query_results = [item async for item in query_iterable]

        assert len(results) == len(query_results)
        query_results_strings = []
        result_strings = []
        for i in range(len(results)):
            query_results_strings.append(cls._get_query_result_string(query_results[i], fields))
            result_strings.append(str(results[i]))
        if is_select:
            query_results_strings = sorted(query_results_strings)
            result_strings = sorted(result_strings)
        assert result_strings == query_results_strings

    @classmethod
    def _pad_with_none(cls, documents_param, field):
        for doc in documents_param:
            if field not in doc:
                doc[field] = None
        return documents_param

    @classmethod
    def _get_distinct_docs(cls, documents_param, field1, field2, is_order_by_or_value):
        if field2 is None:
            res = collections.OrderedDict.fromkeys(doc[field1] for doc in documents_param)
            if is_order_by_or_value:
                res = filter(lambda x: False if x is None else True, res)
        else:
            res = collections.OrderedDict.fromkeys(str(doc[field1]) + "," + str(doc[field2]) for doc in documents_param)
        return list(res)

    @classmethod
    def _get_order_by_docs(cls, documents_param, field1, field2):
        if field2 is None:
            return sorted(documents_param, key=lambda d: (d[field1] is not None, d[field1]))
        else:
            return sorted(documents_param,
                          key=lambda d: (d[field1] is not None, d[field1], d[field2] is not None, d[field2]))

    @classmethod
    async def _validate_distinct_offset_limit(cls, created_collection, query, results):
        query_iterable = created_collection.query_items(query=query)
        assert list(map(lambda doc: doc['value'], [item async for item in query_iterable])) == results

    @classmethod
    async def _validate_offset_limit(cls, created_collection, query, results):
        query_iterable = created_collection.query_items(query=query)
        assert list(map(lambda doc: doc['pk'], [item async for item in query_iterable])) == results

    @staticmethod
    def trigger_split(container, throughput):
        print("Triggering a split in session token helpers")
        container.replace_throughput(throughput)
        print("changed offer to 11k")
        print("--------------------------------")
        print("Waiting for split to complete")
        start_time = time.time()

        while True:
            offer = container.get_throughput()
            if offer.properties['content'].get('isOfferReplacePending', False):
                if time.time() - start_time > 60 * 25:  # timeout test at 25 minutes
                    unittest.skip("Partition split didn't complete in time.")
                else:
                    print("Waiting for split to complete")
                    time.sleep(60)
            else:
                break
        print("Split in session token helpers has completed")

    @staticmethod
    async def trigger_split_async(container, throughput):
        print("Triggering a split in session token helpers")
        await container.replace_throughput(throughput)
        print("changed offer to 11k")
        print("--------------------------------")
        print("Waiting for split to complete")
        start_time = time.time()

        while True:
            offer = await container.get_throughput()
            if offer.properties['content'].get('isOfferReplacePending', False):
                if time.time() - start_time > 60 * 25:  # timeout test at 25 minutes
                    unittest.skip("Partition split didn't complete in time.")
                else:
                    print("Waiting for split to complete")
                    time.sleep(60)
            else:
                break
        print("Split in session token helpers has completed")


def get_vector_indexing_policy(embedding_type):
    return {
        "indexingMode": "consistent",
        "includedPaths": [{"path": "/*"}],
        'excludedPaths': [{'path': '/"_etag"/?'}],
        "vectorIndexes": [
            {"path": "/embedding", "type": f"{embedding_type}"}
        ]
    }


def get_vector_embedding_policy(distance_function, data_type, dimensions):
    return {
        "vectorEmbeddings": [
            {
                "path": "/embedding",
                "dataType": f"{data_type}",
                "dimensions": dimensions,
                "distanceFunction": f"{distance_function}"
            }
        ]
    }


def get_full_text_indexing_policy(path):
    return {
        "indexingMode": "consistent",
        "includedPaths": [{"path": "/*"}],
        'excludedPaths': [{'path': '/"_etag"/?'}],
        "fullTextIndexes": [
            {"path": path}
        ]
    }


def get_full_text_policy(path):
    return {
        "defaultLanguage": "en-US",
        "fullTextPaths": [
            {
                "path": path,
                "language": "en-US"
            }
        ]
    }


class FakeResponse:
    def __init__(self, headers):
        self.headers = headers
        self.reason = "foo"
        self.status_code = "bar"


class FakePipelineResponse:
    def __init__(self, headers=None, status_code=200, message="test-message"):
        self.http_response = FakeHttpResponse(headers, status_code, message)


class FakeHttpResponse:
    def __init__(self, headers=None, status_code=200, message="test-message"):
        if headers is None:
            headers = {}
        self.headers = headers
        self.status_code = status_code
        self.reason = message

    def body(self):
        return None


class MockConnectionRetryPolicy(RetryPolicy):
    def __init__(self, resource_type, error, **kwargs):
        self.resource_type = resource_type
        self.error = error
        self.counter = 0
        self.request_endpoints = []
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super().__init__(**clean_kwargs)

    def send(self, request):
        self.counter = 0
        absolute_timeout = request.context.options.pop('timeout', None)

        retry_active = True
        response = None
        retry_settings = self.configure_retries(request.context.options)
        while retry_active:
            start_time = time.time()
            try:
                # raise the passed in exception for the passed in resource + operation combination
                if request.http_request.headers.get(http_constants.HttpHeaders.ThinClientProxyResourceType) == self.resource_type:
                    self.request_endpoints.append(request.http_request.url)
                    raise self.error
                response = self.next.send(request)
                break
            except ServiceRequestError as err:
                # the request ran into a socket timeout or failed to establish a new connection
                # since request wasn't sent, raise exception immediately to be dealt with in client retry policies
                # This logic is based on the _retry.py file from azure-core
                if retry_settings['connect'] > 0:
                    self.counter += 1
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    if retry_active:
                        self.sleep(retry_settings, request.context.transport)
                        continue
                raise err
            except ServiceResponseError as err:
                # Only read operations can be safely retried with ServiceResponseError
                if not _retry_utility._has_read_retryable_headers(request.http_request.headers):
                    raise err
                # This logic is based on the _retry.py file from azure-core
                if retry_settings['read'] > 0:
                    self.counter += 1
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    if retry_active:
                        self.sleep(retry_settings, request.context.transport)
                        continue
                raise err
            except AzureError as err:
                if self._is_method_retryable(retry_settings, request.http_request):
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    if retry_active:
                        self.sleep(retry_settings, request.context.transport)
                        continue
                raise err
            finally:
                end_time = time.time()
                if absolute_timeout:
                    absolute_timeout -= (end_time - start_time)

        self.update_context(response.context, retry_settings)
        return response

class MockConnectionRetryPolicyAsync(AsyncRetryPolicy):

    def __init__(self, resource_type, error, **kwargs):
        self.resource_type = resource_type
        self.error = error
        self.counter = 0
        self.request_endpoints = []
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super(MockConnectionRetryPolicyAsync, self).__init__(**clean_kwargs)

    async def send(self, request):
        """Sends the PipelineRequest object to the next policy. Uses retry settings if necessary.
        Also enforces an absolute client-side timeout that spans multiple retry attempts.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: Returns the PipelineResponse or raises error if maximum retries exceeded.
        :rtype: ~azure.core.pipeline.PipelineResponse
        :raises ~azure.core.exceptions.AzureError: Maximum retries exceeded.
        :raises ~azure.cosmos.exceptions.CosmosClientTimeoutError: Specified timeout exceeded.
        :raises ~azure.core.exceptions.ClientAuthenticationError: Authentication failed.
        """
        absolute_timeout = request.context.options.pop('timeout', None)
        per_request_timeout = request.context.options.pop('connection_timeout', 0)
        self.counter = 0
        retry_error = None
        retry_active = True
        response = None
        retry_settings = self.configure_retries(request.context.options)
        while retry_active:
            start_time = time.time()
            try:
                # raise the passed in exception for the passed in resource + operation combination
                if request.http_request.headers.get(
                        http_constants.HttpHeaders.ThinClientProxyResourceType) == self.resource_type:
                    self.request_endpoints.append(request.http_request.url)
                    raise self.error
                _retry_utility._configure_timeout(request, absolute_timeout, per_request_timeout)
                response = await self.next.send(request)
                break
            except exceptions.CosmosClientTimeoutError as timeout_error:
                timeout_error.inner_exception = retry_error
                timeout_error.response = response
                timeout_error.history = retry_settings['history']
                raise
            except ServiceRequestError as err:
                retry_error = err
                # the request ran into a socket timeout or failed to establish a new connection
                # since request wasn't sent, raise exception immediately to be dealt with in client retry policies
                if retry_settings['connect'] > 0:
                    self.counter += 1
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    print("Basic Retry in retry utility: ", retry_active)
                    if retry_active:
                        await self.sleep(retry_settings, request.context.transport)
                        continue
                raise err
            except ServiceResponseError as err:
                retry_error = err
                # Since this is ClientConnectionError, it is safe to be retried on both read and write requests
                from aiohttp.client_exceptions import (
                    ClientConnectionError)  # pylint: disable=networking-import-outside-azure-core-transport
                if isinstance(err.inner_exception, ClientConnectionError) or _retry_utility_async._has_read_retryable_headers(request.http_request.headers):
                    # This logic is based on the _retry.py file from azure-core
                    if retry_settings['read'] > 0:
                        self.counter += 1
                        retry_active = self.increment(retry_settings, response=request, error=err)
                        if retry_active:
                            await self.sleep(retry_settings, request.context.transport)
                            continue
                raise err
            except AzureError as err:
                retry_error = err
                if self._is_method_retryable(retry_settings, request.http_request):
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    if retry_active:
                        await self.sleep(retry_settings, request.context.transport)
                        continue
                raise err
            finally:
                end_time = time.time()
                if absolute_timeout:
                    absolute_timeout -= (end_time - start_time)

        self.update_context(response.context, retry_settings)
        return response
