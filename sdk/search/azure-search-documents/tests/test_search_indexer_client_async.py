# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async unit tests for ``SearchIndexerClient`` preview operations."""

from __future__ import annotations

from unittest import mock

import pytest
from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential

from azure.search.documents.indexes.aio import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerSkillset,
)

from _capabilities import require_capability

ENDPOINT = "https://my-search-service.search.windows.net"
KEY = "fake-api-key"


def _client() -> SearchIndexerClient:
    return SearchIndexerClient(ENDPOINT, AzureKeyCredential(KEY))


async def _async_none(*args, **kwargs):
    return None


@pytest.mark.asyncio
class TestSearchIndexerCreateOrUpdateDataSourceConnectionAsync:
    async def test_create_or_update_data_source_connection_forwards_reset_requirement_option(self):
        require_capability(
            "azure.search.documents.indexes.aio.SearchIndexerClient."
            "create_or_update_data_source_connection.skip_indexer_reset_requirement_for_cache"
        )
        data_source = SearchIndexerDataSourceConnection(
            name="ds-1",
            type="azureblob",
            connection_string="UseDevelopmentStorage=true",
            container=SearchIndexerDataContainer(name="c"),
        )
        data_source.e_tag = '"etag-ds"'
        with mock.patch(
            "azure.search.documents.indexes.aio._operations._operations."
            "_SearchIndexerClientOperationsMixin._create_or_update_data_source_connection",
            new=mock.AsyncMock(return_value=data_source),
        ) as mock_create:
            await _client().create_or_update_data_source_connection(
                data_source,
                skip_indexer_reset_requirement_for_cache=True,
                match_condition=MatchConditions.IfNotModified,
            )

        mock_create.assert_awaited_once()
        kwargs = mock_create.call_args.kwargs
        assert kwargs["name"] == "ds-1"
        assert kwargs["data_source"] is data_source
        assert kwargs["prefer"] == "return=representation"
        assert kwargs["etag"] == '"etag-ds"'
        assert kwargs["match_condition"] == MatchConditions.IfNotModified
        assert kwargs["skip_indexer_reset_requirement_for_cache"] is True


@pytest.mark.asyncio
class TestSearchIndexerCreateOrUpdateIndexerAsync:
    async def test_create_or_update_indexer_forwards_reset_requirement_and_cache_reprocessing_options(self):
        require_capability(
            "azure.search.documents.indexes.aio.SearchIndexerClient."
            "create_or_update_indexer.skip_indexer_reset_requirement_for_cache",
            "azure.search.documents.indexes.aio.SearchIndexerClient."
            "create_or_update_indexer.disable_cache_reprocessing_change_detection",
        )
        indexer = SearchIndexer(name="idxr-1", data_source_name="ds-1", target_index_name="idx-1")
        indexer.e_tag = '"etag-indexer"'
        with mock.patch(
            "azure.search.documents.indexes.aio._operations._operations."
            "_SearchIndexerClientOperationsMixin._create_or_update_indexer",
            new=mock.AsyncMock(return_value=indexer),
        ) as mock_create:
            await _client().create_or_update_indexer(
                indexer,
                skip_indexer_reset_requirement_for_cache=True,
                disable_cache_reprocessing_change_detection=True,
                match_condition=MatchConditions.IfNotModified,
            )

        mock_create.assert_awaited_once()
        kwargs = mock_create.call_args.kwargs
        assert kwargs["name"] == "idxr-1"
        assert kwargs["indexer"] is indexer
        assert kwargs["prefer"] == "return=representation"
        assert kwargs["etag"] == '"etag-indexer"'
        assert kwargs["match_condition"] == MatchConditions.IfNotModified
        assert kwargs["skip_indexer_reset_requirement_for_cache"] is True
        assert kwargs["disable_cache_reprocessing_change_detection"] is True


@pytest.mark.asyncio
class TestSearchIndexerCreateOrUpdateSkillsetAsync:
    async def test_create_or_update_skillset_forwards_reset_requirement_and_cache_reprocessing_options(self):
        require_capability(
            "azure.search.documents.indexes.aio.SearchIndexerClient."
            "create_or_update_skillset.skip_indexer_reset_requirement_for_cache",
            "azure.search.documents.indexes.aio.SearchIndexerClient."
            "create_or_update_skillset.disable_cache_reprocessing_change_detection",
        )
        skillset = SearchIndexerSkillset(name="skillset-1", skills=[])
        skillset.e_tag = '"etag-skillset"'
        with mock.patch(
            "azure.search.documents.indexes.aio._operations._operations."
            "_SearchIndexerClientOperationsMixin._create_or_update_skillset",
            new=mock.AsyncMock(return_value=skillset),
        ) as mock_create:
            await _client().create_or_update_skillset(
                skillset,
                skip_indexer_reset_requirement_for_cache=True,
                disable_cache_reprocessing_change_detection=True,
                match_condition=MatchConditions.IfNotModified,
            )

        mock_create.assert_awaited_once()
        kwargs = mock_create.call_args.kwargs
        assert kwargs["name"] == "skillset-1"
        assert kwargs["skillset"] is skillset
        assert kwargs["prefer"] == "return=representation"
        assert kwargs["etag"] == '"etag-skillset"'
        assert kwargs["match_condition"] == MatchConditions.IfNotModified
        assert kwargs["skip_indexer_reset_requirement_for_cache"] is True
        assert kwargs["disable_cache_reprocessing_change_detection"] is True


