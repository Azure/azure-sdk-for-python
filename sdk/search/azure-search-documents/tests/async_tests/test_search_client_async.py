# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
try:
    from unittest import mock
except ImportError:
    import mock
from azure.core.credentials import AzureKeyCredential
from azure.search.documents._generated.models import SearchDocumentsResult, SearchResult
from azure.search.documents.aio import SearchClient
from azure.search.documents.aio._search_client_async import AsyncSearchPageIterator

CREDENTIAL = AzureKeyCredential(key="test_api_key")

class TestSearchClientAsync(object):
    @mock.patch(
        "azure.search.documents._generated.aio.operations._documents_operations.DocumentsOperations.search_post"
    )
    async def test_get_count_reset_continuation_token(self, mock_search_post):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        result = await client.search(search_text="search text")
        assert result._page_iterator_class is AsyncSearchPageIterator
        search_result = SearchDocumentsResult()
        search_result.results = [SearchResult(additional_properties={"key": "val"})]
        mock_search_post.return_value = search_result
        await result.__anext__()
        result._first_page_iterator_instance.continuation_token = "fake token"
        await result.get_count()
        assert not result._first_page_iterator_instance.continuation_token