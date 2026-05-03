# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for ``SearchClient`` patched public behavior."""

from __future__ import annotations

from unittest import mock

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.paging import ItemPaged

from azure.search.documents import ApiVersion, IndexDocumentsBatch, RequestEntityTooLargeError, SearchClient
from azure.search.documents._operations._patch import SearchPageIterator
from azure.search.documents.models import FacetResult, IndexingResult, SearchResult
from azure.search.documents.models._models import SearchDocumentsResult

SEARCH_ENDPOINT = "https://my-search-service.search.windows.net"
INDEX_NAME = "hotel-index"
API_KEY = "fake-api-key"
AUDIENCE = "https://search.azure.com/"
DOCUMENT_KEY = "1"
REPLACEMENT_DOCUMENT_KEY = "2"
SEARCH_TEXT = "historic hotel"
SEMANTIC_QUERY = "historic lodging"
SUGGESTER_NAME = "hotel-name-suggester"
SOURCE_AUTHORIZATION = "aad:hotel-reader"
CONTINUATION_TOKEN = "encoded-next-page-token"
QUERY_WITHOUT_SUGGESTER = "missing-suggester"

CREDENTIAL = AzureKeyCredential(API_KEY)

DOCUMENT_METHODS = [
    "upload_documents",
    "delete_documents",
    "merge_documents",
    "merge_or_upload_documents",
]
DOCUMENT_ACTIONS = dict(zip(DOCUMENT_METHODS, ["upload", "delete", "merge", "mergeOrUpload"]))


def create_search_client(**kwargs):
    return SearchClient(SEARCH_ENDPOINT, INDEX_NAME, CREDENTIAL, **kwargs)


def create_search_documents_result(*documents):
    result = SearchDocumentsResult()
    if not documents:
        documents = ({"HotelId": DOCUMENT_KEY, "HotelName": "Northwind Lodge"},)
    result.results = [SearchResult(document) for document in documents]
    return result


def create_indexing_result(document_key=DOCUMENT_KEY, *, succeeded=True, status_code=200):
    result = IndexingResult()
    result.key = document_key
    result.succeeded = succeeded
    result.status_code = status_code
    return result


def get_search_request(mock_search_post):
    return mock_search_post.call_args.kwargs["body"]


class TestSearchClientConstructor:
    def test_constructor_uses_public_parameter_order_and_translates_audience(self):
        client = create_search_client(audience=AUDIENCE)

        assert client._config.endpoint == SEARCH_ENDPOINT
        assert client._config.index_name == INDEX_NAME
        assert client._config.credential is CREDENTIAL
        assert client._config.credential_scopes == ["https://search.azure.com/.default"]

    def test_constructor_accepts_supported_api_version_enum(self):
        client = create_search_client(api_version=ApiVersion.V2020_06_30)

        assert client._config.api_version == ApiVersion.V2020_06_30


