# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original async hierarchical-partition document CRUD test, re-run on the Rust path.

Source: ``tests/test_crud_subpartition_async.py::TestSubpartitionCrudAsync``.
The method keeps the original steps and assertions; only setup changed. The
client uses ``_backend="rust"`` and the test owns a uniquely named database
(the original creates its own ``/city``, ``/zipcode`` MultiHash container
inside it), deleted afterwards.
"""

import pytest
import os
import unittest
import uuid

import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestSubpartitionCrudAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        await self.client.__aenter__()
        self._db_id = "upsert_item_crud_subpartition_async_" + uuid.uuid4().hex
        self.key_database = None
        try:
            self.key_database = await self.client.create_database(self._db_id)
        except BaseException:
            await self.client.close()
            raise
        self.database_for_test = self.key_database

    async def asyncTearDown(self):
        try:
            if self.key_database is not None:
                await self.client.delete_database(self._db_id)
        finally:
            await self.client.close()

    async def test_partitioned_collection_document_crud_and_query_subpartition_async_rust(self):
        # Source: tests/test_crud_subpartition_async.py::TestSubpartitionCrudAsync.test_partitioned_collection_document_crud_and_query_subpartition_async
        # Container create/delete uses key_database (control-plane).
        created_collection_ref = await self.key_database.create_container(
            id='test_partitioned_collection_partition_document_crud_and_query_MH ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path=['/city', '/zipcode'], kind=documents.PartitionKind.MultiHash)
        )
        created_collection = self.database_for_test.get_container_client(created_collection_ref.id)

        document_definition = {'id': 'document',
                               'key': 'value',
                               'city': 'Redmond',
                               'zipcode': '98052'}

        created_document = await created_collection.create_item(body=document_definition)

        assert created_document.get('id') == document_definition.get('id')
        assert created_document.get('key') == document_definition.get('key')
        assert created_document.get('city') == document_definition.get('city')
        assert created_document.get('zipcode') == document_definition.get('zipcode')

        # read document
        read_document = await created_collection.read_item(
            item=created_document.get('id'),
            partition_key=[created_document.get('city'), created_document.get('zipcode')]
        )

        assert read_document.get('id') == created_document.get('id')
        assert read_document.get('key') == created_document.get('key')
        assert read_document.get('city') == created_document.get('city')
        assert read_document.get('zipcode') == created_document.get('zipcode')

        # Read document feed doesn't require partitionKey as it's always a cross partition query
        documentlist = [document async for document in created_collection.read_all_items()]
        assert 1 == len(documentlist)

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
        document_definition['city'] = 'Atlanta'
        document_definition['zipcode'] = '30363'

        upserted_document = await created_collection.upsert_item(body=document_definition)

        assert upserted_document.get('id') == document_definition.get('id')
        assert upserted_document.get('key') == document_definition.get('key')
        assert upserted_document.get('city') == document_definition.get('city')
        assert upserted_document.get('zipcode') == document_definition.get('zipcode')

        documentlist = [document async for document in created_collection.read_all_items()]
        assert 2 == len(documentlist)

        # delete document
        await created_collection.delete_item(item=upserted_document, partition_key=[upserted_document.get('city'),
                                                                                    upserted_document.get('zipcode')])

        # query document on the partition key specified in the predicate will pass even without setting
        # enableCrossPartitionQuery or passing in the partitionKey value
        documentlist = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.city=\'' + replaced_document.get(
                'city') + '\' and r.zipcode=\'' + replaced_document.get('zipcode') + '\''
            # pylint: disable=line-too-long
        )]
        assert 1 == len(documentlist)

        # cross partition query
        documentlist = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
        )]

        assert 1 == len(documentlist)

        # query document by providing the partitionKey value
        documentlist = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            partition_key=[replaced_document.get('city'), replaced_document.get('zipcode')]
        )]

        assert 1 == len(documentlist)

        # Using incomplete extracted partition key in item body
        incomplete_document = {'id': 'document3',
                               'key': 'value3',
                               'city': 'Vancouver'}

        try:
            await created_collection.create_item(body=incomplete_document)
            self.fail("Test did not fail as expected")
        except exceptions.CosmosHttpResponseError as error:
            assert error.status_code == StatusCodes.BAD_REQUEST
            assert error.sub_status == SubStatusCodes.PARTITION_KEY_MISMATCH

        # using incomplete partition key in read item
        try:
            await created_collection.read_item(created_document, partition_key=["Redmond"])
            self.fail("Test did not fail as expected")
        except exceptions.CosmosHttpResponseError as error:
            assert error.status_code, StatusCodes.BAD_REQUEST
            assert error.sub_status == SubStatusCodes.PARTITION_KEY_MISMATCH

        # using mix value types for partition key
        doc_mixed_types = {'id': "doc4",
                           'key': 'value4',
                           'city': None,
                           'zipcode': 1000}
        created_mixed_type_doc = await created_collection.create_item(body=doc_mixed_types)
        assert doc_mixed_types.get('city') == created_mixed_type_doc.get('city')
        assert doc_mixed_types.get('zipcode') == created_mixed_type_doc.get('zipcode')
        # Known gap 23: Container delete and replace require preliminary metadata (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-23). On Rust this delete_container step first resolves container metadata (possible extra GET) before the DELETE; the step still executes.
        await self.key_database.delete_container(created_collection_ref.id)


if __name__ == "__main__":
    unittest.main()
