# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from os.path import dirname, join, realpath
import time

import pytest

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from azure_devtools.scenario_tests import ReplayableTest

from search_service_preparer import SearchServicePreparer

CWD = dirname(realpath(__file__))

SCHEMA = open(join(CWD, "hotel_schema.json")).read()
try:
    BATCH = json.load(open(join(CWD, "hotel_small.json")))
except UnicodeDecodeError:
    BATCH = json.load(open(join(CWD, "hotel_small.json"), encoding='utf-8'))
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchIndexingBufferedSender, SearchClient

TIME_TO_SLEEP = 3

class SearchIndexingBufferedSenderTest(AzureMgmtTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['api-key']

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_upload_documents_new(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client = SearchIndexingBufferedSender(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client._batch_action_count = 2
        DOCUMENTS = [
            {"hotelId": "1000", "rating": 5, "rooms": [], "hotelName": "Azure Inn"},
            {"hotelId": "1001", "rating": 4, "rooms": [], "hotelName": "Redmond Hotel"},
        ]
        batch_client.upload_documents(DOCUMENTS)

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 12
        for doc in DOCUMENTS:
            result = client.get_document(key=doc["hotelId"])
            assert result["hotelId"] == doc["hotelId"]
            assert result["hotelName"] == doc["hotelName"]
            assert result["rating"] == doc["rating"]
            assert result["rooms"] == doc["rooms"]
        batch_client.close()

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_upload_documents_existing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client = SearchIndexingBufferedSender(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client._batch_action_count = 2
        DOCUMENTS = [
            {"hotelId": "1000", "rating": 5, "rooms": [], "hotelName": "Azure Inn"},
            {"hotelId": "3", "rating": 4, "rooms": [], "hotelName": "Redmond Hotel"},
        ]
        batch_client.upload_documents(DOCUMENTS)

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 11
        batch_client.close()


    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_documents_existing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client = SearchIndexingBufferedSender(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client._batch_action_count = 2
        batch_client.delete_documents([{"hotelId": "3"}, {"hotelId": "4"}])
        batch_client.close()

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 8

        with pytest.raises(HttpResponseError):
            client.get_document(key="3")

        with pytest.raises(HttpResponseError):
            client.get_document(key="4")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_documents_missing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client = SearchIndexingBufferedSender(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client._batch_action_count = 2
        batch_client.delete_documents([{"hotelId": "1000"}, {"hotelId": "4"}])
        batch_client.close()

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 9

        with pytest.raises(HttpResponseError):
            client.get_document(key="1000")

        with pytest.raises(HttpResponseError):
            client.get_document(key="4")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_merge_documents_existing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client = SearchIndexingBufferedSender(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client._batch_action_count = 2
        batch_client.merge_documents(
            [{"hotelId": "3", "rating": 1}, {"hotelId": "4", "rating": 2}]
        )
        batch_client.close()

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 10

        result = client.get_document(key="3")
        assert result["rating"] == 1

        result = client.get_document(key="4")
        assert result["rating"] == 2

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_merge_documents_missing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client = SearchIndexingBufferedSender(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client._batch_action_count = 2
        batch_client.merge_documents(
            [{"hotelId": "1000", "rating": 1}, {"hotelId": "4", "rating": 2}]
        )
        batch_client.close()

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 10

        with pytest.raises(HttpResponseError):
            client.get_document(key="1000")

        result = client.get_document(key="4")
        assert result["rating"] == 2

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_merge_or_upload_documents(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client = SearchIndexingBufferedSender(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        batch_client._batch_action_count = 2
        batch_client.merge_or_upload_documents(
            [{"hotelId": "1000", "rating": 1}, {"hotelId": "4", "rating": 2}]
        )
        batch_client.close()

        # There can be some lag before a document is searchable
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)

        assert client.get_document_count() == 11

        result = client.get_document(key="1000")
        assert result["rating"] == 1

        result = client.get_document(key="4")
        assert result["rating"] == 2
