# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import time
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchIndexingBufferedSender, SearchClient
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from search_service_preparer import SearchEnvVarPreparer, search_decorator

TIME_TO_SLEEP = 3


class TestSearchIndexingBufferedSenderAsync(AzureRecordedTestCase):

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy_async
    async def test_search_client_index_buffered_sender(self, endpoint, api_key, index_name):
        client = SearchClient(endpoint, index_name, api_key)
        batch_client = SearchIndexingBufferedSender(endpoint, index_name, api_key)
        try:
            async with client:
                async with batch_client:
                    doc_count = 10
                    doc_count = await self._test_upload_documents_new(client, batch_client, doc_count)
                    doc_count = await self._test_upload_documents_existing(client, batch_client, doc_count)
                    doc_count = await self._test_delete_documents_existing(client, batch_client, doc_count)
                    doc_count = await self._test_delete_documents_missing(client, batch_client, doc_count)
                    doc_count = await self._test_merge_documents_existing(client, batch_client, doc_count)
                    doc_count = await self._test_merge_documents_missing(client, batch_client, doc_count)
                    doc_count = await self._test_merge_or_upload_documents(client, batch_client, doc_count)
        finally:
            batch_client.close()

    async def _test_upload_documents_new(self, client, batch_client, doc_count):
        batch_client._batch_action_count = 2
        docs = [
            {"hotelId": "1000", "rating": 5, "rooms": [], "hotelName": "Azure Inn"},
            {"hotelId": "1001", "rating": 4, "rooms": [], "hotelName": "Redmond Hotel"},
        ]
        await batch_client.upload_documents(docs)
        doc_count += 2

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert await client.get_document_count() == doc_count
        for doc in docs:
            result = await client.get_document(key=doc["hotelId"])
            assert result["hotelId"] == doc["hotelId"]
            assert result["hotelName"] == doc["hotelName"]
            assert result["rating"] == doc["rating"]
            assert result["rooms"] == doc["rooms"]
        return doc_count

    async def _test_upload_documents_existing(self, client, batch_client, doc_count):
        batch_client._batch_action_count = 2
        # add one new and one existing
        docs = [
            {"hotelId": "1002", "rating": 5, "rooms": [], "hotelName": "Azure Inn"},
            {"hotelId": "3", "rating": 4, "rooms": [], "hotelName": "Redmond Hotel"},
        ]
        await batch_client.upload_documents(docs)
        doc_count += 1

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert await client.get_document_count() == doc_count
        return doc_count

    async def _test_delete_documents_existing(self, client, batch_client, doc_count):
        batch_client._batch_action_count = 2
        docs = [{"hotelId": "3"}, {"hotelId": "4"}]
        await batch_client.delete_documents(docs)
        doc_count -= 2

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert await client.get_document_count() == doc_count

        with pytest.raises(HttpResponseError):
            await client.get_document(key="3")

        with pytest.raises(HttpResponseError):
            await client.get_document(key="4")
        return doc_count

    async def _test_delete_documents_missing(self, client, batch_client, doc_count):
        batch_client._batch_action_count = 2
        # delete one existing and one missing
        docs = [{"hotelId": "1003"}, {"hotelId": "2"}]
        await batch_client.delete_documents(docs)
        doc_count -= 1

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert await client.get_document_count() == doc_count
        with pytest.raises(HttpResponseError):
            await client.get_document(key="1003")
        with pytest.raises(HttpResponseError):
            await client.get_document(key="2")
        return doc_count

    async def _test_merge_documents_existing(self, client, batch_client, doc_count):
        batch_client._batch_action_count = 2
        docs = [{"hotelId": "5", "rating": 1}, {"hotelId": "6", "rating": 2}]
        await batch_client.merge_documents(docs)

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert await client.get_document_count() == doc_count

        result = await client.get_document(key="5")
        assert result["rating"] == 1

        result = await client.get_document(key="6")
        assert result["rating"] == 2
        return doc_count

    async def _test_merge_documents_missing(self, client, batch_client, doc_count):
        batch_client._batch_action_count = 2
        # merge to one existing and one missing document
        docs = [{"hotelId": "1003", "rating": 1}, {"hotelId": "1", "rating": 2}]
        await batch_client.merge_documents(docs)

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert await client.get_document_count() == doc_count

        with pytest.raises(HttpResponseError):
            await client.get_document(key="1003")

        result = await client.get_document(key="1")
        assert result["rating"] == 2
        return doc_count

    async def _test_merge_or_upload_documents(self, client, batch_client, doc_count):
        batch_client._batch_action_count = 2
        # merge to one existing and one missing
        docs = [{"hotelId": "1003", "rating": 1}, {"hotelId": "1", "rating": 2}]
        await batch_client.merge_or_upload_documents(docs)
        doc_count += 1

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert await client.get_document_count() == doc_count

        result = await client.get_document(key="1003")
        assert result["rating"] == 1

        result = await client.get_document(key="1")
        assert result["rating"] == 2
        return doc_count
