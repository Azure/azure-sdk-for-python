# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for ``SearchIndexClient`` preview list-paging kwargs."""

from __future__ import annotations

import json
from unittest import mock

import pytest

from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.rest import HttpRequest

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex

from _capabilities import require_capability

ENDPOINT = "https://my-search-service.search.windows.net"
KEY = "fake-api-key"


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
    response.vector_search = {
        "topicGraphProfiles": [
            {
                "name": "topics",
                "indexName": "hotel-topics",
                "defaultKind": "diverse",
                "defaultDiversityFactor": 0.35,
                "defaultMinDiversityPoolSize": 2500,
            }
        ]
    }
    response.permission_filter_option = None
    response.purview_enabled = None
    response.graph_profile = {"kind": "edgeList", "provenanceIndexName": "hotel-chunks"}
    response.share_point_connector_app_registration = {
        "applicationId": "11111111-1111-1111-1111-111111111111",
        "federatedCredentialId": "22222222-2222-2222-2222-222222222222",
    }
    response.one_lake_security_source = {
        "fabricWorkspaceId": "33333333-3333-3333-3333-333333333333",
        "lakehouseId": "44444444-4444-4444-4444-444444444444",
    }
    response.e_tag = '"etag"'
    return response


class TestSearchIndexClientDelete:
    @pytest.mark.parametrize("resource", ["index", "synonym_map", "alias", "knowledge_base", "knowledge_source"])
    def test_delete_resource_by_name_preserves_condition_and_etag(self, resource):
        with _client() as client:
            with mock.patch.object(client, "_delete_" + resource) as operation:
                getattr(client, "delete_" + resource)(
                    "owned-resource", match_condition=MatchConditions.IfPresent, etag='"etag"'
                )
        operation.assert_called_once_with(
            name="owned-resource", match_condition=MatchConditions.IfPresent, etag='"etag"'
        )


class TestSearchIndexClientKnowledgeBase:
    def test_create_or_update_knowledge_base_accepts_ga_model_constructor(self):
        from azure.search.documents.indexes import types
        from azure.search.documents.indexes.models import KnowledgeBaseAzureOpenAIModel, KnowledgeBaseModelKind

        model = types.KnowledgeBaseModel(
            kind=KnowledgeBaseModelKind.AZURE_OPEN_AI,
            azureOpenAIParameters={"resourceUri": "https://example.openai.azure.com", "deploymentId": "query"},
        )
        base = types.KnowledgeBase(name="owned-base", knowledgeSources=[], models=[model])
        with _client() as client:
            with mock.patch.object(client, "_create_or_update_knowledge_base") as operation:
                client.create_or_update_knowledge_base(base)

        submitted = operation.call_args.kwargs["knowledge_base"]
        assert operation.call_args.kwargs["name"] == "owned-base"
        assert isinstance(submitted.models[0], KnowledgeBaseAzureOpenAIModel)
        assert submitted.as_dict()["models"] == [model]

    @pytest.mark.parametrize("kind", ["microsoftRetriever1", "openAICompatible"])
    def test_create_or_update_knowledge_base_accepts_preview_model_inputs(self, kind):
        from azure.search.documents.indexes import types
        from azure.search.documents.indexes.models import KnowledgeBaseModelKind

        require_capability(
            "azure.search.documents.indexes.types.KnowledgeBaseModelInput",
            (
                "azure.search.documents.indexes.types.KnowledgeBaseMicrosoftRetriever1Model"
                if kind == "microsoftRetriever1"
                else "azure.search.documents.indexes.types.KnowledgeBaseOpenAICompatibleModel"
            ),
        )
        if kind == "microsoftRetriever1":
            model = types.KnowledgeBaseMicrosoftRetriever1Model(kind=KnowledgeBaseModelKind.MICROSOFT_RETRIEVER1)
        else:
            model = types.KnowledgeBaseOpenAICompatibleModel(
                kind=KnowledgeBaseModelKind.OPEN_AI_COMPATIBLE,
                openAICompatibleParameters={
                    "uri": "https://example.invalid/chat/completions",
                    "modelName": "gpt-4o",
                    "headers": {"api-key": "synthetic-key"},
                },
            )
        base = types.KnowledgeBase(name="owned-base", knowledgeSources=[], models=[model])
        with _client() as client:
            with mock.patch.object(client, "_create_or_update_knowledge_base") as operation:
                client.create_or_update_knowledge_base(base)

        submitted = operation.call_args.kwargs["knowledge_base"]
        assert submitted.models[0].kind == kind
        assert submitted.as_dict()["models"] == [model]


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
            "azure.search.documents.indexes.models.SearchIndex.purview_enabled",
            "azure.search.documents.indexes.models.SearchIndex.one_lake_security_source",
            "azure.search.documents.indexes.models.SearchIndex.share_point_connector_app_registration",
            "azure.search.documents.indexes.models.VectorSearch.topic_graph_profiles",
            "azure.search.documents.indexes.models.GraphProfile.provenance_index_name",
        )

        list(_client().list_indexes(select=["name"], search="hot", page_size=3, search_type="prefix"))

        mock_list_select.assert_called_once()
        kwargs = mock_list_select.call_args.kwargs
        assert kwargs["select"] == ["name"]
        assert kwargs["search"] == "hot"
        assert kwargs["page_size"] == 3
        assert kwargs["search_type"] == "prefix"
        response = _index_response_stub()
        converted = kwargs["cls"]([response])
        assert isinstance(converted[0], SearchIndex)
        assert converted[0].name == "hotels"
        assert converted[0].graph_profile.kind == "edgeList"
        serialized = converted[0].as_dict()
        assert serialized["graphProfile"] == response.graph_profile
        assert serialized["vectorSearch"] == response.vector_search
        assert serialized["oneLakeSecuritySource"] == response.one_lake_security_source
        assert serialized["sharePointConnectorAppRegistration"] == response.share_point_connector_app_registration

    def test_list_indexes_projection_preserves_graph_configuration(self):
        from azure.search.documents.indexes._operations._patch import _convert_index_response
        from azure.search.documents.indexes.models._models import SearchIndexResponse

        require_capability("azure.search.documents.indexes.models.SearchIndex.graph_profile")
        response = SearchIndexResponse(
            {
                "name": "hotels",
                "fields": [],
                "graphProfile": {"kind": "edgeList"},
                "oneLakeSecuritySource": {"fabricWorkspaceId": "workspace", "lakehouseId": "lakehouse"},
            }
        )
        converted = _convert_index_response(response).as_dict()
        assert converted["graphProfile"] == {"kind": "edgeList"}
        assert converted["oneLakeSecuritySource"]["lakehouseId"] == "lakehouse"


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
        "_SearchIndexClientOperationsMixin._upload_knowledge_source_file"
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
        "_SearchIndexClientOperationsMixin._upload_knowledge_source_file"
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
        ("get_synonym_maps", "list_synonym_maps"),
        ("get_data_source_connections", "list_data_source_connections"),
        ("get_indexers", "list_indexers"),
        ("get_skillsets", "list_skillsets"),
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


