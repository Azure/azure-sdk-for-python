# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import collections
import logging
import os
import random
import time
import unittest
import uuid

from azure.core.exceptions import AzureError, ServiceRequestError, ServiceResponseError, ClientAuthenticationError
from azure.core.pipeline.policies import AsyncRetryPolicy, RetryPolicy
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._retry_utility import _has_database_account_header, _has_read_retryable_headers, _configure_timeout
from azure.cosmos._routing.routing_range import Range
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import StatusCodes, HttpHeaders
from azure.cosmos.partition_key import (PartitionKey, _PartitionKeyKind, _PartitionKeyVersion, _Undefined,
                                        NonePartitionKeyValue)
from azure.cosmos import (ContainerProxy, DatabaseProxy, documents, exceptions,
                          http_constants)
# from devtools_testutils.azure_recorded_testcase import get_credential
# from devtools_testutils.helpers import is_live
from typing import Sequence, Type, Union

try:
    import urllib3

    urllib3.disable_warnings()
except:
    print("no urllib3")

SPLIT_TIMEOUT = 60*10  # timeout test at 10 minutes
SLEEP_TIME = 30  # sleep for 30 seconds

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
    # is_live._cache = True if not is_emulator else False
    credential = masterKey #if is_emulator else get_credential()
    credential_async = masterKey #if is_emulator else get_credential(is_async=True)

    global_host = os.getenv('GLOBAL_ACCOUNT_HOST', host)
    write_location_host = os.getenv('WRITE_LOCATION_HOST', host)
    read_location_host = os.getenv('READ_LOCATION_HOST', host)
    read_location2_host = os.getenv('READ_LOCATION_HOST2', host)
    global_masterKey = os.getenv('GLOBAL_ACCOUNT_KEY', masterKey)

    write_location = os.getenv('WRITE_LOCATION', host)
    read_location = os.getenv('READ_LOCATION', host)
    read_location2 = os.getenv('READ_LOCATION2', host)

    THROUGHPUT_FOR_5_PARTITIONS = 30000
    THROUGHPUT_FOR_2_PARTITIONS = 12000
    THROUGHPUT_FOR_1_PARTITION = 400

    TEST_DATABASE_ID = os.getenv('COSMOS_TEST_DATABASE_ID', "PythonSDKTestDatabase-" + str(uuid.uuid4()))

    TEST_SINGLE_PARTITION_CONTAINER_ID = "SinglePartitionTestContainer-" + str(uuid.uuid4())
    TEST_MULTI_PARTITION_CONTAINER_ID = "MultiPartitionTestContainer-" + str(uuid.uuid4())
    TEST_SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID = "SinglePartitionWithPrefixPKTestContainer-" + str(uuid.uuid4())
    TEST_MULTI_PARTITION_PREFIX_PK_CONTAINER_ID = "MultiPartitionWithPrefixPKTestContainer-" + str(uuid.uuid4())

    TEST_CONTAINER_PARTITION_KEY = "pk"
    TEST_CONTAINER_PREFIX_PARTITION_KEY = ["pk1", "pk2"]
    TEST_CONTAINER_PREFIX_PARTITION_KEY_PATH = ['/pk1', '/pk2']

    # these will be populated by the get_account_info method
    WRITE_LOCATION = ""
    # some default value that is needed for emulator tests
    READ_LOCATION = "West US"

    @classmethod
    def get_account_info(cls, client: CosmosClient):
        account_info = client.get_database_account()
        cls.WRITE_LOCATION = account_info.WritableLocations[0]["name"]
        if len(account_info.ReadableLocations) > 1:
            cls.READ_LOCATION = account_info.ReadableLocations[1]["name"]

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
    def create_single_partition_prefix_pk_container_if_not_exist(cls, client):
        # type: (CosmosClient) -> ContainerProxy
        database = cls.create_database_if_not_exist(client)
        document_collection = database.create_container_if_not_exists(
            id=cls.TEST_SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID,
            partition_key=PartitionKey(path=cls.TEST_CONTAINER_PREFIX_PARTITION_KEY_PATH, kind='MultiHash'),
            offer_throughput=cls.THROUGHPUT_FOR_1_PARTITION)
        return document_collection

    @classmethod
    def create_multi_partition_prefix_pk_container_if_not_exist(cls, client):
        # type: (CosmosClient) -> ContainerProxy
        database = cls.create_database_if_not_exist(client)
        document_collection = database.create_container_if_not_exists(
            id=cls.TEST_MULTI_PARTITION_PREFIX_PK_CONTAINER_ID,
            partition_key=PartitionKey(path=cls.TEST_CONTAINER_PREFIX_PARTITION_KEY_PATH, kind='MultiHash'),
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
        print(f"changed offer to {throughput}")
        print("--------------------------------")
        print("Waiting for split to complete")
        start_time = time.time()

        while True:
            offer = container.get_throughput()
            if offer.properties['content'].get('isOfferReplacePending', False):
                if time.time() - start_time > SPLIT_TIMEOUT:  # timeout test at 10 minutes
                    raise unittest.SkipTest("Partition split didn't complete in time")
                else:
                    print("Waiting for split to complete")
                    time.sleep(SLEEP_TIME)
            else:
                break
        print("Split in session token helpers has completed")

    @staticmethod
    async def trigger_split_async(container, throughput):
        print("Triggering a split in session token helpers")
        await container.replace_throughput(throughput)
        print(f"changed offer to {throughput}")
        print("--------------------------------")
        print("Waiting for split to complete")
        start_time = time.time()

        while True:
            offer = await container.get_throughput()
            if offer.properties['content'].get('isOfferReplacePending', False):
                if time.time() - start_time > SPLIT_TIMEOUT:  # timeout test at 10 minutes
                    raise unittest.SkipTest("Partition split didn't complete in time")
                else:
                    print("Waiting for split to complete")
                    time.sleep(SLEEP_TIME)
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

def get_test_item():
    test_item = {
        'id': 'Item_' + str(uuid.uuid4()),
        'test_object': True,
        'lastName': 'Smith',
        'attr1': random.randint(0, 10)
    }
    return test_item

def pre_split_hook(response):
    request_headers = response.http_request.headers
    session_token = request_headers.get('x-ms-session-token')
    assert len(session_token) <= 20
    assert session_token.startswith('0')
    assert session_token.count(':') == 1
    assert session_token.count(',') == 0

def post_split_hook(response):
    request_headers = response.http_request.headers
    session_token = request_headers.get('x-ms-session-token')
    assert len(session_token) > 30
    assert len(session_token) < 60 # should only be 0-1 or 0-2, not 0-1-2
    assert session_token.startswith('0') is False
    assert session_token.count(':') == 2
    assert session_token.count(',') == 1

class ResponseHookCaller:
    def __init__(self):
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1


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

def no_token_response_hook(raw_response):
    request_headers = raw_response.http_request.headers
    assert request_headers.get(HttpHeaders.SessionToken) is None

def token_response_hook(raw_response):
    request_headers = raw_response.http_request.headers
    assert request_headers.get(HttpHeaders.SessionToken) is not None


class MockConnectionRetryPolicy(RetryPolicy):
    def __init__(self, resource_type, error=None, **kwargs):
        self.resource_type = resource_type
        self.error = error
        self.counter = 0
        self.request_endpoints = []
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super().__init__(**clean_kwargs)

    def send(self, request):
        # background health checks could reset counter unintentionally
        if request.http_request.headers.get(http_constants.HttpHeaders.ThinClientProxyResourceType) == self.resource_type:
            self.counter = 0
        absolute_timeout = request.context.options.pop('timeout', None)
        per_request_timeout = request.context.options.pop('connection_timeout', 0)
        request_params = request.context.options.pop('request_params', None)
        global_endpoint_manager = request.context.options.pop('global_endpoint_manager', None)
        retry_error = None
        retry_active = True
        response = None
        retry_settings = self.configure_retries(request.context.options)
        while retry_active:
            start_time = time.time()
            try:
                # raise the passed in exception for the passed in resource + operation combination
                if request.http_request.headers.get(http_constants.HttpHeaders.ThinClientProxyResourceType) == self.resource_type:
                    self.request_endpoints.append(request.http_request.url)
                    if self.error:
                        raise self.error
                _configure_timeout(request, absolute_timeout, per_request_timeout)
                response = self.next.send(request)
                break
            except ClientAuthenticationError:  # pylint:disable=try-except-raise
                # the authentication policy failed such that the client's request can't
                # succeed--we'll never have a response to it, so propagate the exception
                raise
            except exceptions.CosmosClientTimeoutError as timeout_error:
                timeout_error.inner_exception = retry_error
                timeout_error.response = response
                timeout_error.history = retry_settings['history']
                raise
            except ServiceRequestError as err:
                retry_error = err
                # the request ran into a socket timeout or failed to establish a new connection
                # since request wasn't sent, raise exception immediately to be dealt with in client retry policies
                # This logic is based on the _retry.py file from azure-core
                if (not _has_database_account_header(request.http_request.headers)
                        and not request_params.healthy_tentative_location):
                    if retry_settings['connect'] > 0:
                        self.counter += 1
                        global_endpoint_manager.record_failure(request_params)
                        retry_active = self.increment(retry_settings, response=request, error=err)
                        if retry_active:
                            self.sleep(retry_settings, request.context.transport)
                            continue
                raise err
            except ServiceResponseError as err:
                retry_error = err
                # Only read operations can be safely retried with ServiceResponseError
                if (not _has_read_retryable_headers(request.http_request.headers) or
                        _has_database_account_header(request.http_request.headers) or
                        request_params.healthy_tentative_location):
                    raise err
                # This logic is based on the _retry.py file from azure-core
                if retry_settings['read'] > 0:
                    self.counter += 1
                    global_endpoint_manager.record_failure(request_params)
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    if retry_active:
                        self.sleep(retry_settings, request.context.transport)
                        continue
                raise err
            except CosmosHttpResponseError as err:
                raise err
            except AzureError as err:
                retry_error = err
                if (_has_database_account_header(request.http_request.headers) or
                        request_params.healthy_tentative_location):
                    raise err
                if _has_read_retryable_headers(request.http_request.headers) and retry_settings['read'] > 0:
                    self.counter += 1
                    global_endpoint_manager.record_failure(request_params)
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

    def __init__(self, resource_type, error = None, **kwargs):
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
        self.counter = 0
        absolute_timeout = request.context.options.pop('timeout', None)
        per_request_timeout = request.context.options.pop('connection_timeout', 0)
        request_params = request.context.options.pop('request_params', None)
        global_endpoint_manager = request.context.options.pop('global_endpoint_manager', None)
        retry_error = None
        retry_active = True
        response = None
        retry_settings = self.configure_retries(request.context.options)
        while retry_active:
            start_time = time.time()
            try:
                if request.http_request.headers.get(
                        http_constants.HttpHeaders.ThinClientProxyResourceType) == self.resource_type:
                    self.request_endpoints.append(request.http_request.url)
                    if self.error:
                        raise self.error
                _configure_timeout(request, absolute_timeout, per_request_timeout)
                response = await self.next.send(request)
                break
            except ClientAuthenticationError:  # pylint:disable=try-except-raise
                # the authentication policy failed such that the client's request can't
                # succeed--we'll never have a response to it, so propagate the exception
                raise
            except exceptions.CosmosClientTimeoutError as timeout_error:
                timeout_error.inner_exception = retry_error
                timeout_error.response = response
                timeout_error.history = retry_settings['history']
                raise
            except ServiceRequestError as err:
                retry_error = err
                # the request ran into a socket timeout or failed to establish a new connection
                # since request wasn't sent, raise exception immediately to be dealt with in client retry policies
                if (not _has_database_account_header(request.http_request.headers)
                        and not request_params.healthy_tentative_location):
                    if retry_settings['connect'] > 0:
                        self.counter += 1
                        await global_endpoint_manager.record_failure(request_params)
                        retry_active = self.increment(retry_settings, response=request, error=err)
                        if retry_active:
                            await self.sleep(retry_settings, request.context.transport)
                            continue
                raise err
            except ServiceResponseError as err:
                retry_error = err
                if (_has_database_account_header(request.http_request.headers) or
                        request_params.healthy_tentative_location):
                    raise err
                # Since this is ClientConnectionError, it is safe to be retried on both read and write requests
                try:
                    # pylint: disable=networking-import-outside-azure-core-transport
                    from aiohttp.client_exceptions import (
                        ClientConnectionError)
                    if (isinstance(err.inner_exception, ClientConnectionError)
                            or _has_read_retryable_headers(request.http_request.headers)):
                        # This logic is based on the _retry.py file from azure-core
                        if retry_settings['read'] > 0:
                            self.counter += 1
                            await global_endpoint_manager.record_failure(request_params)
                            retry_active = self.increment(retry_settings, response=request, error=err)
                            if retry_active:
                                await self.sleep(retry_settings, request.context.transport)
                                continue
                except ImportError:
                    raise err # pylint: disable=raise-missing-from
                raise err
            except CosmosHttpResponseError as err:
                raise err
            except AzureError as err:
                retry_error = err
                if (_has_database_account_header(request.http_request.headers) or
                        request_params.healthy_tentative_location):
                    raise err
                if _has_read_retryable_headers(request.http_request.headers) and retry_settings['read'] > 0:
                    self.counter += 1
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

def hash_partition_key_value(
        pk_value: Sequence[Union[None, bool, int, float, str, _Undefined, Type[NonePartitionKeyValue]]],
        kind: str = _PartitionKeyKind.HASH,
        version: int = _PartitionKeyVersion.V2,
    ):
    return PartitionKey._get_hashed_partition_key_string(
        pk_value=pk_value,
        kind=kind,
        version=version,
    )

def create_range(range_min: str, range_max: str, is_min_inclusive: bool = True, is_max_inclusive: bool = False):
    if range_max == range_min:
        range_max += "FF"
    return Range(
        range_min=range_min,
        range_max=range_max,
        isMinInclusive=is_min_inclusive,
        isMaxInclusive=is_max_inclusive,
    )

def create_feed_range_in_dict(feed_range):
    return FeedRangeInternalEpk(feed_range).to_dict()


class MockHandler(logging.Handler):

    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def reset(self):
        self.messages = []

    def emit(self, record):
        self.messages.append(record)
