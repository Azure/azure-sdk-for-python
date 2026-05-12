# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async live tests for ``SearchIndexClient`` index operations."""
from __future__ import annotations

from datetime import timedelta

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import (
    AnalyzeTextOptions,
    CorsOptions,
    FreshnessScoringFunction,
    FreshnessScoringParameters,
    ScoringFunctionAggregation,
    ScoringProfile,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
)
from devtools_testutils import AzureRecordedTestCase

from _search_helpers_async import live_test, make_index_client, safe_delete

INDEX_DESCRIPTION = "Hotel index"
REPLACEMENT_INDEX_DESCRIPTION = "Replacement hotel index"
CORS_OPTIONS = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
SCORING_PROFILE_NAME = "scoring-profile"
REPLACEMENT_SCORING_PROFILE_NAME = "replacement-scoring-profile"


def _build_hotel_fields():
    return [
        SimpleField(name="HotelId", type=SearchFieldDataType.STRING, key=True),
        SimpleField(name="BaseRate", type=SearchFieldDataType.DOUBLE),
    ]


def _build_hotel_index(
    index_name: str,
    *,
    description: str = INDEX_DESCRIPTION,
    scoring_profiles: list[ScoringProfile] | None = None,
    cors_options: CorsOptions | None = CORS_OPTIONS,
) -> SearchIndex:
    return SearchIndex(
        name=index_name,
        fields=_build_hotel_fields(),
        description=description,
        scoring_profiles=scoring_profiles or [],
        cors_options=cors_options,
    )


def _build_scoring_profile(profile_name: str) -> ScoringProfile:
    return ScoringProfile(name=profile_name)


async def _collect_async(async_iterable):
    return [item async for item in async_iterable]


