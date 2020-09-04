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
from azure.search.documents import SearchClient

TIME_TO_SLEEP = 3

class SearchClientTest(AzureMgmtTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['api-key']

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_document_count(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        assert client.get_document_count() == 10

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_document(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        for hotel_id in range(1, 11):
            result = client.get_document(key=str(hotel_id))
            expected = BATCH["value"][hotel_id - 1]
            assert result.get("hotelId") == expected.get("hotelId")
            assert result.get("hotelName") == expected.get("hotelName")
            assert result.get("description") == expected.get("description")

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_document_missing(self, api_key, endpoint, index_name, **kwargs):
        client = SearchClient(
            endpoint, index_name, AzureKeyCredential(api_key)
        )
        with pytest.raises(HttpResponseError):
            client.get_document(key="1000")
