# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original async partitioned-container document CRUD test, re-run on the Rust path.

Source: ``tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync``.
The method keeps the original steps and assertions; only setup changed. The
client uses ``_backend="rust"`` and the test owns a uniquely named database
(the original creates its own ``/id`` container inside it), deleted afterwards.
"""

import pytest
import os
import unittest
import uuid

from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosAADLong
@pytest.mark.cosmosLong
class TestCRUDContainerOperationsAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        await self.client.__aenter__()
        self._db_id = "delete_item_crud_container_async_" + uuid.uuid4().hex
        self.key_databaseForTest = None
        try:
            self.key_databaseForTest = await self.client.create_database(self._db_id)
        except BaseException:
            await self.client.close()
            raise
        self.data_databaseForTest = self.key_databaseForTest
        self.database_for_test = self.key_databaseForTest

    async def asyncTearDown(self):
        try:
            if self.key_databaseForTest is not None:
                await self.client.delete_database(self._db_id)
        finally:
            await self.client.close()

    async def test_partitioned_collection_document_crud_and_query_async_rust(self):
        # Source: tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_partitioned_collection_document_crud_and_query_async
        created_collection_ref = await self.key_databaseForTest.create_container(
            str(uuid.uuid4()), PartitionKey(path="/id")
        )
        created_collection = self.data_databaseForTest.get_container_client(created_collection_ref.id)

        document_definition = {'id': 'document',
                               'key': 'value'}

        created_document = await created_collection.create_item(body=document_definition)

        assert created_document.get('id') == document_definition.get('id')
        assert created_document.get('key') == document_definition.get('key')

        # read document
        read_document = await created_collection.read_item(
            item=created_document.get('id'),
            partition_key=created_document.get('id')
        )

        assert read_document.get('id') == created_document.get('id')
        assert read_document.get('key') == created_document.get('key')

        # Read document feed doesn't require partitionKey as it's always a cross partition query
        document_list = [document async for document in created_collection.read_all_items()]
        assert 1 == len(document_list)

        # replace document
        document_definition['key'] = 'new value'

        replaced_document = await created_collection.replace_item(
            item=read_document,
            body=document_definition
        )

        assert replaced_document.get('key') == document_definition.get('key')

        # upsert document(create scenario)
        document_definition['id'] = 'document2'
        document_definition['key'] = 'value2'

        upserted_document = await created_collection.upsert_item(body=document_definition)

        assert upserted_document.get('id') == document_definition.get('id')
        assert upserted_document.get('key') == document_definition.get('key')

        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == 2

        # delete document
        await created_collection.delete_item(item=upserted_document, partition_key=upserted_document.get('id'))

        # query document on the partition key specified in the predicate will pass even without setting enableCrossPartitionQuery or passing in the partitionKey value
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.id=\'' + replaced_document.get('id') + '\''  # nosec
        )]
        assert len(document_list) == 1

        # cross partition query
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'')]

        assert len(document_list) == 1

        # query document by providing the partitionKey value
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            partition_key=replaced_document.get('id')
        )]

        assert len(document_list) == 1
        # Known gap 23: Container delete and replace require preliminary metadata (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-23). On Rust this delete_container step first resolves container metadata (possible extra GET) before the DELETE; the step still executes.
        await self.key_databaseForTest.delete_container(created_collection.id)


if __name__ == "__main__":
    unittest.main()