class TestSearchIndexClientAsync(AzureRecordedTestCase):
    @live_test()
    async def test_get_service_statistics_returns_counters_and_limits(self, endpoint):
        client = make_index_client(endpoint)
        try:
            result = await client.get_service_statistics()
        finally:
            await client.close()

        assert "counters" in result
        assert "limits" in result

    @live_test()
    async def test_list_indexes_returns_empty_page_when_service_has_no_indexes(self, endpoint):
        client = make_index_client(endpoint)
        try:
            assert await _collect_async(client.list_indexes()) == []
        finally:
            await client.close()

    @live_test()
    async def test_create_get_list_statistics_analyze_and_delete_index(self, endpoint):
        client = make_index_client(endpoint)
        index_name = self.get_resource_name("index-create")
        try:
            created_index = await client.create_index(
                _build_hotel_index(index_name, scoring_profiles=[_build_scoring_profile(SCORING_PROFILE_NAME)])
            )

            assert created_index.name == index_name
            assert created_index.description == INDEX_DESCRIPTION
            assert created_index.scoring_profiles[0].name == SCORING_PROFILE_NAME
            assert created_index.cors_options.allowed_origins == CORS_OPTIONS.allowed_origins
            assert created_index.cors_options.max_age_in_seconds == CORS_OPTIONS.max_age_in_seconds

            retrieved_index = await client.get_index(index_name)
            assert retrieved_index.name == index_name
            assert retrieved_index.description == INDEX_DESCRIPTION

            index_names = set(await _collect_async(client.list_index_names()))
            assert index_name in index_names
            assert any(index.name == index_name for index in await _collect_async(client.list_indexes()))

            projected_indexes = await _collect_async(client.list_indexes(select=["name", "description"]))
            projected_index = next(index for index in projected_indexes if index.name == index_name)
            assert projected_index.description == INDEX_DESCRIPTION
            assert projected_index.fields == []

            statistics = await client.get_index_statistics(index_name)
            assert "documentCount" in statistics
            assert "storageSize" in statistics
            assert "vectorIndexSize" in statistics

            analyze_request = AnalyzeTextOptions(text="One's <two/>", analyzer_name="standard.lucene")
            analyze_result = await client.analyze_text(index_name, analyze_request)
            tokens = [token.token for token in analyze_result.tokens]
            assert len(tokens) == 2
            if self.is_live:
                assert tokens == ["one's", "two"]

            search_client = client.get_search_client(index_name)
            try:
                assert await search_client.get_document_count() == 0
            finally:
                await search_client.close()

            await client.delete_index(index_name)
            with pytest.raises(HttpResponseError):
                await client.get_index(index_name)
        finally:
            await safe_delete(client.delete_index, index_name)
            await client.close()

    @live_test()
    async def test_create_or_update_index_accepts_model_and_mapping(self, endpoint):
        client = make_index_client(endpoint)
        model_index_name = self.get_resource_name("index-create-or-update-model")
        mapping_index_name = self.get_resource_name("index-create-or-update-mapping")
        try:
            model_result = await client.create_or_update_index(_build_hotel_index(model_index_name))
            assert model_result.name == model_index_name
            assert model_result.description == INDEX_DESCRIPTION

            model_result.description = REPLACEMENT_INDEX_DESCRIPTION
            model_result.scoring_profiles = [_build_scoring_profile(REPLACEMENT_SCORING_PROFILE_NAME)]
            model_result = await client.create_or_update_index(model_result)
            assert model_result.description == REPLACEMENT_INDEX_DESCRIPTION
            assert model_result.scoring_profiles[0].name == REPLACEMENT_SCORING_PROFILE_NAME

            mapping = _build_hotel_index(mapping_index_name).as_dict()
            mapping_result = await client.create_or_update_index(mapping)
            assert mapping_result.name == mapping_index_name
            assert mapping_result.description == INDEX_DESCRIPTION
        finally:
            await safe_delete(client.delete_index, model_index_name)
            await safe_delete(client.delete_index, mapping_index_name)
            await client.close()

    @live_test()
    async def test_create_or_update_index_uses_model_etag_and_match_condition(self, endpoint):
        client = make_index_client(endpoint)
        index_name = self.get_resource_name("index-create-or-update-match-condition")
        try:
            index = await client.create_index(_build_hotel_index(index_name))
            original_e_tag = index.e_tag

            replacement_index = _build_hotel_index(index_name, description=REPLACEMENT_INDEX_DESCRIPTION)
            await client.create_or_update_index(replacement_index)

            index.e_tag = original_e_tag
            index.description = INDEX_DESCRIPTION
            with pytest.raises(HttpResponseError):
                await client.create_or_update_index(index, match_condition=MatchConditions.IfNotModified)
        finally:
            await safe_delete(client.delete_index, index_name)
            await client.close()

    @live_test()
    async def test_delete_index_accepts_model_etag_and_match_condition(self, endpoint):
        client = make_index_client(endpoint)
        index_name = self.get_resource_name("index-delete-match-condition")
        try:
            index = await client.create_index(_build_hotel_index(index_name))
            original_e_tag = index.e_tag

            await client.create_or_update_index(_build_hotel_index(index_name, description=REPLACEMENT_INDEX_DESCRIPTION))

            index.e_tag = original_e_tag
            with pytest.raises(HttpResponseError):
                await client.delete_index(index, match_condition=MatchConditions.IfNotModified)
        finally:
            await safe_delete(client.delete_index, index_name)
            await client.close()

    @live_test()
    async def test_scoring_profile_preserves_product_aggregation(self, endpoint):
        client = make_index_client(endpoint)
        index_name = self.get_resource_name("index-create-scoring-profile-product")
        fields = [
            SimpleField(name="HotelId", type=SearchFieldDataType.STRING, key=True),
            SimpleField(name="LastModified", type=SearchFieldDataType.DATE_TIME_OFFSET, filterable=True),
        ]
        scoring_profile = ScoringProfile(
            name="product-scoring-profile",
            function_aggregation=ScoringFunctionAggregation.PRODUCT,
            functions=[
                FreshnessScoringFunction(
                    field_name="LastModified",
                    boost=2.5,
                    parameters=FreshnessScoringParameters(boosting_duration=timedelta(days=7)),
                )
            ],
        )
        try:
            result = await client.create_index(
                SearchIndex(name=index_name, fields=fields, scoring_profiles=[scoring_profile])
            )
            assert result.scoring_profiles[0].function_aggregation == ScoringFunctionAggregation.PRODUCT

            retrieved_index = await client.get_index(index_name)
            assert retrieved_index.scoring_profiles[0].function_aggregation == ScoringFunctionAggregation.PRODUCT

            retrieved_index.scoring_profiles[0].function_aggregation = ScoringFunctionAggregation.SUM
            await client.create_or_update_index(retrieved_index)

            result = await client.get_index(index_name)
            assert result.scoring_profiles[0].function_aggregation == ScoringFunctionAggregation.SUM
        finally:
            await safe_delete(client.delete_index, index_name)
            await client.close()