class TestSearchIndexClientFileIngestion:
    @pytest.mark.parametrize("operation", ["multipart", "replacement"])
    def test_begin_ingest_knowledge_source_file_returns_typed_poller(self, operation):
        from azure.search.documents.indexes.models import KnowledgeSourceFile

        method = f"begin_ingest_knowledge_source_file_{operation}"
        require_capability(f"azure.search.documents.indexes.SearchIndexClient.{method}")
        response = mock.Mock()
        response.http_response.headers = {}
        response.http_response.json.return_value = {"result": {"fileId": "file-1"}}
        initial = f"_ingest_knowledge_source_file_{operation}_initial"
        kwargs = {"file_id": "file-1"} if operation == "replacement" else {}
        client = _client()
        with mock.patch.object(client, initial, return_value=response):
            poller = getattr(client, method)(name="files", body={}, polling=False, **kwargs)
            result = poller.result()

        assert isinstance(result, KnowledgeSourceFile)
        assert result.file_id == "file-1"

    @pytest.mark.parametrize("operation", ["multipart", "replacement"])
    def test_begin_ingest_failed_monitor_raises(self, operation):
        method = f"begin_ingest_knowledge_source_file_{operation}"
        require_capability(f"azure.search.documents.indexes.SearchIndexClient.{method}")
        location = f"{ENDPOINT}/knowledgesources('files')/files/operations/operation-1"
        accepted = mock.Mock()
        accepted.http_response.status_code = 202
        accepted.http_response.request = HttpRequest(
            "POST", ENDPOINT, headers={"x-ms-client-request-id": "offline-ingestion"}
        )
        accepted.http_response.headers = {"operation-location": location}
        accepted.http_response.json.return_value = {"status": "Running"}
        accepted.http_response.text.return_value = '{"status": "Running"}'
        failed = mock.Mock()
        failed.http_response.status_code = 200
        failed.http_response.reason = "OK"
        failed.http_response.headers = {}
        failed.http_response.json.return_value = {
            "status": "Failed",
            "error": {"code": "ExtractionFailed", "message": "Fixture extraction failed"},
        }
        failed.http_response.text.return_value = json.dumps(failed.http_response.json.return_value)
        kwargs = {"file_id": "file-1"} if operation == "replacement" else {}
        with _client() as client:
            with mock.patch.object(client, f"_ingest_knowledge_source_file_{operation}_initial", return_value=accepted):
                with mock.patch.object(client._client._pipeline, "run", return_value=failed) as poll:
                    poller = getattr(client, method)(name="files", body={}, polling_interval=0, **kwargs)
                    with pytest.raises(HttpResponseError, match="Fixture extraction failed") as error:
                        poller.result(timeout=5)
        assert poller.status() == "Failed"
        assert error.value.error.code == "ExtractionFailed"
        poll.assert_called_once()
        assert poll.call_args.args[0].method == "GET"
        assert poll.call_args.args[0].url == location


class TestSearchIndexClientKnowledgeSource:
    @pytest.mark.parametrize("scenario", ["facet_hint", "graph_cache"])
    def test_create_or_update_knowledge_source_preserves_preview_configuration(self, scenario):
        from _preview_helpers import assert_knowledge_source_configuration, knowledge_source_configuration

        source = knowledge_source_configuration(scenario)
        client = _client()
        with mock.patch.object(client, "_create_or_update_knowledge_source", return_value=source) as create:
            result = client.create_or_update_knowledge_source(source)

        assert result is source
        assert create.call_args.kwargs["prefer"] == "return=representation"
        assert_knowledge_source_configuration(create.call_args.kwargs["knowledge_source"].as_dict(), scenario)
