# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from os.path import dirname, join, realpath

import pytest

from devtools_testutils import AzureMgmtTestCase
from azure_devtools.scenario_tests import ReplayableTest
from search_service_preparer import SearchServicePreparer, SearchResourceGroupPreparer

from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import(
    SynonymMap,
)
from azure.search.documents.indexes import SearchIndexClient

CWD = dirname(realpath(__file__))
SCHEMA = open(join(CWD, "hotel_schema.json")).read()
try:
    BATCH = json.load(open(join(CWD, "hotel_small.json")))
except UnicodeDecodeError:
    BATCH = json.load(open(join(CWD, "hotel_small.json"), encoding='utf-8'))
TIME_TO_SLEEP = 5
CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=storagename;AccountKey=NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==;EndpointSuffix=core.windows.net'

class SearchSynonymMapsClientTest(AzureMgmtTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['api-key']

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_synonym_map(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(endpoint, AzureKeyCredential(api_key))
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name="test-syn-map", synonyms=synonyms)
        result = client.create_synonym_map(synonym_map)
        assert isinstance(result, SynonymMap)
        assert result.name == "test-syn-map"
        assert result.synonyms == [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        assert len(client.get_synonym_maps()) == 1

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_synonym_map(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(endpoint, AzureKeyCredential(api_key))
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name="test-syn-map", synonyms=synonyms)
        result = client.create_synonym_map(synonym_map)
        assert len(client.get_synonym_maps()) == 1
        client.delete_synonym_map("test-syn-map")
        assert len(client.get_synonym_maps()) == 0

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_synonym_map_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(endpoint, AzureKeyCredential(api_key))
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name="test-syn-map", synonyms=synonyms)
        result = client.create_synonym_map(synonym_map)
        etag = result.e_tag

        synonym_map.synonyms = "\n".join([
            "Washington, Wash. => WA",
        ])
        client.create_or_update_synonym_map(synonym_map)

        result.e_tag = etag
        with pytest.raises(HttpResponseError):
            client.delete_synonym_map(result, match_condition=MatchConditions.IfNotModified)
            assert len(client.get_synonym_maps()) == 1

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_synonym_map(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(endpoint, AzureKeyCredential(api_key))
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name="test-syn-map", synonyms=synonyms)
        client.create_synonym_map(synonym_map)
        assert len(client.get_synonym_maps()) == 1
        result = client.get_synonym_map("test-syn-map")
        assert isinstance(result, SynonymMap)
        assert result.name == "test-syn-map"
        assert result.synonyms == [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_synonym_maps(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(endpoint, AzureKeyCredential(api_key))
        synonyms = [
            "USA, United States, United States of America",
        ]
        synonym_map_1 = SynonymMap(name="test-syn-map-1", synonyms=synonyms)
        client.create_synonym_map(synonym_map_1)
        synonyms = [
            "Washington, Wash. => WA",
        ]
        synonym_map_2 = SynonymMap(name="test-syn-map-2", synonyms=synonyms)
        client.create_synonym_map(synonym_map_2)
        result = client.get_synonym_maps()
        assert isinstance(result, list)
        assert all(isinstance(x, SynonymMap) for x in result)
        assert set(x.name for x in result) == {"test-syn-map-1", "test-syn-map-2"}

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_synonym_map(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(endpoint, AzureKeyCredential(api_key))
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name="test-syn-map", synonyms=synonyms)
        client.create_synonym_map(synonym_map)
        assert len(client.get_synonym_maps()) == 1
        synonym_map.synonyms = ["Washington, Wash. => WA",]
        client.create_or_update_synonym_map(synonym_map)
        assert len(client.get_synonym_maps()) == 1
        result = client.get_synonym_map("test-syn-map")
        assert isinstance(result, SynonymMap)
        assert result.name == "test-syn-map"
        assert result.synonyms == [
            "Washington, Wash. => WA",
        ]

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_synonym_map_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexClient(endpoint, AzureKeyCredential(api_key))
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name="test-syn-map", synonyms=synonyms)
        result = client.create_synonym_map(synonym_map)
        etag = result.e_tag

        synonym_map.synonyms = [
            "Washington, Wash. => WA",
        ]

        client.create_or_update_synonym_map(synonym_map)

        result.e_tag = etag
        with pytest.raises(HttpResponseError):
            client.create_or_update_synonym_map(result, match_condition=MatchConditions.IfNotModified)
