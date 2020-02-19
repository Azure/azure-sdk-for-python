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

from azure.search.index._generated.models import IndexAction, IndexBatch as IndexBatchModel, SearchDocumentsResult, SearchResult
from azure.search.index._search_index_client import _SearchDocumentsPaged

from azure.search import AutocompleteQuery, IndexBatch, SearchApiKeyCredential, SearchIndexClient, SearchQuery, SuggestQuery

CREDENTIAL = SearchApiKeyCredential(api_key="test_api_key")

CRUD_METHOD_NAMES = [
    'upload_documents',
    'delete_documents',
    'merge_documents',
    'merge_or_upload_documents'
]

CRUD_METHOD_MAP = dict(zip(CRUD_METHOD_NAMES, ['upload', 'delete', 'merge', 'mergeOrUpload']))

class TestSearchIndexClient(object):

    def test_init(self):
        client = SearchIndexClient("service name", "index name", CREDENTIAL)
        assert client._client._config.headers_policy.headers == {
            "api-key": "test_api_key",
            "Accept": "application/json;odata.metadata=none",
        }

    def test_search_dns_suffix(self):
        client = SearchIndexClient("service name", "index name", CREDENTIAL)
        assert client._client._config.search_dns_suffix == "search.windows.net"

        client = SearchIndexClient("service name", "index name", CREDENTIAL, search_dns_suffix="DNS suffix")
        assert client._client._config.search_dns_suffix == "DNS suffix"

    def test_repr(self):
        client = SearchIndexClient("service name", "index name", CREDENTIAL)
        assert repr(client) == "<SearchIndexClient [service={}, index={}]>".format(repr("service name"), repr("index name"))

    @mock.patch("azure.search.index._generated.operations._documents_operations.DocumentsOperations.count")
    def test_get_document_count(self, mock_count):
        client = SearchIndexClient("service name", "index name", CREDENTIAL)
        client.get_document_count()
        assert mock_count.called
        assert mock_count.call_args[0] == ()
        assert mock_count.call_args[1] == {}

    @mock.patch("azure.search.index._generated.operations._documents_operations.DocumentsOperations.get")
    def test_get_document_count(self, mock_get):
        client = SearchIndexClient("service name", "index name", CREDENTIAL)
        client.get_document("some_key")
        assert mock_get.called
        assert mock_get.call_args[0] == ()
        assert mock_get.call_args[1] == {"key": "some_key", "selected_fields": None}

        mock_get.reset()

        client.get_document("some_key", selected_fields="foo")
        assert mock_get.called
        assert mock_get.call_args[0] == ()
        assert mock_get.call_args[1] == {"key": "some_key", "selected_fields": "foo"}

    @pytest.mark.parametrize('query', ["search text", SearchQuery(search_text="search text")], ids=repr)
    @mock.patch("azure.search.index._generated.operations._documents_operations.DocumentsOperations.search_post")
    def test_search_query_argument(self, mock_search_post, query):
        client = SearchIndexClient("service name", "index name", CREDENTIAL)
        result = client.search(query)
        assert isinstance(result, ItemPaged)
        assert result._page_iterator_class is _SearchDocumentsPaged
        search_result = SearchDocumentsResult()
        search_result.results = [SearchResult(additional_properties={"key":"val"})]
        mock_search_post.return_value = search_result
        assert not mock_search_post.called
        next(result)
        assert mock_search_post.called
        assert mock_search_post.call_args[0] == ()
        assert mock_search_post.call_args[1]["search_request"].search_text == "search text"

    def test_search_bad_argument(self):
        client = SearchIndexClient("service name", "index name", CREDENTIAL)
        with pytest.raises(TypeError) as e:
            client.search(10)
            assert str(e) == "Expected a SuggestQuery for 'query', but got {}".format(repr(10))

    @mock.patch("azure.search.index._generated.operations._documents_operations.DocumentsOperations.suggest_post")
    def test_suggest_query_argument(self, mock_suggest_post):
        client = SearchIndexClient("service name", "index name", CREDENTIAL)
        result = client.suggest(SuggestQuery(search_text="search text"))
        assert mock_suggest_post.called
        assert mock_suggest_post.call_args[0] == ()
        assert mock_suggest_post.call_args[1]["suggest_request"].search_text == "search text"

    def test_suggest_bad_argument(self):
        client = SearchIndexClient("service name", "index name", CREDENTIAL)
        with pytest.raises(TypeError) as e:
            client.suggest("bad_query")
            assert str(e) == "Expected a SuggestQuery for 'query', but got {}".format(repr("bad_query"))

    @mock.patch("azure.search.index._generated.operations._documents_operations.DocumentsOperations.autocomplete_post")
    def test_autocomplete_query_argument(self, mock_autocomplete_post):
        client = SearchIndexClient("service name", "index name", CREDENTIAL)
        result = client.autocomplete(AutocompleteQuery(search_text="search text"))
        assert mock_autocomplete_post.called
        assert mock_autocomplete_post.call_args[0] == ()
        assert mock_autocomplete_post.call_args[1]["autocomplete_request"].search_text == "search text"

    def test_autocomplete_bad_argument(self):
        client = SearchIndexClient("service name", "index name", CREDENTIAL)
        with pytest.raises(TypeError) as e:
            client.autocomplete("bad_query")
            assert str(e) == "Expected a AutocompleteQuery for 'query', but got {}".format(repr("bad_query"))

    @pytest.mark.parametrize('arg', [[], ["doc1"], ["doc1", "doc2"]], ids=lambda x: str(len(x)) + " docs")
    @pytest.mark.parametrize('method_name', CRUD_METHOD_NAMES)
    def test_add_method(self, arg, method_name):
        with mock.patch.object(SearchIndexClient, 'index_batch', return_value=None) as mock_index_batch:
            client = SearchIndexClient("service name", "index name", CREDENTIAL)

            method = getattr(client, method_name)
            method(arg, extra="foo")

            assert mock_index_batch.called
            assert len(mock_index_batch.call_args[0]) == 1
            batch = mock_index_batch.call_args[0][0]
            assert isinstance(batch, IndexBatch)
            assert all(action.action_type == CRUD_METHOD_MAP[method_name] for action in batch.actions)
            assert [action.additional_properties for action in batch.actions] == arg
            assert mock_index_batch.call_args[1] == {"extra": "foo"}

    @mock.patch("azure.search.index._generated.operations._documents_operations.DocumentsOperations.index")
    def test_index_batch(self, mock_index):
        client = SearchIndexClient("service name", "index name", CREDENTIAL)

        batch = IndexBatch()
        batch.add_upload_documents("upload1")
        batch.add_delete_documents("delete1", "delete2")
        batch.add_merge_documents(["merge1", "merge2", 'merge3'])
        batch.add_merge_or_upload_documents("merge_or_upload1")

        client.index_batch(batch, extra="foo")
        assert mock_index.called
        assert mock_index.call_args[0] == ()
        assert len(mock_index.call_args[1]) == 2
        assert mock_index.call_args[1]['extra'] == "foo"
        index_batch = mock_index.call_args[1]['batch']
        assert isinstance(index_batch, IndexBatchModel)
        assert index_batch.actions == batch.actions