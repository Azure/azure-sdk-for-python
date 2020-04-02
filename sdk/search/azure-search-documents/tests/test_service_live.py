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

from search_service_preparer import SearchServicePreparer

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.search.documents import(
    SearchServiceClient,
    Field,
    Index,
    AnalyzeRequest,
    AnalyzeResult,
    ScoringProfile,
    CorsOptions,
)

CWD = dirname(realpath(__file__))
SCHEMA = open(join(CWD, "hotel_schema.json")).read()
BATCH = json.load(open(join(CWD, "hotel_small.json")))
TIME_TO_SLEEP = 5

class SearchIndexClientTest(AzureMgmtTestCase):
    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer()
    def test_get_service_statistics(self, api_key, endpoint, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.get_service_statistics()
        assert isinstance(result, dict)
        assert set(result.keys()) == {"counters", "limits"}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer()
    def test_list_indexes_empty(self, api_key, endpoint, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.list_indexes()
        assert len(result) == 0

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_list_indexes(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.list_indexes()
        assert len(result) == 1
        assert result[0].name == index_name

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_index(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.get_index(index_name)
        assert result.name == index_name

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_index_statistics(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.get_index_statistics(index_name)
        assert set(result.keys()) == {'document_count', 'storage_size'}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_indexes(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        client.delete_index(index_name)
        import time
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)
        result = client.list_indexes()
        assert len(result) == 0

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_index(self, api_key, endpoint, index_name, **kwargs):
        name = "hotels"
        fields = [
        {
          "name": "hotelId",
          "type": "Edm.String",
          "key": True,
          "searchable": False
        },
        {
          "name": "baseRate",
          "type": "Edm.Double"
        }]
        scoring_profile = ScoringProfile(
            name="MyProfile"
        )
        scoring_profiles = []
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        index = Index(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.create_index(index)
        assert result.name == "hotels"
        assert result.scoring_profiles[0].name == scoring_profile.name
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_index(self, api_key, endpoint, index_name, **kwargs):
        name = "hotels"
        fields = [
            {
                "name": "hotelId",
                "type": "Edm.String",
                "key": True,
                "searchable": False
            },
            {
                "name": "baseRate",
                "type": "Edm.Double"
            }]
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        scoring_profiles = []
        index = Index(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.create_or_update_index(index_name=index.name, index=index)
        assert len(result.scoring_profiles) == 0
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds
        scoring_profile = ScoringProfile(
            name="MyProfile"
        )
        scoring_profiles = []
        scoring_profiles.append(scoring_profile)
        index = Index(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        result = client.create_or_update_index(index_name=index.name, index=index)
        assert result.scoring_profiles[0].name == scoring_profile.name
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_analyze_text(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        analyze_request = AnalyzeRequest(text="One's <two/>", analyzer="standard.lucene")
        result = client.analyze_text(index_name, analyze_request)
        assert len(result.tokens) == 2