class TestSearchRequestBuilding:
    @mock.patch("azure.search.documents._operations._operations._SearchClientOperationsMixin._search_post")
    def test_search_returns_lazy_pager_and_builds_search_request(self, mock_search_post):
        mock_search_post.return_value = create_search_documents_result()
        client = create_search_client()

        result = client.search(
            search_text=SEARCH_TEXT,
            include_total_count=True,
            facets=["Category,count:5"],
            filter="Rating ge 4",
            highlight_fields="HotelName, Description",
            highlight_post_tag="</strong>",
            highlight_pre_tag="<strong>",
            minimum_coverage=80.0,
            order_by=["Rating asc"],
            query_type="semantic",
            scoring_parameters=["location--122.1,47.6"],
            scoring_profile="geo-boost",
            semantic_query=SEMANTIC_QUERY,
            search_fields=["HotelName", "Description"],
            search_mode="all",
            query_answer="extractive",
            query_answer_count=3,
            query_answer_threshold=0.8,
            query_caption="extractive",
            query_caption_highlight_enabled=False,
            semantic_configuration_name="hotel-semantic-config",
            select=["HotelId", "HotelName"],
            skip=2,
            top=5,
            scoring_statistics="global",
            session_id="session-1",
            vector_queries=[],
            vector_filter_mode="postFilter",
            semantic_error_mode="partial",
            semantic_max_wait_in_milliseconds=750,
            debug="semantic",
            x_ms_enable_elevated_read=True,
            x_ms_query_source_authorization=SOURCE_AUTHORIZATION,
        )

        assert isinstance(result, ItemPaged)
        assert result._page_iterator_class is SearchPageIterator
        mock_search_post.assert_not_called()

        document = next(result)

        assert document["HotelId"] == DOCUMENT_KEY
        assert document["@search.score"] is None
        mock_search_post.assert_called_once()
        assert mock_search_post.call_args.args == ()
        assert mock_search_post.call_args.kwargs["x_ms_enable_elevated_read"] is True
        assert mock_search_post.call_args.kwargs["x_ms_query_source_authorization"] == SOURCE_AUTHORIZATION
        search_request = get_search_request(mock_search_post)
        assert search_request.search_text == SEARCH_TEXT
        assert search_request.include_total_count is True
        assert search_request.facets == ["Category,count:5"]
        assert search_request.filter == "Rating ge 4"
        assert search_request.highlight_fields == ["HotelName", "Description"]
        assert search_request.highlight_post_tag == "</strong>"
        assert search_request.highlight_pre_tag == "<strong>"
        assert search_request.minimum_coverage == 80.0
        assert search_request.order_by == ["Rating asc"]
        assert search_request.query_type == "semantic"
        assert search_request.scoring_parameters == ["location--122.1,47.6"]
        assert search_request.scoring_profile == "geo-boost"
        assert search_request.semantic_query == SEMANTIC_QUERY
        assert search_request.search_fields == ["HotelName", "Description"]
        assert search_request.search_mode == "all"
        assert search_request.answers == "extractive|count-3,threshold-0.8"
        assert search_request.captions == "extractive|highlight-false"
        assert search_request.semantic_configuration_name == "hotel-semantic-config"
        assert search_request.select == ["HotelId", "HotelName"]
        assert search_request.skip == 2
        assert search_request.top == 5
        assert search_request.scoring_statistics == "global"
        assert search_request.session_id == "session-1"
        assert search_request.vector_queries == []
        assert search_request.vector_filter_mode == "postFilter"
        assert search_request.semantic_error_handling == "partial"
        assert search_request.semantic_max_wait_in_milliseconds == 750
        assert search_request.debug == "semantic"

    @mock.patch("azure.search.documents._operations._operations._SearchClientOperationsMixin._search_post")
    def test_search_accepts_comma_delimited_select(self, mock_search_post):
        mock_search_post.return_value = create_search_documents_result()
        client = create_search_client()

        result = client.search(search_text=SEARCH_TEXT, select="HotelId,HotelName")
        next(result)

        assert get_search_request(mock_search_post).select == ["HotelId", "HotelName"]

    @mock.patch("azure.search.documents._operations._operations._SearchClientOperationsMixin._search_post")
    def test_search_metadata_accessors_fetch_first_page_once_and_clear_continuation(self, mock_search_post):
        search_result = create_search_documents_result()
        search_result.count = 12
        search_result.coverage = 98.5
        search_result.answers = [mock.Mock(key="answer-1")]
        facet_bucket = FacetResult()
        facet_bucket.count = 4
        search_result.facets = {"Category": [facet_bucket]}
        mock_search_post.return_value = search_result
        client = create_search_client()
        result = client.search(search_text=SEARCH_TEXT)

        assert result.get_count() == 12
        result._first_page_iterator_instance.continuation_token = CONTINUATION_TOKEN

        assert result.get_coverage() == 98.5
        assert result.get_answers() == search_result.answers
        assert result.get_facets() == {"Category": [{"count": 4}]}
        assert result._first_page_iterator_instance.continuation_token is None
        mock_search_post.assert_called_once()

    @mock.patch("azure.search.documents._operations._operations._SearchClientOperationsMixin._search_post")
    def test_search_metadata_accessors_return_none_when_metadata_is_absent(self, mock_search_post):
        mock_search_post.return_value = create_search_documents_result()
        client = create_search_client()
        result = client.search(search_text=SEARCH_TEXT)

        assert result.get_count() is None
        assert result.get_coverage() is None
        assert result.get_facets() is None
        mock_search_post.assert_called_once()


class TestSearchSuggestionRequests:
    @mock.patch("azure.search.documents._operations._operations._SearchClientOperationsMixin._suggest_post")
    def test_suggest_forwards_public_arguments_to_generated_operation(self, mock_suggest_post):
        expected = [mock.Mock(text="Northwind Lodge")]
        mock_suggest_post.return_value = mock.Mock(results=expected)
        client = create_search_client()

        results = client.suggest(
            search_text=SEARCH_TEXT,
            suggester_name=SUGGESTER_NAME,
            filter="Rating ge 4",
            use_fuzzy_matching=True,
            highlight_post_tag="</strong>",
            highlight_pre_tag="<strong>",
            minimum_coverage=80.0,
            order_by=["Rating asc"],
            search_fields=["HotelName"],
            select=["HotelId", "HotelName"],
            top=3,
        )

        assert results == expected
        mock_suggest_post.assert_called_once_with(
            search_text=SEARCH_TEXT,
            suggester_name=SUGGESTER_NAME,
            filter="Rating ge 4",
            use_fuzzy_matching=True,
            highlight_post_tag="</strong>",
            highlight_pre_tag="<strong>",
            minimum_coverage=80.0,
            order_by=["Rating asc"],
            search_fields=["HotelName"],
            select=["HotelId", "HotelName"],
            top=3,
        )

    def test_suggest_requires_suggester_name(self):
        client = create_search_client()

        with pytest.raises(TypeError):
            client.suggest(QUERY_WITHOUT_SUGGESTER)

    @mock.patch("azure.search.documents._operations._operations._SearchClientOperationsMixin._autocomplete_post")
    def test_autocomplete_forwards_public_arguments_to_generated_operation(self, mock_autocomplete_post):
        expected = [mock.Mock(text="northwind", query_plus_text="historic northwind")]
        mock_autocomplete_post.return_value = mock.Mock(results=expected)
        client = create_search_client()

        results = client.autocomplete(
            search_text=SEARCH_TEXT,
            suggester_name=SUGGESTER_NAME,
            mode="twoTerms",
            filter="Rating ge 4",
            use_fuzzy_matching=True,
            highlight_post_tag="</strong>",
            highlight_pre_tag="<strong>",
            minimum_coverage=80.0,
            search_fields=["HotelName"],
            top=5,
        )

        assert results == expected
        mock_autocomplete_post.assert_called_once_with(
            search_text=SEARCH_TEXT,
            suggester_name=SUGGESTER_NAME,
            autocomplete_mode="twoTerms",
            filter="Rating ge 4",
            use_fuzzy_matching=True,
            highlight_post_tag="</strong>",
            highlight_pre_tag="<strong>",
            minimum_coverage=80.0,
            search_fields=["HotelName"],
            top=5,
        )

    def test_autocomplete_requires_suggester_name(self):
        client = create_search_client()

        with pytest.raises(TypeError):
            client.autocomplete(QUERY_WITHOUT_SUGGESTER)


