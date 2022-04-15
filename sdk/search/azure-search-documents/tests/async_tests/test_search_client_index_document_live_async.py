# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from pydoc import doc
import pytest
import time
from azure.core.exceptions import HttpResponseError
from azure.search.documents.aio import SearchClient
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from search_service_preparer import SearchEnvVarPreparer, search_decorator

TIME_TO_SLEEP = 3


class TestSearchClientDocumentsAsync(AzureRecordedTestCase):

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy_async
    async def test_search_client_index_document(self, endpoint, api_key, index_name):
        client = SearchClient(endpoint, index_name, api_key)
        doc_count = 10
        async with client:
            doc_count = await self._test_upload_documents_new(client, doc_count)
            doc_count = await self._test_upload_documents_existing(client, doc_count)
            doc_count = await self._test_delete_documents_existing(client, doc_count)
            doc_count = await self._test_delete_documents_missing(client, doc_count)
            doc_count = await self._test_merge_documents_existing(client, doc_count)
            doc_count = await self._test_merge_documents_missing(client, doc_count)
            doc_count = await self._test_merge_or_upload_documents(client, doc_count)

    async def _test_upload_documents_new(self, client, doc_count):
        docs = [
            {"hotelId": "1000", "rating": 5, "rooms": [], "hotelName": "Azure Inn"},
            {"hotelId": "1001", "rating": 4, "rooms": [], "hotelName": "Redmond Hotel"},
        ]
        results = await client.upload_documents(docs)
        assert len(results) == len(docs)
        assert set(x.status_code for x in results) == {201}
        doc_count += len(docs)

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

    async def _test_upload_documents_existing(self, client, doc_count):
        # add one new and one existing
        docs = [
            {"hotelId": "1002", "rating": 5, "rooms": [], "hotelName": "Azure Inn"},
            {"hotelId": "3", "rating": 4, "rooms": [], "hotelName": "Redmond Hotel"},
        ]
        results = await client.upload_documents(docs)
        assert len(results) == len(docs)
        doc_count += 1
        assert set(x.status_code for x in results) == {200, 201}
        return doc_count

    async def _test_delete_documents_existing(self, client, doc_count):
        docs = [{"hotelId": "3"}, {"hotelId": "4"}]
        results = await client.delete_documents(docs)
        assert len(results) == len(docs)
        assert set(x.status_code for x in results) == {200}
        doc_count -= len(docs)

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert await client.get_document_count() == doc_count

        with pytest.raises(HttpResponseError):
            await client.get_document(key="3")

        with pytest.raises(HttpResponseError):
            await client.get_document(key="4")
        return doc_count

    async def _test_delete_documents_missing(self, client, doc_count):
        # delete one existing and one missing
        docs = [{"hotelId": "1003"}, {"hotelId": "2"}]
        results = await client.delete_documents(docs)
        assert len(results) == len(docs)
        assert set(x.status_code for x in results) == {200}
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

    async def _test_merge_documents_existing(self, client, doc_count):
        docs = [{"hotelId": "5", "rating": 1}, {"hotelId": "6", "rating": 2}]
        results = await client.merge_documents(docs)
        assert len(results) == len(docs)
        assert set(x.status_code for x in results) == {200}

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert await client.get_document_count() == doc_count

        result = await client.get_document(key="5")
        assert result["rating"] == 1

        result = await client.get_document(key="6")
        assert result["rating"] == 2
        return doc_count

    async def _test_merge_documents_missing(self, client, doc_count):
        # merge to one existing and one missing document
        docs = [{"hotelId": "1003", "rating": 1}, {"hotelId": "1", "rating": 2}]
        results = await client.merge_documents(docs)
        assert len(results) == len(docs)
        assert set(x.status_code for x in results) == {200, 404}

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert await client.get_document_count() == doc_count

        with pytest.raises(HttpResponseError):
            await client.get_document(key="1003")

        result = await client.get_document(key="1")
        assert result["rating"] == 2
        return doc_count

    async def _test_merge_or_upload_documents(self, client, doc_count):
        # merge to one existing and one missing
        docs = [{"hotelId": "1003", "rating": 1}, {"hotelId": "1", "rating": 2}]
        results = await client.merge_or_upload_documents(docs)
        assert len(results) == len(docs)
        assert set(x.status_code for x in results) == {200, 201}
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
