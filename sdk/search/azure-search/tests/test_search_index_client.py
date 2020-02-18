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

from azure.search.index._generated.models import SearchDocumentsResult, SearchResult
from azure.search.index._search_index_client import _SearchDocumentsPaged

from azure.search import AutocompleteQuery, SearchApiKeyCredential, SearchIndexClient, SearchQuery, SuggestQuery

credential = SearchApiKeyCredential(api_key="test_api_key")

class TestSearchIndexClient(object):

    def test_init(self):
        pass

    def test_search_dns_suffix(self):
        client = SearchIndexClient("service name", "index name", credential)
        assert client._client._config.search_dns_suffix == "search.windows.net"

        client = SearchIndexClient("service name", "index name", credential, search_dns_suffix="DNS suffix")
        assert client._client._config.search_dns_suffix == "DNS suffix"

    def test_repr(self):
        client = SearchIndexClient("service name", "index name", credential)
        assert repr(client) == "<SearchIndexClient [service={}, index={}]>".format(repr("service name"), repr("index name"))

    @mock.patch("azure.search.index._generated.operations._documents_operations.DocumentsOperations.count")
    def test_get_document_count(self, mock_count):
        client = SearchIndexClient("service name", "index name", credential)
        client.get_document_count()
        mock_count.assert_called_once()
        assert mock_count.call_args[0] == ()
        assert mock_count.call_args[1] == {}

    @pytest.mark.parametrize('query', ["search text", SearchQuery(search_text="search text")], ids=repr)
    @mock.patch("azure.search.index._generated.operations._documents_operations.DocumentsOperations.search_post")
    def test_search_query_argument(self, mock_search_post, query):
        client = SearchIndexClient("service name", "index name", credential)
        result = client.search(query)
        assert isinstance(result, ItemPaged)
        assert result._page_iterator_class is _SearchDocumentsPaged
        search_result = SearchDocumentsResult()
        search_result.results = [SearchResult(additional_properties={"key":"val"})]
        mock_search_post.return_value = search_result
        mock_search_post.assert_not_called()
        next(result)
        mock_search_post.assert_called_once()
        assert mock_search_post.call_args[0] == ()
        assert mock_search_post.call_args[1]["search_request"].search_text == "search text"

    def test_search_bad_argument(self):
        client = SearchIndexClient("service name", "index name", credential)
        with pytest.raises(TypeError) as e:
            client.search(10)
            assert str(e) == "Expected a SuggestQuery for 'query', but got {}".format(repr(10))

    @mock.patch("azure.search.index._generated.operations._documents_operations.DocumentsOperations.suggest_post")
    def test_suggest_query_argument(self, mock_suggest_post):
        client = SearchIndexClient("service name", "index name", credential)
        result = client.suggest(SuggestQuery(search_text="search text"))
        mock_suggest_post.assert_called_once()
        assert mock_suggest_post.call_args[0] == ()
        assert mock_suggest_post.call_args[1]["suggest_request"].search_text == "search text"

    def test_suggest_bad_argument(self):
        client = SearchIndexClient("service name", "index name", credential)
        with pytest.raises(TypeError) as e:
            client.suggest("bad_query")
            assert str(e) == "Expected a SuggestQuery for 'query', but got {}".format(repr("bad_query"))

    @mock.patch("azure.search.index._generated.operations._documents_operations.DocumentsOperations.autocomplete_post")
    def test_autocomplete_query_argument(self, mock_autocomplete_post):
        client = SearchIndexClient("service name", "index name", credential)
        result = client.autocomplete(AutocompleteQuery(search_text="search text"))
        mock_autocomplete_post.assert_called_once()
        assert mock_autocomplete_post.call_args[0] == ()
        assert mock_autocomplete_post.call_args[1]["autocomplete_request"].search_text == "search text"

    def test_autocomplete_bad_argument(self):
        client = SearchIndexClient("service name", "index name", credential)
        with pytest.raises(TypeError) as e:
            client.autocomplete("bad_query")
            assert str(e) == "Expected a AutocompleteQuery for 'query', but got {}".format(repr("bad_query"))
