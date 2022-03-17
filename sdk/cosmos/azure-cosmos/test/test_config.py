#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import os
import time
import uuid
import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos.partition_key import NonePartitionKeyValue
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

    global_host = '[YOUR_GLOBAL_ENDPOINT_HERE]'
    write_location_host = '[YOUR_WRITE_ENDPOINT_HERE]'
    read_location_host = '[YOUR_READ_ENDPOINT_HERE]'
    read_location2_host = '[YOUR_READ_ENDPOINT2_HERE]'
    global_masterKey = '[YOUR_KEY_HERE]'

    write_location = '[YOUR_WRITE_LOCATION_HERE]'
    read_location = '[YOUR_READ_LOCATION_HERE]'
    read_location2 = '[YOUR_READ_LOCATION2_HERE]'

    THROUGHPUT_FOR_5_PARTITIONS = 30000
    THROUGHPUT_FOR_1_PARTITION = 400

    TEST_DATABASE_ID = os.getenv('COSMOS_TEST_DATABASE_ID', "Python SDK Test Database " + str(uuid.uuid4()))
    TEST_DATABASE_ID_PLAIN = "COSMOS_TEST_DATABASE"
    TEST_THROUGHPUT_DATABASE_ID = "Python SDK Test Throughput Database " + str(uuid.uuid4())
    TEST_COLLECTION_SINGLE_PARTITION_ID = "Single Partition Test Collection"
    TEST_COLLECTION_MULTI_PARTITION_ID = "Multi Partition Test Collection"
    TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_ID = "Multi Partition Test Collection With Custom PK"

    TEST_COLLECTION_MULTI_PARTITION_PARTITION_KEY = "id"
    TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_PARTITION_KEY = "pk"

    TEST_DATABASE = None
    TEST_COLLECTION_SINGLE_PARTITION = None
    TEST_COLLECTION_MULTI_PARTITION = None
    TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK = None

    IS_MULTIMASTER_ENABLED = False
    @classmethod
    def create_database_if_not_exist(cls, client):
        # type: (CosmosClient) -> Database
        if cls.TEST_DATABASE is not None:
            return cls.TEST_DATABASE
        cls.try_delete_database(client)
        cls.TEST_DATABASE = client.create_database(cls.TEST_DATABASE_ID)
        cls.IS_MULTIMASTER_ENABLED = client.get_database_account()._EnableMultipleWritableLocations
        return cls.TEST_DATABASE

    @classmethod
    def create_database_if_not_exist_with_throughput(cls, client, throughput):
        # type: (CosmosClient) -> Database
        if cls.TEST_DATABASE is not None:
            return cls.TEST_DATABASE
        cls.try_delete_database(client)
        cls.TEST_DATABASE = client.create_database(id=cls.TEST_THROUGHPUT_DATABASE_ID, offer_throughput=throughput)
        cls.IS_MULTIMASTER_ENABLED = client.get_database_account()._EnableMultipleWritableLocations
        return cls.TEST_DATABASE

    @classmethod
    def try_delete_database(cls, client):
        # type: (CosmosClient) -> None
        try:
            client.delete_database(cls.TEST_DATABASE_ID)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code != StatusCodes.NOT_FOUND:
                raise e

    @classmethod
    def create_single_partition_collection_if_not_exist(cls, client):
        # type: (CosmosClient) -> Container
        if cls.TEST_COLLECTION_SINGLE_PARTITION is None:
            cls.TEST_COLLECTION_SINGLE_PARTITION = cls.create_collection_with_required_throughput(client,
                    cls.THROUGHPUT_FOR_1_PARTITION, False)
        cls.remove_all_documents(cls.TEST_COLLECTION_SINGLE_PARTITION, False)
        return cls.TEST_COLLECTION_SINGLE_PARTITION


    @classmethod
    def create_multi_partition_collection_if_not_exist(cls, client):
        # type: (CosmosClient) -> Container
        if cls.TEST_COLLECTION_MULTI_PARTITION is None:
            cls.TEST_COLLECTION_MULTI_PARTITION = cls.create_collection_with_required_throughput(client,
                    cls.THROUGHPUT_FOR_5_PARTITIONS, False)
        cls.remove_all_documents(cls.TEST_COLLECTION_MULTI_PARTITION, False)
        return cls.TEST_COLLECTION_MULTI_PARTITION

    @classmethod
    def create_multi_partition_collection_with_custom_pk_if_not_exist(cls, client):
        # type: (CosmosClient) -> Container
        if cls.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK is None:
            cls.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK = cls.create_collection_with_required_throughput(client,
                    cls.THROUGHPUT_FOR_5_PARTITIONS, True)
        cls.remove_all_documents(cls.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK, True)
        return cls.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK

    @classmethod
    def create_collection_if_not_exist_no_custom_throughput(cls, client):
        # type: (CosmosClient) -> Container
        database = cls.create_database_if_not_exist(client)
        collection_id = cls.TEST_COLLECTION_SINGLE_PARTITION_ID

        document_collection = database.create_container_if_not_exists(
            id=collection_id,
            partition_key=PartitionKey(path="/id"))
        return document_collection

    @classmethod
    def create_collection_with_required_throughput(cls, client, throughput, use_custom_partition_key):
        # type: (CosmosClient, int, boolean) -> Container
        database = cls.create_database_if_not_exist(client)

        if throughput == cls.THROUGHPUT_FOR_1_PARTITION:
            collection_id = cls.TEST_COLLECTION_SINGLE_PARTITION_ID
            partition_key = cls.TEST_COLLECTION_MULTI_PARTITION_PARTITION_KEY
        else:
            if use_custom_partition_key:
                collection_id = cls.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_ID
                partition_key = cls.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_PARTITION_KEY
            else:
                collection_id = cls.TEST_COLLECTION_MULTI_PARTITION_ID
                partition_key = cls.TEST_COLLECTION_MULTI_PARTITION_PARTITION_KEY

        document_collection = database.create_container(
            id=collection_id,
            partition_key=PartitionKey(path='/' + partition_key, kind='Hash'),
            offer_throughput=throughput)
        return document_collection

    @classmethod
    def remove_all_documents(cls, document_collection, use_custom_partition_key):
        # type: (Container, boolean) -> None
        while True:
            query_iterable = document_collection.query_items(query="Select * from c", enable_cross_partition_query=True)
            read_documents = list(query_iterable)
            try:
                for document in read_documents:
                    partition_key = 'dummy_pk'
                    if not use_custom_partition_key:
                        partition_key = document[cls.TEST_COLLECTION_MULTI_PARTITION_PARTITION_KEY]
                    else:
                        if cls.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_PARTITION_KEY in document:
                            partition_key = document[cls.TEST_COLLECTION_MULTI_PARTITION_WITH_CUSTOM_PK_PARTITION_KEY]
                        else:
                            partition_key = NonePartitionKeyValue
                    document_collection.delete_item(item=document, partition_key=partition_key)
                if cls.IS_MULTIMASTER_ENABLED:
                    # sleep to ensure deletes are propagated for multimaster enabled accounts
                    time.sleep(2)
                break
            except exceptions.CosmosHttpResponseError as e:
                print("Error occurred while deleting documents:" + str(e) + " \nRetrying...")


class FakeResponse:
    def __init__(self, headers):
        self.headers = headers
        self.reason = "foo"
        self.status_code = "bar"