class TestSearchDocumentIndexing:
    @pytest.mark.parametrize("method_name", DOCUMENT_METHODS)
    def test_document_action_helpers_create_batch_and_forward_options(self, method_name):
        documents = [
            {"HotelId": DOCUMENT_KEY, "HotelName": "Northwind Lodge"},
            {"HotelId": REPLACEMENT_DOCUMENT_KEY, "HotelName": "Contoso Suites"},
        ]
        with mock.patch.object(SearchClient, "index_documents", return_value=[]) as mock_index_documents:
            client = create_search_client()
            method = getattr(client, method_name)

            result = method(documents, request_id="request-1")

        assert result == []
        mock_index_documents.assert_called_once()
        batch = mock_index_documents.call_args.args[0]
        assert isinstance(batch, IndexDocumentsBatch)
        assert [action.as_dict() for action in batch.actions] == [
            {"@search.action": DOCUMENT_ACTIONS[method_name], **documents[0]},
            {"@search.action": DOCUMENT_ACTIONS[method_name], **documents[1]},
        ]
        assert mock_index_documents.call_args.kwargs == {"request_id": "request-1"}

    @mock.patch("azure.search.documents._operations._operations._SearchClientOperationsMixin._index")
    def test_index_documents_maps_413_and_returns_indexing_results(self, mock_index):
        expected = [create_indexing_result()]
        mock_index.return_value = mock.Mock(results=expected)
        client = create_search_client()
        batch = IndexDocumentsBatch()
        batch.add_upload_actions([{"HotelId": DOCUMENT_KEY, "HotelName": "Northwind Lodge"}])

        results = client.index_documents(batch, request_id="request-1")

        assert results == expected
        mock_index.assert_called_once()
        assert mock_index.call_args.kwargs["batch"] is batch
        assert mock_index.call_args.kwargs["error_map"] == {413: RequestEntityTooLargeError}
        assert mock_index.call_args.kwargs["request_id"] == "request-1"

    @mock.patch("azure.search.documents._operations._operations._SearchClientOperationsMixin._index")
    def test_index_documents_splits_batch_when_request_is_too_large(self, mock_index):
        first_result = create_indexing_result(DOCUMENT_KEY)
        second_result = create_indexing_result(REPLACEMENT_DOCUMENT_KEY)
        mock_index.side_effect = [
            RequestEntityTooLargeError("request body too large"),
            mock.Mock(results=[first_result]),
            mock.Mock(results=[second_result]),
        ]
        client = create_search_client()
        batch = IndexDocumentsBatch()
        batch.add_upload_actions(
            [
                {"HotelId": DOCUMENT_KEY, "HotelName": "Northwind Lodge"},
                {"HotelId": REPLACEMENT_DOCUMENT_KEY, "HotelName": "Contoso Suites"},
            ]
        )

        results = client.index_documents(batch)

        assert results == [first_result, second_result]
        assert [len(call.kwargs["batch"].actions) for call in mock_index.call_args_list] == [2, 1, 1]

    @mock.patch("azure.search.documents._operations._operations._SearchClientOperationsMixin._index")
    def test_index_documents_raises_request_too_large_for_single_action(self, mock_index):
        mock_index.side_effect = RequestEntityTooLargeError("request body too large")
        client = create_search_client()
        batch = IndexDocumentsBatch()
        batch.add_upload_actions([{"HotelId": DOCUMENT_KEY, "HotelName": "Northwind Lodge"}])

        with pytest.raises(RequestEntityTooLargeError):
            client.index_documents(batch)
