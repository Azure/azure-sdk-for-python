# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for ``SearchIndexerClient`` preview operations.

Covers the 2026-05-01-preview re-introduced operations: ``resync``,
``reset_documents`` and ``reset_skills``. Each test gates on
``require_capability`` so the module is import-safe on GA branches.
"""

from __future__ import annotations

from unittest import mock

import pytest
from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential

from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerSkillset,
)

from _capabilities import require_capability

ENDPOINT = "https://my-search-service.search.windows.net"
KEY = "fake-api-key"

_DELETE_RESOURCES = [
    ("delete_data_source_connection", "SearchIndexerDataSourceConnection"),
    ("delete_indexer", "SearchIndexer"),
    ("delete_skillset", "SearchIndexerSkillset"),
]
_DELETE_CONDITIONS = [
    (MatchConditions.Unconditionally, None, None),
    (MatchConditions.IfNotModified, "If-Match", '"etag"'),
    (MatchConditions.IfModified, "If-None-Match", '"etag"'),
    (MatchConditions.IfPresent, "If-Match", "*"),
    (MatchConditions.IfMissing, "If-None-Match", "*"),
]


class TestSearchIndexerClientDeletes:
    @pytest.mark.parametrize("method_name,model_name", _DELETE_RESOURCES)
    @pytest.mark.parametrize("condition,header,value", _DELETE_CONDITIONS)
    @pytest.mark.parametrize("as_model", [False, True])
    def test_delete_preserves_conditions_in_generated_headers(
        self, method_name, model_name, condition, header, value, as_model
    ):
        from types import SimpleNamespace
        from azure.search.documents.indexes import models

        resource = (
            getattr(models, model_name)({"name": "resource", "@odata.etag": '"etag"'}) if as_model else "resource"
        )
        kwargs = {} if as_model else {"etag": '"etag"'}
        response = mock.Mock(status_code=204)

        with _client() as client, mock.patch.object(
            client._client._pipeline, "run", return_value=SimpleNamespace(http_response=response)
        ) as run:
            getattr(client, method_name)(resource, match_condition=condition, headers={"x-custom": "value"}, **kwargs)

        request = run.call_args.args[0]
        assert request.method == "DELETE"
        assert "resource" in request.url
        assert request.headers["x-custom"] == "value"
        if header is None:
            assert "If-Match" not in request.headers
            assert "If-None-Match" not in request.headers
        else:
            assert request.headers[header] == value


def _client() -> SearchIndexerClient:
    return SearchIndexerClient(ENDPOINT, AzureKeyCredential(KEY))


class TestSearchIndexerCreateOrUpdateDataSourceConnection:
    @mock.patch(
        "azure.search.documents.indexes._operations._operations."
        "_SearchIndexerClientOperationsMixin._create_or_update_data_source_connection"
    )
    def test_create_or_update_data_source_connection_forwards_reset_requirement_option(self, mock_create):
        require_capability(
            "azure.search.documents.indexes.SearchIndexerClient."
            "create_or_update_data_source_connection.skip_indexer_reset_requirement_for_cache"
        )
        data_source = SearchIndexerDataSourceConnection(
            name="ds-1",
            type="azureblob",
            connection_string="UseDevelopmentStorage=true",
            container=SearchIndexerDataContainer(name="c"),
        )
        data_source.e_tag = '"etag-ds"'

        _client().create_or_update_data_source_connection(
            data_source,
            skip_indexer_reset_requirement_for_cache=True,
            match_condition=MatchConditions.IfNotModified,
        )

        mock_create.assert_called_once()
        kwargs = mock_create.call_args.kwargs
        assert kwargs["name"] == "ds-1"
        assert kwargs["data_source"] is data_source
        assert kwargs["prefer"] == "return=representation"
        assert kwargs["etag"] == '"etag-ds"'
        assert kwargs["match_condition"] == MatchConditions.IfNotModified
        assert kwargs["skip_indexer_reset_requirement_for_cache"] is True


class TestSearchIndexerCreateOrUpdateIndexer:
    @mock.patch(
        "azure.search.documents.indexes._operations._operations._SearchIndexerClientOperationsMixin._create_or_update_indexer"
    )
    def test_create_or_update_indexer_forwards_reset_requirement_and_cache_reprocessing_options(self, mock_create):
        require_capability(
            "azure.search.documents.indexes.SearchIndexerClient."
            "create_or_update_indexer.skip_indexer_reset_requirement_for_cache",
            "azure.search.documents.indexes.SearchIndexerClient."
            "create_or_update_indexer.disable_cache_reprocessing_change_detection",
        )
        indexer = SearchIndexer(name="idxr-1", data_source_name="ds-1", target_index_name="idx-1")
        indexer.e_tag = '"etag-indexer"'

        _client().create_or_update_indexer(
            indexer,
            skip_indexer_reset_requirement_for_cache=True,
            disable_cache_reprocessing_change_detection=True,
            match_condition=MatchConditions.IfNotModified,
        )

        mock_create.assert_called_once()
        kwargs = mock_create.call_args.kwargs
        assert kwargs["name"] == "idxr-1"
        assert kwargs["indexer"] is indexer
        assert kwargs["prefer"] == "return=representation"
        assert kwargs["etag"] == '"etag-indexer"'
        assert kwargs["match_condition"] == MatchConditions.IfNotModified
        assert kwargs["skip_indexer_reset_requirement_for_cache"] is True
        assert kwargs["disable_cache_reprocessing_change_detection"] is True


class TestSearchIndexerCreateOrUpdateSkillset:
    @mock.patch(
        "azure.search.documents.indexes._operations._operations._SearchIndexerClientOperationsMixin._create_or_update_skillset"
    )
    def test_create_or_update_skillset_forwards_reset_requirement_and_cache_reprocessing_options(self, mock_create):
        require_capability(
            "azure.search.documents.indexes.SearchIndexerClient."
            "create_or_update_skillset.skip_indexer_reset_requirement_for_cache",
            "azure.search.documents.indexes.SearchIndexerClient."
            "create_or_update_skillset.disable_cache_reprocessing_change_detection",
        )
        skillset = SearchIndexerSkillset(name="skillset-1", skills=[])
        skillset.e_tag = '"etag-skillset"'

        _client().create_or_update_skillset(
            skillset,
            skip_indexer_reset_requirement_for_cache=True,
            disable_cache_reprocessing_change_detection=True,
            match_condition=MatchConditions.IfNotModified,
        )

        mock_create.assert_called_once()
        kwargs = mock_create.call_args.kwargs
        assert kwargs["name"] == "skillset-1"
        assert kwargs["skillset"] is skillset
        assert kwargs["prefer"] == "return=representation"
        assert kwargs["etag"] == '"etag-skillset"'
        assert kwargs["match_condition"] == MatchConditions.IfNotModified
        assert kwargs["skip_indexer_reset_requirement_for_cache"] is True
        assert kwargs["disable_cache_reprocessing_change_detection"] is True


class TestSearchIndexerResync:
    @mock.patch("azure.search.documents.indexes._operations._operations._SearchIndexerClientOperationsMixin._resync")
    def test_resync_forwards_name_and_body(self, mock_resync):
        require_capability("azure.search.documents.indexes.SearchIndexerClient.resync")
        from azure.search.documents.indexes.models import IndexerResyncBody

        body = IndexerResyncBody(options=["permissions"])

        _client().resync("idx-1", body, request_id="req-1")

        mock_resync.assert_called_once()
        kwargs = mock_resync.call_args.kwargs
        assert kwargs["name"] == "idx-1"
        assert kwargs["indexer_resync"] is body
        assert kwargs["request_id"] == "req-1"

    @mock.patch("azure.search.documents.indexes._operations._operations._SearchIndexerClientOperationsMixin._resync")
    def test_resync_accepts_json_dict(self, mock_resync):
        require_capability("azure.search.documents.indexes.SearchIndexerClient.resync")

        body = {"options": ["permissions"]}
        _client().resync("idx-1", body)

        mock_resync.assert_called_once()
        assert mock_resync.call_args.kwargs["indexer_resync"] == body


class TestSearchIndexerResetDocuments:
    @mock.patch(
        "azure.search.documents.indexes._operations._operations._SearchIndexerClientOperationsMixin._reset_documents",
        create=True,
    )
    def test_reset_documents_forwards_keys_and_overwrite(self, mock_reset):
        require_capability("azure.search.documents.indexes.SearchIndexerClient.reset_documents")
        from azure.search.documents.indexes.models import DocumentKeysOrIds

        body = DocumentKeysOrIds(document_keys=["k1", "k2"], datasource_document_ids=["id1"])

        _client().reset_documents("idx-1", body, overwrite=True)

        mock_reset.assert_called_once()
        kwargs = mock_reset.call_args.kwargs
        assert kwargs["name"] == "idx-1"
        assert kwargs["keys_or_ids"] is body
        assert kwargs["overwrite"] is True

    @mock.patch(
        "azure.search.documents.indexes._operations._operations._SearchIndexerClientOperationsMixin._reset_documents",
        create=True,
    )
    def test_reset_documents_defaults_keys_to_none(self, mock_reset):
        require_capability("azure.search.documents.indexes.SearchIndexerClient.reset_documents")

        _client().reset_documents("idx-1")

        mock_reset.assert_called_once()
        kwargs = mock_reset.call_args.kwargs
        assert kwargs["name"] == "idx-1"
        assert kwargs["keys_or_ids"] is None
        assert kwargs["overwrite"] is None


class TestSearchIndexerResetSkills:
    @mock.patch(
        "azure.search.documents.indexes._operations._operations._SearchIndexerClientOperationsMixin._reset_skills",
        create=True,
    )
    def test_reset_skills_forwards_skill_names(self, mock_reset):
        require_capability("azure.search.documents.indexes.SearchIndexerClient.reset_skills")
        from azure.search.documents.indexes.models import SkillNames

        names = SkillNames(skill_names=["skill-a", "skill-b"])

        _client().reset_skills("skillset-1", names, request_id="req-2")

        mock_reset.assert_called_once()
        kwargs = mock_reset.call_args.kwargs
        assert kwargs["name"] == "skillset-1"
        assert kwargs["skill_names"] is names
        assert kwargs["request_id"] == "req-2"

    @mock.patch(
        "azure.search.documents.indexes._operations._operations._SearchIndexerClientOperationsMixin._reset_skills",
        create=True,
    )
    def test_reset_skills_accepts_json_dict(self, mock_reset):
        require_capability("azure.search.documents.indexes.SearchIndexerClient.reset_skills")

        body = {"skillNames": ["skill-a"]}
        _client().reset_skills("skillset-1", body)

        mock_reset.assert_called_once()
        assert mock_reset.call_args.kwargs["skill_names"] == body
