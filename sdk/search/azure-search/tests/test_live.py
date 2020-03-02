# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from os.path import dirname, join, realpath

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

from consts import SERVICE_URL, TEST_SERVICE_NAME
from search_service_preparer import SearchServicePreparer

CWD = dirname(realpath(__file__))

SCHEMA = open(join(CWD, "hotel_schema.json")).read()
BATCH = json.load(open(join(CWD, "hotel_small.json")))

from azure.search import SearchIndexClient, SearchApiKeyCredential


class SearchIndexClientTest(AzureMgmtTestCase):
    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_basic(self, api_key, index_name, **kwargs):
        client = SearchIndexClient(
            TEST_SERVICE_NAME, index_name, SearchApiKeyCredential(api_key)
        )
        assert client.get_document_count() == 10
