# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for ``SearchIndexClient`` list-paging customizations."""

from __future__ import annotations

from unittest import mock

import pytest

from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from azure.core.paging import ItemPaged

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex

from _capabilities import require_capability

ENDPOINT = "https://my-search-service.search.windows.net"
KEY = "fake-api-key"

_DELETE_RESOURCES = [
    ("delete_index", "SearchIndex"),
    ("delete_synonym_map", "SynonymMap"),
    ("delete_alias", "SearchAlias"),
    ("delete_knowledge_base", "KnowledgeBase"),
    ("delete_knowledge_source", "SearchIndexKnowledgeSource"),
]
_DELETE_CONDITIONS = [
    (MatchConditions.Unconditionally, None, None),
    (MatchConditions.IfNotModified, "If-Match", '"etag"'),
    (MatchConditions.IfModified, "If-None-Match", '"etag"'),
    (MatchConditions.IfPresent, "If-Match", "*"),
    (MatchConditions.IfMissing, "If-None-Match", "*"),
]


class TestSearchIndexClientDeletes:
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


def _client() -> SearchIndexClient:
    return SearchIndexClient(ENDPOINT, AzureKeyCredential(KEY))


def _empty_pager(*_args, **_kwargs):
    pager = mock.MagicMock(spec=ItemPaged)
    pager.__iter__.return_value = iter([])
    return pager


def _index_response_stub(name="hotels"):
    response = mock.Mock()
    response.name = name
    response.fields = []
    response.description = None
    response.scoring_profiles = None
    response.default_scoring_profile = None
    response.cors_options = None
    response.suggesters = None
    response.analyzers = None
    response.tokenizers = None
    response.token_filters = None
    response.char_filters = None
    response.normalizers = None
    response.encryption_key = None
    response.similarity = None
    response.semantic_search = None
    response.vector_search = None
    response.permission_filter_option = None
    response.purview_enabled = None
    response.share_point_connector_app_registration = {
        "applicationId": "sharepoint-app",
        "federatedCredentialId": "sharepoint-credential",
    }
    response.e_tag = '"etag"'
    return response


class TestListIndexes:
    @mock.patch(
        "azure.search.documents.indexes._operations._operations._SearchIndexClientOperationsMixin._list_indexes",
        side_effect=_empty_pager,
    )
    def test_list_indexes_forwards_search_paging(self, mock_list):
        require_capability(
            "azure.search.documents.indexes.SearchIndexClient.list_indexes.search",
            "azure.search.documents.indexes.SearchIndexClient.list_indexes.page_size",
            "azure.search.documents.indexes.SearchIndexClient.list_indexes.search_type",
        )

        list(_client().list_indexes(search="hot", page_size=10, search_type="prefix"))

        mock_list.assert_called_once()
        kwargs = mock_list.call_args.kwargs
        assert kwargs["search"] == "hot"
        assert kwargs["page_size"] == 10
        assert kwargs["search_type"] == "prefix"

    @mock.patch(
        "azure.search.documents.indexes._operations._operations."
        "_SearchIndexClientOperationsMixin._list_indexes_with_selected_properties",
        side_effect=_empty_pager,
    )
    def test_list_indexes_with_select_forwards_paging_kwargs(self, mock_list_select):
        require_capability(
            "azure.search.documents.indexes.SearchIndexClient.list_indexes.search",
            "azure.search.documents.indexes.SearchIndexClient.list_indexes.page_size",
            "azure.search.documents.indexes.SearchIndexClient.list_indexes.search_type",
            "azure.search.documents.indexes.models.SearchIndex.cors_options",
            "azure.search.documents.indexes.models.SearchIndex.permission_filter_option",
            "azure.search.documents.indexes.models.SearchIndex.share_point_connector_app_registration",
        )

        list(_client().list_indexes(select=["name"], search="hot", page_size=3, search_type="prefix"))

        mock_list_select.assert_called_once()
        kwargs = mock_list_select.call_args.kwargs
        assert kwargs["select"] == ["name"]
        assert kwargs["search"] == "hot"
        assert kwargs["page_size"] == 3
        assert kwargs["search_type"] == "prefix"
        converted = kwargs["cls"]([_index_response_stub()])
        assert isinstance(converted[0], SearchIndex)
        assert converted[0].name == "hotels"
        registration = converted[0].share_point_connector_app_registration
        assert registration.application_id == "sharepoint-app"
        assert registration.federated_credential_id == "sharepoint-credential"
        assert converted[0].e_tag == '"etag"'


