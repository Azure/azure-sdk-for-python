# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from azure.core.exceptions import HttpResponseError
from azure.core import MatchConditions
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase

from search_service_preparer import SearchEnvVarPreparer, search_decorator
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import(
    AnalyzeTextOptions,
    CorsOptions,
    SearchIndex,
    ScoringProfile,
    SimpleField,
    SearchFieldDataType
)

class TestSearchIndexClientAsync(AzureRecordedTestCase):

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy_async
    async def test_search_index_client(self, **kwargs):
        api_key = kwargs.pop("api_key")
        endpoint = kwargs.pop("endpoint")
        index_name = kwargs.pop("index_name")
        client = SearchIndexClient(endpoint, api_key)
        index_name = "hotels"
        async with client:
            await self._test_get_service_statistics(client)
            await self._test_list_indexes_empty(client)
            await self._test_create_index(client, index_name)
            await self._test_list_indexes(client, index_name)
            await self._test_get_index(client, index_name)
            await self._test_get_index_statistics(client, index_name)
            await self._test_delete_indexes_if_unchanged(client)
            await self._test_create_or_update_index(client)
            await self._test_create_or_update_indexes_if_unchanged(client)
            await self._test_analyze_text(client, index_name)
            await self._test_delete_indexes(client)

    async def _test_get_service_statistics(self, client):
        result = await client.get_service_statistics()
        assert isinstance(result, dict)
        assert set(result.keys()) == {"counters", "limits"}

    async def _test_list_indexes_empty(self, client):
        result = client.list_indexes()
        with pytest.raises(StopAsyncIteration):
            await result.__anext__()

    async def _test_create_index(self, client, index_name):
        fields = fields = [
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
        result = await client.create_index(index)
        assert result.name == "hotels"
        assert result.scoring_profiles[0].name == scoring_profile.name
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds

    async def _test_list_indexes(self, client, index_name):
        result = client.list_indexes()
        first = await result.__anext__()
        assert first.name == index_name
        with pytest.raises(StopAsyncIteration):
            await result.__anext__()

    async def _test_get_index(self, client, index_name):
        result = await client.get_index(index_name)
        assert result.name == index_name

    async def _test_get_index_statistics(self, client, index_name):
        result = await client.get_index_statistics(index_name)
        assert set(result.keys()) == {'document_count', 'storage_size'}

    async def _test_delete_indexes_if_unchanged(self, client):
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
        result = await client.create_index(index)
        etag = result.e_tag
        # get eTag and update
        index.scoring_profiles = []
        await client.create_or_update_index(index)

        index.e_tag = etag
        with pytest.raises(HttpResponseError):
            await client.delete_index(index, match_condition=MatchConditions.IfNotModified)

    async def _test_create_or_update_index(self, client):
        name = "hotels-cou"
        fields = fields = [
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
        result = await client.create_or_update_index(index=index)
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
        result = await client.create_or_update_index(index=index)
        assert result.scoring_profiles[0].name == scoring_profile.name
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds

    async def _test_create_or_update_indexes_if_unchanged(self, client):
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
        result = await client.create_index(index)
        etag = result.e_tag
        # get eTag and update
        index.scoring_profiles = []
        await client.create_or_update_index(index)

        index.e_tag = etag
        with pytest.raises(HttpResponseError):
            await client.create_or_update_index(index, match_condition=MatchConditions.IfNotModified)

    async def _test_analyze_text(self, client, index_name):
        analyze_request = AnalyzeTextOptions(text="One's <two/>", analyzer_name="standard.lucene")
        result = await client.analyze_text(index_name, analyze_request)
        assert len(result.tokens) == 2

    async def _test_delete_indexes(self, client):
        result = client.list_indexes()
        async for index in result:
            await client.delete_index(index.name)
