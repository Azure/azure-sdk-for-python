# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

try:
    from unittest import mock
except ImportError:
    import mock

from azure.core.paging import ItemPaged
from azure.core.credentials import AzureKeyCredential

from azure.search.documents._generated.models import (
    IndexBatch,
    SearchDocumentsResult,
    SearchResult,
)
from azure.search.documents._search_client import SearchPageIterator

from azure.search.documents import (
    IndexDocumentsBatch,
    SearchClient,
    RequestEntityTooLargeError,
    ApiVersion,
)
from azure.search.documents.models import odata

CREDENTIAL = AzureKeyCredential(key="test_api_key")

CRUD_METHOD_NAMES = [
    "upload_documents",
    "delete_documents",
    "merge_documents",
    "merge_or_upload_documents",
]

CRUD_METHOD_MAP = dict(
    zip(CRUD_METHOD_NAMES, ["upload", "delete", "merge", "mergeOrUpload"])
)


class Test_odata(object):
    def test_const(self):
        assert odata("no escapes") == "no escapes"

    def test_numbers(self):
        assert odata("foo eq {foo}", foo=10) == "foo eq 10"

    def test_string(self):
        assert odata("foo eq {foo}", foo="a string") == "foo eq 'a string'"

    def test_mixed(self):
        expected = "foo eq 'a string' and bar le 10"
        out = odata("foo eq {foo} and bar le {bar}", foo="a string", bar=10)
        assert out == expected

    def test_escape_single_quote(self):
        assert odata("foo eq {foo}", foo="a '' str'ing") == "foo eq 'a '''' str''ing'"

    def test_prevent_double_quoting(self):
        assert odata("foo eq '{foo}'", foo="a string") == "foo eq 'a string'"