@pytest.mark.asyncio
class TestSearchIndexerResyncAsync:
    async def test_resync_forwards_name_and_body(self):
        require_capability("azure.search.documents.indexes.aio.SearchIndexerClient.resync")
        from azure.search.documents.indexes.models import IndexerResyncBody

        body = IndexerResyncBody(options=["permissions"])
        with mock.patch(
            "azure.search.documents.indexes.aio._operations._operations._SearchIndexerClientOperationsMixin._resync",
            new=mock.AsyncMock(return_value=None),
        ) as mock_resync:
            await _client().resync("idx-1", body, request_id="req-1")

        mock_resync.assert_awaited_once()
        kwargs = mock_resync.call_args.kwargs
        assert kwargs["name"] == "idx-1"
        assert kwargs["indexer_resync"] is body
        assert kwargs["request_id"] == "req-1"

    async def test_resync_accepts_json_dict(self):
        require_capability("azure.search.documents.indexes.aio.SearchIndexerClient.resync")

        body = {"options": ["permissions"]}
        with mock.patch(
            "azure.search.documents.indexes.aio._operations._operations._SearchIndexerClientOperationsMixin._resync",
            new=mock.AsyncMock(return_value=None),
        ) as mock_resync:
            await _client().resync("idx-1", body)

        assert mock_resync.call_args.kwargs["indexer_resync"] == body


@pytest.mark.asyncio
class TestSearchIndexerResetDocumentsAsync:
    async def test_reset_documents_forwards_keys_and_overwrite(self):
        require_capability("azure.search.documents.indexes.aio.SearchIndexerClient.reset_documents")
        from azure.search.documents.indexes.models import DocumentKeysOrIds

        body = DocumentKeysOrIds(document_keys=["k1", "k2"], datasource_document_ids=["id1"])
        with mock.patch(
            "azure.search.documents.indexes.aio._operations._operations."
            "_SearchIndexerClientOperationsMixin._reset_documents",
            new=mock.AsyncMock(return_value=None),
        ) as mock_reset:
            await _client().reset_documents("idx-1", body, overwrite=True)

        mock_reset.assert_awaited_once()
        kwargs = mock_reset.call_args.kwargs
        assert kwargs["name"] == "idx-1"
        assert kwargs["keys_or_ids"] is body
        assert kwargs["overwrite"] is True

    async def test_reset_documents_defaults_keys_to_none(self):
        require_capability("azure.search.documents.indexes.aio.SearchIndexerClient.reset_documents")

        with mock.patch(
            "azure.search.documents.indexes.aio._operations._operations."
            "_SearchIndexerClientOperationsMixin._reset_documents",
            new=mock.AsyncMock(return_value=None),
        ) as mock_reset:
            await _client().reset_documents("idx-1")

        kwargs = mock_reset.call_args.kwargs
        assert kwargs["keys_or_ids"] is None
        assert kwargs["overwrite"] is None


@pytest.mark.asyncio
class TestSearchIndexerResetSkillsAsync:
    async def test_reset_skills_forwards_skill_names(self):
        require_capability("azure.search.documents.indexes.aio.SearchIndexerClient.reset_skills")
        from azure.search.documents.indexes.models import SkillNames

        names = SkillNames(skill_names=["skill-a", "skill-b"])
        with mock.patch(
            "azure.search.documents.indexes.aio._operations._operations._SearchIndexerClientOperationsMixin._reset_skills",
            new=mock.AsyncMock(return_value=None),
        ) as mock_reset:
            await _client().reset_skills("skillset-1", names, request_id="req-2")

        mock_reset.assert_awaited_once()
        kwargs = mock_reset.call_args.kwargs
        assert kwargs["name"] == "skillset-1"
        assert kwargs["skill_names"] is names
        assert kwargs["request_id"] == "req-2"

    async def test_reset_skills_accepts_json_dict(self):
        require_capability("azure.search.documents.indexes.aio.SearchIndexerClient.reset_skills")

        body = {"skillNames": ["skill-a"]}
        with mock.patch(
            "azure.search.documents.indexes.aio._operations._operations._SearchIndexerClientOperationsMixin._reset_skills",
            new=mock.AsyncMock(return_value=None),
        ) as mock_reset:
            await _client().reset_skills("skillset-1", body)

        assert mock_reset.call_args.kwargs["skill_names"] == body
