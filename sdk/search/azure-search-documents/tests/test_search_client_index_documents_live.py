# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``SearchClient`` document indexing operations."""

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
    hotel_index,
    live_test,
    wait_for_live_indexing,
)


def _assert_missing(search_client, hotel_id):
    with pytest.raises(HttpResponseError):
        search_client.get_document(key=hotel_id)


class TestSearchClientIndexDocuments(AzureRecordedTestCase):
    def _wait_for_indexing(self):
        wait_for_live_indexing(self)

    @live_test()
    def test_index_documents_sends_batch_actions(self, endpoint):
        index_name = self.get_resource_name("index-index-documents")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            batch = IndexDocumentsBatch()
            batch.add_upload_actions(
                [build_hotel_document("1000", rating=5), build_hotel_document("1001", rating=4)]
            )
            batch.add_delete_actions([{"HotelId": "2"}])
            batch.add_merge_actions([{"HotelId": "3", "Rating": 1}])

            results = search_client.index_documents(batch)
            self._wait_for_indexing()

            assert len(results) == 4
            assert all(result.succeeded for result in results)
            assert search_client.get_document_count() == HOTEL_DOCUMENT_COUNT + 1
            assert search_client.get_document(key="1000")["HotelName"] == HOTEL_NAME
            assert search_client.get_document(key="1001")["Rating"] == 4
            assert search_client.get_document(key="3")["Rating"] == 1
            _assert_missing(search_client, "2")

    @live_test()
    def test_upload_documents_creates_new_documents(self, endpoint):
        index_name = self.get_resource_name("index-upload-documents-new")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            documents = [
                build_hotel_document("1000", rating=5),
                build_hotel_document("1001", rating=4, hotel_name=REPLACEMENT_HOTEL_NAME),
            ]

            results = search_client.upload_documents(documents)
            self._wait_for_indexing()

            assert len(results) == len(documents)
            assert {result.status_code for result in results} == {201}
            assert search_client.get_document_count() == HOTEL_DOCUMENT_COUNT + len(documents)
            assert search_client.get_document(key="1000")["HotelName"] == HOTEL_NAME
            assert search_client.get_document(key="1001")["HotelName"] == REPLACEMENT_HOTEL_NAME

    @live_test()
    def test_upload_documents_replaces_existing_documents(self, endpoint):
        index_name = self.get_resource_name("index-upload-documents-existing")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            documents = [
                build_hotel_document("3", rating=4, hotel_name=REPLACEMENT_HOTEL_NAME),
                build_hotel_document("1000", rating=5),
            ]

            results = search_client.upload_documents(documents)
            self._wait_for_indexing()

            assert len(results) == len(documents)
            assert {result.status_code for result in results} == {200, 201}
            assert search_client.get_document_count() == HOTEL_DOCUMENT_COUNT + 1
            assert search_client.get_document(key="3")["HotelName"] == REPLACEMENT_HOTEL_NAME

    @live_test()
    def test_delete_documents_removes_existing_documents(self, endpoint):
        index_name = self.get_resource_name("index-delete-documents-existing")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = search_client.delete_documents([{"HotelId": "3"}, {"HotelId": "4"}])
            self._wait_for_indexing()

            assert len(results) == 2
            assert {result.status_code for result in results} == {200}
            assert search_client.get_document_count() == HOTEL_DOCUMENT_COUNT - 2
            _assert_missing(search_client, "3")
            _assert_missing(search_client, "4")

    @live_test()
    def test_delete_documents_succeeds_for_invalid_key(self, endpoint):
        index_name = self.get_resource_name("index-delete-documents-invalid-key")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = search_client.delete_documents([{"HotelId": MISSING_HOTEL_ID}, {"HotelId": "2"}])
            self._wait_for_indexing()

            assert len(results) == 2
            assert {result.status_code for result in results} == {200}
            assert search_client.get_document_count() == HOTEL_DOCUMENT_COUNT - 1
            _assert_missing(search_client, MISSING_HOTEL_ID)
            _assert_missing(search_client, "2")

    @live_test()
    def test_merge_documents_updates_existing_documents(self, endpoint):
        index_name = self.get_resource_name("index-merge-documents-existing")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = search_client.merge_documents(
                [{"HotelId": "5", "Rating": 1}, {"HotelId": "6", "Rating": 2}]
            )
            self._wait_for_indexing()

            assert len(results) == 2
            assert {result.status_code for result in results} == {200}
            assert search_client.get_document_count() == HOTEL_DOCUMENT_COUNT
            assert search_client.get_document(key="5")["Rating"] == 1
            assert search_client.get_document(key="6")["Rating"] == 2

    @live_test()
    def test_merge_documents_reports_invalid_key(self, endpoint):
        index_name = self.get_resource_name("index-merge-documents-invalid-key")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = search_client.merge_documents(
                [{"HotelId": MISSING_HOTEL_ID, "Rating": 1}, {"HotelId": "1", "Rating": 2}]
            )
            self._wait_for_indexing()

            assert len(results) == 2
            assert {result.status_code for result in results} == {200, 404}
            assert search_client.get_document_count() == HOTEL_DOCUMENT_COUNT
            _assert_missing(search_client, MISSING_HOTEL_ID)
            assert search_client.get_document(key="1")["Rating"] == 2

    @live_test()
    def test_merge_or_upload_documents_updates_existing_and_creates_missing(self, endpoint):
        index_name = self.get_resource_name("index-merge-or-upload-documents")

        with hotel_index(self, endpoint, index_name) as (search_client, _):
            results = search_client.merge_or_upload_documents(
                [{"HotelId": MISSING_HOTEL_ID, "Rating": 1}, {"HotelId": "1", "Rating": 2}]
            )
            self._wait_for_indexing()

            assert len(results) == 2
            assert {result.status_code for result in results} == {200, 201}
            assert search_client.get_document_count() == HOTEL_DOCUMENT_COUNT + 1
            assert search_client.get_document(key=MISSING_HOTEL_ID)["Rating"] == 1
            assert search_client.get_document(key="1")["Rating"] == 2