class TestSearchClient(object):
    def test_init(self):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        assert client._headers == {
            "api-key": "test_api_key",
            "Accept": "application/json;odata.metadata=none",
        }

    def test_credential_roll(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchClient("endpoint", "index name", credential)
        assert client._headers == {
            "api-key": "old_api_key",
            "Accept": "application/json;odata.metadata=none",
        }
        credential.update("new_api_key")
        assert client._headers == {
            "api-key": "new_api_key",
            "Accept": "application/json;odata.metadata=none",
        }

    def test_headers_merge(self):
        credential = AzureKeyCredential(key="test_api_key")
        client = SearchClient("endpoint", "index name", credential)
        orig = {"foo": "bar"}
        result = client._merge_client_headers(orig)
        assert result is not orig
        assert result == {
            "api-key": "test_api_key",
            "Accept": "application/json;odata.metadata=none",
            "foo": "bar",
        }

    def test_repr(self):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        assert repr(client) == "<SearchClient [endpoint={}, index={}]>".format(
            repr("endpoint"), repr("index name")
        )

    @mock.patch(
        "azure.search.documents._generated.v2020_06_preview.operations._documents_operations.DocumentsOperations.count"
    )
    def test_get_document_count(self, mock_count):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        client.get_document_count()
        assert mock_count.called
        assert mock_count.call_args[0] == ()
        assert len(mock_count.call_args[1]) == 1
        assert mock_count.call_args[1]["headers"] == client._headers


    @mock.patch(
        "azure.search.documents._generated.v2020_06_preview.operations._documents_operations.DocumentsOperations.get"
    )
    def test_get_document(self, mock_get):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        client.get_document("some_key")
        assert mock_get.called
        assert mock_get.call_args[0] == ()
        assert len(mock_get.call_args[1]) == 3
        assert mock_get.call_args[1]["headers"] == client._headers
        assert mock_get.call_args[1]["key"] == "some_key"
        assert mock_get.call_args[1]["selected_fields"] == None

        mock_get.reset()

        client.get_document("some_key", selected_fields="foo")
        assert mock_get.called
        assert mock_get.call_args[0] == ()
        assert len(mock_get.call_args[1]) == 3
        assert mock_get.call_args[1]["headers"] == client._headers
        assert mock_get.call_args[1]["key"] == "some_key"
        assert mock_get.call_args[1]["selected_fields"] == "foo"

    @mock.patch(
        "azure.search.documents._generated.v2020_06_preview.operations._documents_operations.DocumentsOperations.search_post"
    )
    def test_search_query_argument(self, mock_search_post):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        result = client.search(search_text="search text")
        assert isinstance(result, ItemPaged)
        assert result._page_iterator_class is SearchPageIterator
        search_result = SearchDocumentsResult()
        search_result.results = [SearchResult(additional_properties={"key": "val"})]
        mock_search_post.return_value = search_result
        assert not mock_search_post.called
        next(result)
        assert mock_search_post.called
        assert mock_search_post.call_args[0] == ()
        assert (
            mock_search_post.call_args[1]["search_request"].search_text == "search text"
        )

    @mock.patch(
        "azure.search.documents._generated.v2020_06_preview.operations._documents_operations.DocumentsOperations.suggest_post"
    )
    def test_suggest_query_argument(self, mock_suggest_post):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        result = client.suggest(
            search_text="search text", suggester_name="sg"
        )
        assert mock_suggest_post.called
        assert mock_suggest_post.call_args[0] == ()
        assert mock_suggest_post.call_args[1]["headers"] == client._headers
        assert (
            mock_suggest_post.call_args[1]["suggest_request"].search_text
            == "search text"
        )

    def test_suggest_bad_argument(self):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        with pytest.raises(TypeError) as e:
            client.suggest("bad_query")
            assert str(e) == "Expected a SuggestQuery for 'query', but got {}".format(
                repr("bad_query")
            )

    @mock.patch(
        "azure.search.documents._generated.v2020_06_preview.operations._documents_operations.DocumentsOperations.autocomplete_post"
    )
    def test_autocomplete_query_argument(self, mock_autocomplete_post):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        result = client.autocomplete(
            search_text="search text", suggester_name="sg"
        )
        assert mock_autocomplete_post.called
        assert mock_autocomplete_post.call_args[0] == ()
        assert mock_autocomplete_post.call_args[1]["headers"] == client._headers
        assert (
            mock_autocomplete_post.call_args[1]["autocomplete_request"].search_text
            == "search text"
        )

    @mock.patch(
        "azure.search.documents._generated.v2020_06.operations._documents_operations.DocumentsOperations.count"
    )
    def test_get_document_count_v2020_06_30(self, mock_count):
        client = SearchClient("endpoint", "index name", CREDENTIAL, api_version=ApiVersion.V2020_06_30)
        client.get_document_count()
        assert mock_count.called
        assert mock_count.call_args[0] == ()
        assert len(mock_count.call_args[1]) == 1
        assert mock_count.call_args[1]["headers"] == client._headers

    @mock.patch(
        "azure.search.documents._generated.v2020_06.operations._documents_operations.DocumentsOperations.get"
    )
    def test_get_document_v2020_06_30(self, mock_get):
        client = SearchClient("endpoint", "index name", CREDENTIAL, api_version=ApiVersion.V2020_06_30)
        client.get_document("some_key")
        assert mock_get.called
        assert mock_get.call_args[0] == ()
        assert len(mock_get.call_args[1]) == 3
        assert mock_get.call_args[1]["headers"] == client._headers
        assert mock_get.call_args[1]["key"] == "some_key"
        assert mock_get.call_args[1]["selected_fields"] == None

        mock_get.reset()

        client.get_document("some_key", selected_fields="foo")
        assert mock_get.called
        assert mock_get.call_args[0] == ()
        assert len(mock_get.call_args[1]) == 3
        assert mock_get.call_args[1]["headers"] == client._headers
        assert mock_get.call_args[1]["key"] == "some_key"
        assert mock_get.call_args[1]["selected_fields"] == "foo"

    @mock.patch(
        "azure.search.documents._generated.v2020_06.operations._documents_operations.DocumentsOperations.search_post"
    )
    def test_search_query_argument_v2020_06_30(self, mock_search_post):
        client = SearchClient("endpoint", "index name", CREDENTIAL, api_version=ApiVersion.V2020_06_30)
        result = client.search(search_text="search text")
        assert isinstance(result, ItemPaged)
        assert result._page_iterator_class is SearchPageIterator
        search_result = SearchDocumentsResult()
        search_result.results = [SearchResult(additional_properties={"key": "val"})]
        mock_search_post.return_value = search_result
        assert not mock_search_post.called
        next(result)
        assert mock_search_post.called
        assert mock_search_post.call_args[0] == ()
        assert (
                mock_search_post.call_args[1]["search_request"].search_text == "search text"
        )

    @mock.patch(
        "azure.search.documents._generated.v2020_06.operations._documents_operations.DocumentsOperations.suggest_post"
    )
    def test_suggest_query_argument_v2020_06_30(self, mock_suggest_post):
        client = SearchClient("endpoint", "index name", CREDENTIAL, api_version=ApiVersion.V2020_06_30)
        result = client.suggest(
            search_text="search text", suggester_name="sg"
        )
        assert mock_suggest_post.called
        assert mock_suggest_post.call_args[0] == ()
        assert mock_suggest_post.call_args[1]["headers"] == client._headers
        assert (
                mock_suggest_post.call_args[1]["suggest_request"].search_text
                == "search text"
        )

    @mock.patch(
        "azure.search.documents._generated.v2020_06.operations._documents_operations.DocumentsOperations.autocomplete_post"
    )
    def test_autocomplete_query_argument_v2020_06_30(self, mock_autocomplete_post):
        client = SearchClient("endpoint", "index name", CREDENTIAL, api_version=ApiVersion.V2020_06_30)
        result = client.autocomplete(
            search_text="search text", suggester_name="sg"
        )
        assert mock_autocomplete_post.called
        assert mock_autocomplete_post.call_args[0] == ()
        assert mock_autocomplete_post.call_args[1]["headers"] == client._headers
        assert (
                mock_autocomplete_post.call_args[1]["autocomplete_request"].search_text
                == "search text"
        )

    def test_autocomplete_bad_argument(self):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        with pytest.raises(TypeError) as e:
            client.autocomplete("bad_query")
            assert str(
                e
            ) == "Expected a AutocompleteQuery for 'query', but got {}".format(
                repr("bad_query")
            )

    @pytest.mark.parametrize(
        "arg", [[], ["doc1"], ["doc1", "doc2"]], ids=lambda x: str(len(x)) + " docs"
    )
    @pytest.mark.parametrize("method_name", CRUD_METHOD_NAMES)
    def test_add_method(self, arg, method_name):
        with mock.patch.object(
            SearchClient, "index_documents", return_value=None
        ) as mock_index_documents:
            client = SearchClient("endpoint", "index name", CREDENTIAL)

            method = getattr(client, method_name)
            method(arg, extra="foo")

            assert mock_index_documents.called
            assert len(mock_index_documents.call_args[0]) == 1
            batch = mock_index_documents.call_args[0][0]
            assert isinstance(batch, IndexDocumentsBatch)
            assert all(
                action.action_type == CRUD_METHOD_MAP[method_name]
                for action in batch.actions
            )
            assert [action.additional_properties for action in batch.actions] == arg
            assert mock_index_documents.call_args[1]["headers"] == client._headers
            assert mock_index_documents.call_args[1]["extra"] == "foo"

    @mock.patch(
        "azure.search.documents._generated.v2020_06_preview.operations._documents_operations.DocumentsOperations.index"
    )
    def test_index_documents(self, mock_index):
        client = SearchClient("endpoint", "index name", CREDENTIAL)

        batch = IndexDocumentsBatch()
        actions = batch.add_upload_actions("upload1")
        assert len(actions) == 1
        for x in actions:
            assert x.action_type == "upload"
        actions = batch.add_delete_actions("delete1", "delete2")
        assert len(actions) == 2
        for x in actions:
            assert x.action_type == "delete"
        actions = batch.add_merge_actions(["merge1", "merge2", "merge3"])
        for x in actions:
            assert x.action_type == "merge"
        actions = batch.add_merge_or_upload_actions("merge_or_upload1")
        for x in actions:
            assert x.action_type == "mergeOrUpload"

        client.index_documents(batch, extra="foo")
        assert mock_index.called
        assert mock_index.call_args[0] == ()
        assert len(mock_index.call_args[1]) == 4
        assert mock_index.call_args[1]["headers"] == client._headers
        assert mock_index.call_args[1]["extra"] == "foo"

    def test_request_too_large_error(self):
        with mock.patch.object(SearchClient, "_index_documents_actions", side_effect=RequestEntityTooLargeError("Error")):
            client = SearchClient("endpoint", "index name", CREDENTIAL)
            batch = IndexDocumentsBatch()
            batch.add_upload_actions("upload1")
            with pytest.raises(RequestEntityTooLargeError):
                client.index_documents(batch, extra="foo")
