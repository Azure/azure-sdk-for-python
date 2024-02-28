# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import collections
import os
import uuid

import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
from azure.cosmos import ContainerProxy
from azure.cosmos import DatabaseProxy
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey

try:
    import urllib3

    urllib3.disable_warnings()
except:
    print("no urllib3")


class TestConfig(object):
    # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="Cosmos DB Emulator Key")]
    masterKey = os.getenv('ACCOUNT_KEY',
                          'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==')
    host = os.getenv('ACCOUNT_HOST', 'https://localhost:8081/')
    connection_str = os.getenv('ACCOUNT_CONNECTION_STR', 'AccountEndpoint={};AccountKey={};'.format(host, masterKey))

    connectionPolicy = documents.ConnectionPolicy()
    connectionPolicy.DisableSSLVerification = True

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


class FakeResponse:
    def __init__(self, headers):
        self.headers = headers
        self.reason = "foo"
        self.status_code = "bar"