class TestListIndexNames:
    @mock.patch(
        "azure.search.documents.indexes._operations._operations._SearchIndexClientOperationsMixin._list_indexes",
        side_effect=_empty_pager,
    )
    def test_list_index_names_forwards_search_paging(self, mock_list):
        require_capability(
            "azure.search.documents.indexes.SearchIndexClient.list_index_names.search",
            "azure.search.documents.indexes.SearchIndexClient.list_index_names.page_size",
            "azure.search.documents.indexes.SearchIndexClient.list_index_names.search_type",
        )

        list(_client().list_index_names(search="hot", page_size=20, search_type="prefix"))

        mock_list.assert_called_once()
        kwargs = mock_list.call_args.kwargs
        assert kwargs["search"] == "hot"
        assert kwargs["page_size"] == 20
        assert kwargs["search_type"] == "prefix"
        # The names projection passes a `cls` callback that maps to .name strings.
        assert callable(kwargs["cls"])


class TestKnowledgeSourceFileOperations:
    @mock.patch(
        "azure.search.documents.indexes._operations._operations."
        "_SearchIndexClientOperationsMixin._upload_knowledge_source_file",
        create=True,
    )
    def test_upload_knowledge_source_file_forwards_content(self, mock_upload):
        require_capability("azure.search.documents.indexes.SearchIndexClient.upload_knowledge_source_file")

        _client().upload_knowledge_source_file(
            "files-source",
            b"content",
            content_type="application/octet-stream",
            content_disposition='attachment; filename="content.bin"',
        )

        mock_upload.assert_called_once()
        kwargs = mock_upload.call_args.kwargs
        assert kwargs["name"] == "files-source"
        assert kwargs["file"] == b"content"
        assert kwargs["content_type"] == "application/octet-stream"
        assert kwargs["content_disposition"] == 'attachment; filename="content.bin"'

    @mock.patch(
        "azure.search.documents.indexes._operations._operations."
        "_SearchIndexClientOperationsMixin._upload_knowledge_source_file",
        create=True,
    )
    def test_upload_knowledge_source_file_builds_content_disposition_from_filename(self, mock_upload):
        require_capability("azure.search.documents.indexes.SearchIndexClient.upload_knowledge_source_file")

        _client().upload_knowledge_source_file(
            "files-source",
            b"content",
            filename="installation-guide.pdf",
        )

        mock_upload.assert_called_once()
        kwargs = mock_upload.call_args.kwargs
        assert kwargs["content_disposition"] == 'attachment; filename="installation-guide.pdf"'

    def test_upload_knowledge_source_file_requires_filename_or_content_disposition(self):
        require_capability("azure.search.documents.indexes.SearchIndexClient.upload_knowledge_source_file")

        with pytest.raises(ValueError, match="filename"):
            _client().upload_knowledge_source_file("files-source", b"content")

    @mock.patch(
        "azure.search.documents.indexes._operations._operations."
        "_SearchIndexClientOperationsMixin._delete_knowledge_source_file"
    )
    def test_delete_knowledge_source_file_forwards_file_id(self, mock_delete):
        require_capability("azure.search.documents.indexes.SearchIndexClient.delete_knowledge_source_file")

        _client().delete_knowledge_source_file("files-source", "file-1")

        mock_delete.assert_called_once()
        kwargs = mock_delete.call_args.kwargs
        assert kwargs["name"] == "files-source"
        assert kwargs["file_id"] == "file-1"

    @mock.patch(
        "azure.search.documents.indexes._operations._operations."
        "_SearchIndexClientOperationsMixin.update_knowledge_source_file"
    )
    def test_update_knowledge_source_file_uses_name_first_and_forwards_by_keyword(self, mock_update):
        require_capability("azure.search.documents.indexes.SearchIndexClient.update_knowledge_source_file")
        from azure.search.documents.indexes.models import UpdateKnowledgeSourceFileRequest

        body = UpdateKnowledgeSourceFileRequest({"metadata": {"fileName": "updated.txt"}, "content": b"updated"})

        _client().update_knowledge_source_file("files-source", "file-1", body)

        mock_update.assert_called_once_with(name="files-source", file_id="file-1", body=body)


@pytest.mark.parametrize(
    ("public_method", "generated_method"),
    [
        ("get_synonym_maps", "_get_synonym_maps"),
        ("get_data_source_connections", "_get_data_source_connections"),
        ("get_indexers", "_get_indexers"),
        ("get_skillsets", "_get_skillsets"),
    ],
)
def test_custom_list_wrappers_forward_search_paging(public_method, generated_method):
    from azure.search.documents.indexes import SearchIndexerClient

    client = (
        _client() if public_method == "get_synonym_maps" else SearchIndexerClient(ENDPOINT, AzureKeyCredential(KEY))
    )
    generated_owner = (
        "_SearchIndexClientOperationsMixin"
        if public_method == "get_synonym_maps"
        else "_SearchIndexerClientOperationsMixin"
    )
    patch_target = "azure.search.documents.indexes._operations._operations." f"{generated_owner}.{generated_method}"

    with mock.patch(patch_target, return_value=[]) as mock_list:
        result = getattr(client, public_method)(
            select=["name"],
            search="hot",
            page_size=2,
            search_type="prefix",
        )

    assert result == []
    mock_list.assert_called_once_with(
        select=["name"],
        search="hot",
        page_size=2,
        search_type="prefix",
    )
