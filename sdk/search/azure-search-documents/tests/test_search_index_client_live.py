# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import(
    AnalyzeTextOptions,
    CorsOptions,
    SearchIndex,
    ScoringProfile,
    SimpleField,
    SearchFieldDataType
)
from azure.search.documents.indexes import SearchIndexClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from search_service_preparer import SearchEnvVarPreparer, search_decorator


class TestSearchIndexClient(AzureRecordedTestCase):

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy
    def test_search_index_client(self, **kwargs):
        api_key = kwargs.pop("api_key")
        endpoint = kwargs.pop("endpoint")
        index_name = kwargs.pop("index_name")
        client = SearchIndexClient(endpoint, api_key)
        index_name = "hotels"
        self._test_get_service_statistics(client)
        self._test_list_indexes_empty(client)
        self._test_create_index(client, index_name)
        self._test_list_indexes(client, index_name)
        self._test_get_index(client, index_name)
        self._test_get_index_statistics(client, index_name)
        self._test_delete_indexes_if_unchanged(client)
        self._test_create_or_update_index(client)
        self._test_create_or_update_indexes_if_unchanged(client)
        self._test_analyze_text(client, index_name)
        self._test_delete_indexes(client)

    def _test_get_service_statistics(self, client):
        result = client.get_service_statistics()
        assert isinstance(result, dict)
        assert set(result.keys()) == {"counters", "limits"}

    def _test_list_indexes_empty(self, client):
        result = client.list_indexes()
        with pytest.raises(StopIteration):
            next(result)

    def _test_list_indexes(self, client, index_name):
        result = client.list_indexes()
        first = next(result)
        assert first.name == index_name

        with pytest.raises(StopIteration):
            next(result)

    def _test_get_index(self, client, index_name):
        result = client.get_index(index_name)
        assert result.name == index_name

    def _test_get_index_statistics(self, client, index_name):
        result = client.get_index_statistics(index_name)
        assert set(result.keys()) == {'document_count', 'storage_size'}

    def _test_create_index(self, client, index_name):
        fields = [
            SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
            SimpleField(name="baseRate", type=SearchFieldDataType.Double)
        ]
        scoring_profile = ScoringProfile(
            name="MyProfile"
        )
        scoring_profiles = []
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        index = SearchIndex(
            name=index_name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        result = client.create_index(index)
        assert result.name == index_name
        assert result.scoring_profiles[0].name == scoring_profile.name
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds

    def _test_create_or_update_index(self, client):
        name = "hotels-cou"
        fields = [
            SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
            SimpleField(name="baseRate", type=SearchFieldDataType.Double)
        ]
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        scoring_profiles = []
        index = SearchIndex(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        result = client.create_or_update_index(index=index)
        assert len(result.scoring_profiles) == 0
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds
        scoring_profile = ScoringProfile(
            name="MyProfile"
        )
        scoring_profiles = []
        scoring_profiles.append(scoring_profile)
        index = SearchIndex(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        result = client.create_or_update_index(index=index)
        assert result.scoring_profiles[0].name == scoring_profile.name
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds

    def _test_create_or_update_indexes_if_unchanged(self, client):
        # First create an index
        name = "hotels-coa-unchanged"
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
        index = SearchIndex(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        result = client.create_index(index)
        etag = result.e_tag
        # get e tag  and update
        index.scoring_profiles = []
        client.create_or_update_index(index)

        index.e_tag = etag
        with pytest.raises(HttpResponseError):
            client.create_or_update_index(index, match_condition=MatchConditions.IfNotModified)

    def _test_analyze_text(self, client, index_name):
        analyze_request = AnalyzeTextOptions(text="One's <two/>", analyzer_name="standard.lucene")
        result = client.analyze_text(index_name, analyze_request)
        assert len(result.tokens) == 2

    def _test_delete_indexes_if_unchanged(self, client):
        # First create an index
        name = "hotels-del-unchanged"
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
        index = SearchIndex(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        result = client.create_index(index)
        etag = result.e_tag
        # get e tag  and update
        index.scoring_profiles = []
        client.create_or_update_index(index)

        index.e_tag = etag
        with pytest.raises(HttpResponseError):
            client.delete_index(index, match_condition=MatchConditions.IfNotModified)

    def _test_delete_indexes(self, client):
        for index in client.list_indexes():
            client.delete_index(index)
