# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``SearchIndexClient`` index operations."""
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

from _search_helpers import live_test, make_index_client, safe_delete

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


class TestSearchIndexClient(AzureRecordedTestCase):
    @live_test()
    def test_get_service_statistics_returns_counters_and_limits(self, endpoint):
        client = make_index_client(endpoint)
        try:
            result = client.get_service_statistics()
        finally:
            client.close()

        assert "counters" in result
        assert "limits" in result

    @live_test()
    def test_list_indexes_returns_empty_page_when_service_has_no_indexes(self, endpoint):
        client = make_index_client(endpoint)
        try:
            assert list(client.list_indexes()) == []
        finally:
            client.close()

    @live_test()
    def test_create_get_list_statistics_analyze_and_delete_index(self, endpoint):
        client = make_index_client(endpoint)
        index_name = self.get_resource_name("index-create")
        try:
            created_index = client.create_index(
                _build_hotel_index(index_name, scoring_profiles=[_build_scoring_profile(SCORING_PROFILE_NAME)])
            )

            assert created_index.name == index_name
            assert created_index.description == INDEX_DESCRIPTION
            assert created_index.scoring_profiles[0].name == SCORING_PROFILE_NAME
            assert created_index.cors_options.allowed_origins == CORS_OPTIONS.allowed_origins
            assert created_index.cors_options.max_age_in_seconds == CORS_OPTIONS.max_age_in_seconds

            retrieved_index = client.get_index(index_name)
            assert retrieved_index.name == index_name
            assert retrieved_index.description == INDEX_DESCRIPTION

            index_names = set(client.list_index_names())
            assert index_name in index_names
            assert any(index.name == index_name for index in client.list_indexes())

            projected_indexes = list(client.list_indexes(select=["name", "description"]))
            projected_index = next(index for index in projected_indexes if index.name == index_name)
            assert projected_index.description == INDEX_DESCRIPTION
            assert projected_index.fields == []

            statistics = client.get_index_statistics(index_name)
            assert "documentCount" in statistics
            assert "storageSize" in statistics
            assert "vectorIndexSize" in statistics

            analyze_request = AnalyzeTextOptions(text="One's <two/>", analyzer_name="standard.lucene")
            analyze_result = client.analyze_text(index_name, analyze_request)
            tokens = [token.token for token in analyze_result.tokens]
            assert len(tokens) == 2
            if self.is_live:
                assert tokens == ["one's", "two"]

            search_client = client.get_search_client(index_name)
            try:
                assert search_client.get_document_count() == 0
            finally:
                search_client.close()

            client.delete_index(index_name)
            with pytest.raises(HttpResponseError):
                client.get_index(index_name)
        finally:
            safe_delete(client.delete_index, index_name)
            client.close()

    @live_test()
    def test_create_or_update_index_accepts_model_and_mapping(self, endpoint):
        client = make_index_client(endpoint)
        model_index_name = self.get_resource_name("index-create-or-update-model")
        mapping_index_name = self.get_resource_name("index-create-or-update-mapping")
        try:
            model_result = client.create_or_update_index(_build_hotel_index(model_index_name))
            assert model_result.name == model_index_name
            assert model_result.description == INDEX_DESCRIPTION

            model_result.description = REPLACEMENT_INDEX_DESCRIPTION
            model_result.scoring_profiles = [_build_scoring_profile(REPLACEMENT_SCORING_PROFILE_NAME)]
            model_result = client.create_or_update_index(model_result)
            assert model_result.description == REPLACEMENT_INDEX_DESCRIPTION
            assert model_result.scoring_profiles[0].name == REPLACEMENT_SCORING_PROFILE_NAME

            mapping = _build_hotel_index(mapping_index_name).as_dict()
            mapping_result = client.create_or_update_index(mapping)
            assert mapping_result.name == mapping_index_name
            assert mapping_result.description == INDEX_DESCRIPTION
        finally:
            safe_delete(client.delete_index, model_index_name)
            safe_delete(client.delete_index, mapping_index_name)
            client.close()

    @live_test()
    def test_create_or_update_index_uses_model_etag_and_match_condition(self, endpoint):
        client = make_index_client(endpoint)
        index_name = self.get_resource_name("index-create-or-update-match-condition")
        try:
            index = client.create_index(_build_hotel_index(index_name))
            original_e_tag = index.e_tag

            replacement_index = _build_hotel_index(index_name, description=REPLACEMENT_INDEX_DESCRIPTION)
            client.create_or_update_index(replacement_index)

            index.e_tag = original_e_tag
            index.description = INDEX_DESCRIPTION
            with pytest.raises(HttpResponseError):
                client.create_or_update_index(index, match_condition=MatchConditions.IfNotModified)
        finally:
            safe_delete(client.delete_index, index_name)
            client.close()

    @live_test()
    def test_delete_index_accepts_model_etag_and_match_condition(self, endpoint):
        client = make_index_client(endpoint)
        index_name = self.get_resource_name("index-delete-match-condition")
        try:
            index = client.create_index(_build_hotel_index(index_name))
            original_e_tag = index.e_tag

            client.create_or_update_index(_build_hotel_index(index_name, description=REPLACEMENT_INDEX_DESCRIPTION))

            index.e_tag = original_e_tag
            with pytest.raises(HttpResponseError):
                client.delete_index(index, match_condition=MatchConditions.IfNotModified)
        finally:
            safe_delete(client.delete_index, index_name)
            client.close()

    @live_test()
    def test_scoring_profile_preserves_product_aggregation(self, endpoint):
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
            result = client.create_index(
                SearchIndex(name=index_name, fields=fields, scoring_profiles=[scoring_profile])
            )
            assert result.scoring_profiles[0].function_aggregation == ScoringFunctionAggregation.PRODUCT

            retrieved_index = client.get_index(index_name)
            assert retrieved_index.scoring_profiles[0].function_aggregation == ScoringFunctionAggregation.PRODUCT

            retrieved_index.scoring_profiles[0].function_aggregation = ScoringFunctionAggregation.SUM
            client.create_or_update_index(retrieved_index)

            result = client.get_index(index_name)
            assert result.scoring_profiles[0].function_aggregation == ScoringFunctionAggregation.SUM
        finally:
            safe_delete(client.delete_index, index_name)
            client.close()
