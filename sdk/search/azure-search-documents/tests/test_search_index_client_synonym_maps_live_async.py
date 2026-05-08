# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async live tests for ``SearchIndexClient`` synonym map operations."""
from __future__ import annotations

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import SynonymMap
from devtools_testutils import AzureRecordedTestCase

from _search_helpers_async import live_test, make_index_client, safe_delete

SYNONYMS = [
    "United States, United States of America",
    "Washington State, State of Washington",
]
REPLACEMENT_SYNONYMS = ["Washington State, State of Washington"]


def _build_synonym_map(synonym_map_name: str, *, synonyms: list[str] | None = None) -> SynonymMap:
    return SynonymMap(name=synonym_map_name, synonyms=synonyms if synonyms is not None else SYNONYMS)


class TestSearchIndexClientSynonymMapAsync(AzureRecordedTestCase):
    @live_test()
    async def test_create_get_list_and_delete_synonym_map(self, endpoint):
        client = make_index_client(endpoint)
        synonym_map_name = self.get_resource_name("synonym-map-create")
        try:
            created_synonym_map = await client.create_synonym_map(_build_synonym_map(synonym_map_name))

            assert created_synonym_map.name == synonym_map_name
            assert created_synonym_map.synonyms == SYNONYMS

            retrieved_synonym_map = await client.get_synonym_map(synonym_map_name)
            assert retrieved_synonym_map.name == synonym_map_name
            assert retrieved_synonym_map.synonyms == SYNONYMS

            synonym_map_names = await client.get_synonym_map_names()
            assert synonym_map_name in synonym_map_names
            assert synonym_map_name in {synonym_map.name for synonym_map in await client.get_synonym_maps()}

            selected_synonym_maps = await client.get_synonym_maps(select=["name"])
            selected_synonym_map = next(
                synonym_map for synonym_map in selected_synonym_maps if synonym_map.name == synonym_map_name
            )
            assert selected_synonym_map.name == synonym_map_name

            await client.delete_synonym_map(synonym_map_name)
            with pytest.raises(HttpResponseError):
                await client.get_synonym_map(synonym_map_name)
        finally:
            await safe_delete(client.delete_synonym_map, synonym_map_name)
            await client.close()

    @live_test()
    async def test_create_or_update_synonym_map_accepts_model_and_mapping(self, endpoint):
        client = make_index_client(endpoint)
        model_synonym_map_name = self.get_resource_name("synonym-map-create-or-update-model")
        mapping_synonym_map_name = self.get_resource_name("synonym-map-create-or-update-mapping")
        try:
            model_result = await client.create_or_update_synonym_map(_build_synonym_map(model_synonym_map_name))
            assert model_result.name == model_synonym_map_name
            assert model_result.synonyms == SYNONYMS

            model_result.synonyms = REPLACEMENT_SYNONYMS
            model_result = await client.create_or_update_synonym_map(model_result)
            assert model_result.synonyms == REPLACEMENT_SYNONYMS

            mapping = _build_synonym_map(mapping_synonym_map_name).as_dict()
            mapping_result = await client.create_or_update_synonym_map(mapping)
            assert mapping_result.name == mapping_synonym_map_name
            assert mapping_result.synonyms == SYNONYMS
        finally:
            await safe_delete(client.delete_synonym_map, model_synonym_map_name)
            await safe_delete(client.delete_synonym_map, mapping_synonym_map_name)
            await client.close()

    @live_test()
    async def test_create_or_update_synonym_map_uses_model_etag_and_match_condition(self, endpoint):
        client = make_index_client(endpoint)
        synonym_map_name = self.get_resource_name("synonym-map-create-or-update-match-condition")
        try:
            synonym_map = await client.create_synonym_map(_build_synonym_map(synonym_map_name))
            original_e_tag = synonym_map.e_tag

            await client.create_or_update_synonym_map(_build_synonym_map(synonym_map_name, synonyms=REPLACEMENT_SYNONYMS))

            synonym_map.e_tag = original_e_tag
            synonym_map.synonyms = SYNONYMS
            with pytest.raises(HttpResponseError):
                await client.create_or_update_synonym_map(synonym_map, match_condition=MatchConditions.IfNotModified)
        finally:
            await safe_delete(client.delete_synonym_map, synonym_map_name)
            await client.close()

    @live_test()
    async def test_delete_synonym_map_accepts_model_etag_and_match_condition(self, endpoint):
        client = make_index_client(endpoint)
        synonym_map_name = self.get_resource_name("synonym-map-delete-match-condition")
        try:
            synonym_map = await client.create_synonym_map(_build_synonym_map(synonym_map_name))
            original_e_tag = synonym_map.e_tag

            await client.create_or_update_synonym_map(_build_synonym_map(synonym_map_name, synonyms=REPLACEMENT_SYNONYMS))

            synonym_map.e_tag = original_e_tag
            with pytest.raises(HttpResponseError):
                await client.delete_synonym_map(synonym_map, match_condition=MatchConditions.IfNotModified)
        finally:
            await safe_delete(client.delete_synonym_map, synonym_map_name)
            await client.close()
