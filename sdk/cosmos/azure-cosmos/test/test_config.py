# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import collections
import os
import time
import uuid

import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey

try:
    import urllib3

    urllib3.disable_warnings()
except:
    print("no urllib3")


class _test_config(object):

    #[SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="Cosmos DB Emulator Key")]
    masterKey = os.getenv('ACCOUNT_KEY', 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==')
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
    TEST_THROUGHPUT_DATABASE_ID = "Python SDK Test Throughput Database " + str(uuid.uuid4())
    TEST_COLLECTION_SINGLE_PARTITION_ID = "Single Partition Test Collection " + str(uuid.uuid4())
    TEST_COLLECTION_MULTI_PARTITION_ID = "Multi Partition Test Collection " + str(uuid.uuid4())
    TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_ID = ("Multi Partition Test Collection With Custom PK "
                                                         + str(uuid.uuid4()))

    TEST_COLLECTION_MULTI_PARTITION_PARTITION_KEY = "id"
    TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_PARTITION_KEY = "pk"

    IS_MULTI_MASTER_ENABLED = False

    @classmethod
    def create_database_if_not_exist(cls, client):
        # type: (CosmosClient) -> Database
        cls.try_delete_database(client)
        test_database = client.create_database(cls.TEST_DATABASE_ID)
        cls.IS_MULTI_MASTER_ENABLED = client.get_database_account()._EnableMultipleWritableLocations
        return test_database

    @classmethod
    def try_delete_database(cls, client):
        # type: (CosmosClient) -> None
        try:
            client.delete_database(cls.TEST_DATABASE_ID)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code != StatusCodes.NOT_FOUND:
                raise e

    @classmethod
    def create_multi_partition_collection_if_not_exist(cls, client):
        # type: (CosmosClient) -> Container
        test_collection_multi_partition = cls.create_collection_with_required_throughput(
            client,
            cls.THROUGHPUT_FOR_5_PARTITIONS,
            False)
        cls.remove_all_documents(test_collection_multi_partition, False)
        return test_collection_multi_partition

    @classmethod
    def create_multi_partition_collection_with_custom_pk_if_not_exist(cls, client):
        # type: (CosmosClient) -> Container
        test_collection_multi_partition_with_custom_pk = cls.create_collection_with_required_throughput(
            client,
            cls.THROUGHPUT_FOR_5_PARTITIONS,
            True)
        cls.remove_all_documents(test_collection_multi_partition_with_custom_pk, True)
        return test_collection_multi_partition_with_custom_pk

    @classmethod
    def create_collection_with_required_throughput(cls, client, throughput, use_custom_partition_key):
        # type: (CosmosClient, int, boolean) -> Container
        database = cls.create_database_if_not_exist(client)

        if throughput == cls.THROUGHPUT_FOR_1_PARTITION:
            collection_id = cls.TEST_CONTAINER_SINGLE_PARTITION_ID
            partition_key = cls.TEST_COLLECTION_MULTI_PARTITION_PARTITION_KEY
        else:
            if use_custom_partition_key:
                collection_id = cls.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_ID
                partition_key = cls.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_PARTITION_KEY
            else:
                collection_id = cls.TEST_COLLECTION_MULTI_PARTITION_ID
                partition_key = cls.TEST_COLLECTION_MULTI_PARTITION_PARTITION_KEY

        document_collection = database.create_container_if_not_exists(
            id=collection_id,
            partition_key=PartitionKey(path='/' + partition_key, kind='Hash'),
            offer_throughput=throughput)
        return document_collection

    @classmethod
    def remove_all_documents(cls, document_collection, partition_key):
        # type: (Container, boolean) -> None
        while True:
            query_iterable = document_collection.query_items(query="Select * from c", enable_cross_partition_query=True)
            read_documents = list(query_iterable)
            try:
                for document in read_documents:
                    document_collection.delete_item(item=document, partition_key=partition_key)
                if cls.IS_MULTI_MASTER_ENABLED:
                    # sleep to ensure deletes are propagated for multimaster enabled accounts
                    time.sleep(2)
                break
            except exceptions.CosmosHttpResponseError as e:
                print("Error occurred while deleting documents:" + str(e) + " \nRetrying...")

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
