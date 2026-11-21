# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Recorded async execution of preview samples and their result assertions."""

import pytest
from devtools_testutils import AzureRecordedTestCase

from _preview_sample_helpers import (
    cleanup_retained_sample_async,
    load_preview_sample,
    record_topic_embeddings,
    track_sample_creations,
)
from _search_helpers_async import live_test


class TestPreviewFeatureSamplesAsync(AzureRecordedTestCase):
    async def _run_sample(self, endpoint, scenario, variables):
        with pytest.MonkeyPatch.context() as monkeypatch:
            sample, variables = load_preview_sample(self, monkeypatch, scenario, endpoint, variables, is_async=True)
            retained = scenario == "topic_graph" or scenario.startswith("graph_")
            created = track_sample_creations(monkeypatch, is_async=True) if retained else []
            if scenario == "topic_graph":
                record_topic_embeddings(self, monkeypatch, variables, is_async=True)
            try:
                await sample.main()
            finally:
                if retained:
                    await cleanup_retained_sample_async(endpoint, created)
            return variables

    @live_test()
    async def test_search_agentic_returns_hotel_evidence_and_usage(self, endpoint, variables=None):
        return await self._run_sample(endpoint, "agentic_search", variables)

    @live_test()
    async def test_retrieve_microsoft_retriever_returns_hotel_evidence(self, endpoint, variables=None):
        return await self._run_sample(endpoint, "microsoft_retriever", variables)

    @live_test()
    async def test_begin_ingest_upload_and_replace_returns_updated_hotel_evidence(self, endpoint, variables=None):
        return await self._run_sample(endpoint, "file_lro", variables)

    @live_test()
    async def test_retrieve_compatible_chat_returns_hotel_evidence(self, endpoint, variables=None):
        return await self._run_sample(endpoint, "compatible_chat", variables)

    @live_test()
    async def test_retrieve_native_gpt6_returns_hotel_evidence(self, endpoint, variables=None):
        return await self._run_sample(endpoint, "gpt6", variables)

    @live_test()
    async def test_retrieve_automatic_hints_refreshes_new_country_after_ttl(self, endpoint, variables=None):
        return await self._run_sample(endpoint, "automatic_hints", variables)

    @live_test()
    async def test_search_topic_graph_modes_retrieve_populated_hotel_evidence(self, endpoint, variables=None):
        return await self._run_sample(endpoint, "topic_graph", variables)

    @live_test()
    async def test_graph_setup_returns_seeded_relationship_and_provenance(self, endpoint, variables=None):
        return await self._run_sample(endpoint, "graph_index", variables)

    @live_test()
    async def test_retrieve_extracted_graph_returns_hotel_relationship_evidence(self, endpoint, variables=None):
        return await self._run_sample(endpoint, "graph_extraction", variables)

    @live_test()
    async def test_retrieve_hydrated_graph_returns_supporting_hotel_text(self, endpoint, variables=None):
        return await self._run_sample(endpoint, "graph_hydration", variables)
