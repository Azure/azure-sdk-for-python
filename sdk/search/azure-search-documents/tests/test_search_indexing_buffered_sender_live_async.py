# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async live tests for ``SearchIndexingBufferedSender`` queueing and flush behavior."""

from __future__ import annotations

import pytest

from azure.core.exceptions import HttpResponseError
from azure.search.documents import IndexDocumentsBatch
from devtools_testutils import AzureRecordedTestCase

from _search_helpers import (
    HOTEL_DOCUMENT_COUNT,
    HOTEL_NAME,
    MISSING_HOTEL_ID,
    REPLACEMENT_HOTEL_NAME,
    build_hotel_document,
)
from _search_helpers_async import hotel_index_with_buffered_sender, live_test, wait_for_live_indexing

BATCH_ACTION_COUNT = 2


async def _assert_missing(search_client, hotel_id):
    with pytest.raises(HttpResponseError):
        await search_client.get_document(key=hotel_id)


class TestSearchIndexingBufferedSenderAsync(AzureRecordedTestCase):
    async def _wait_for_indexing(self):
        await wait_for_live_indexing(self)

    @live_test()
    async def test_upload_documents_flushes_actions_and_adds_documents(self, endpoint):
        index_name = self.get_resource_name("index-buffered-upload-documents")

        async with hotel_index_with_buffered_sender(
            self,
            endpoint,
            index_name,
            auto_flush=False,
        ) as (search_client, buffered_sender):
            documents = [
                build_hotel_document("1000", rating=5),
                build_hotel_document("3", rating=4, hotel_name=REPLACEMENT_HOTEL_NAME),
            ]

            await buffered_sender.upload_documents(documents)
            await buffered_sender.flush()
            await self._wait_for_indexing()

            assert await search_client.get_document_count() == HOTEL_DOCUMENT_COUNT + 1
            assert (await search_client.get_document(key="1000"))["Rating"] == 5
            assert (await search_client.get_document(key="3"))["HotelName"] == REPLACEMENT_HOTEL_NAME

    @live_test()
    async def test_upload_documents_auto_flushes_when_batch_action_count_is_reached(self, endpoint):
        index_name = self.get_resource_name("index-buffered-upload-documents-auto-flush")

        async with hotel_index_with_buffered_sender(
            self,
            endpoint,
            index_name,
            initial_batch_action_count=BATCH_ACTION_COUNT,
        ) as (search_client, buffered_sender):
            await buffered_sender.upload_documents(
                [build_hotel_document("1000", rating=5), build_hotel_document("1001", rating=4)]
            )
            await self._wait_for_indexing()

            assert await search_client.get_document_count() == HOTEL_DOCUMENT_COUNT + 2

    @live_test()
    async def test_delete_documents_flushes_existing_and_invalid_keys(self, endpoint):
        index_name = self.get_resource_name("index-buffered-delete-documents")

        async with hotel_index_with_buffered_sender(self, endpoint, index_name, auto_flush=False) as (
            search_client,
            buffered_sender,
        ):
            await buffered_sender.delete_documents([{"HotelId": "3"}, {"HotelId": "4"}, {"HotelId": MISSING_HOTEL_ID}])

            assert await buffered_sender.flush() is False
            await self._wait_for_indexing()

            assert await search_client.get_document_count() == HOTEL_DOCUMENT_COUNT - 2
            await _assert_missing(search_client, "3")
            await _assert_missing(search_client, "4")
            await _assert_missing(search_client, MISSING_HOTEL_ID)

    @live_test()
    async def test_merge_documents_flushes_existing_document_and_reports_missing_key_failure(self, endpoint):
        index_name = self.get_resource_name("index-buffered-merge-documents-invalid-key")

        async with hotel_index_with_buffered_sender(
            self,
            endpoint,
            index_name,
            auto_flush=False,
        ) as (search_client, buffered_sender):
            await buffered_sender.merge_documents(
                [{"HotelId": "5", "Rating": 1}, {"HotelId": MISSING_HOTEL_ID, "Rating": 2}]
            )

            has_error = await buffered_sender.flush()
            if self.is_live:
                assert has_error is True
            await self._wait_for_indexing()

            assert await search_client.get_document_count() == HOTEL_DOCUMENT_COUNT
            assert (await search_client.get_document(key="5"))["Rating"] == 1
            await _assert_missing(search_client, MISSING_HOTEL_ID)

    @live_test()
    async def test_merge_or_upload_documents_flushes_existing_and_missing_documents(self, endpoint):
        index_name = self.get_resource_name("index-buffered-merge-or-upload-documents")

        async with hotel_index_with_buffered_sender(self, endpoint, index_name, auto_flush=False) as (
            search_client,
            buffered_sender,
        ):
            await buffered_sender.merge_or_upload_documents(
                [{"HotelId": "1", "Rating": 2}, {"HotelId": MISSING_HOTEL_ID, "Rating": 1}]
            )

            assert await buffered_sender.flush() is False
            await self._wait_for_indexing()

            assert await search_client.get_document_count() == HOTEL_DOCUMENT_COUNT + 1
            assert (await search_client.get_document(key="1"))["Rating"] == 2
            assert (await search_client.get_document(key=MISSING_HOTEL_ID))["Rating"] == 1

    @live_test()
    async def test_index_documents_flushes_batch_actions(self, endpoint):
        index_name = self.get_resource_name("index-buffered-index-documents")

        async with hotel_index_with_buffered_sender(self, endpoint, index_name, auto_flush=False) as (
            search_client,
            buffered_sender,
        ):
            batch = IndexDocumentsBatch()
            batch.add_upload_actions([build_hotel_document("1000", rating=5)])
            batch.add_merge_actions([{"HotelId": "3", "Rating": 2}])

            results = await buffered_sender.index_documents(batch)
            await self._wait_for_indexing()

            assert len(results) == 2
            assert all(result.succeeded for result in results)
            assert await search_client.get_document_count() == HOTEL_DOCUMENT_COUNT + 1
            assert (await search_client.get_document(key="1000"))["HotelName"] == HOTEL_NAME
            assert (await search_client.get_document(key="3"))["Rating"] == 2
