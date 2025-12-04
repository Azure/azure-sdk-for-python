# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest import mock
from azure.core.credentials import AzureKeyCredential
from azure.core.async_paging import AsyncPageIterator
from azure.search.documents.models import (
    FacetResult,
    SearchDocumentsResult,
    SearchResult,
)
from azure.search.documents.aio import SearchClient
from test_search_index_client_async import await_prepared_test

CREDENTIAL = AzureKeyCredential(key="test_api_key")


class TestSearchClientAsync:
    @await_prepared_test
    @mock.patch(
        "azure.search.documents.aio._operations._operations._SearchClientOperationsMixin._search_post"
    )
    async def test_get_count_reset_continuation_token(self, mock_search_post):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        result = await client.search(search_text="search text")
        assert result._page_iterator_class is AsyncPageIterator
        search_result = SearchDocumentsResult()
        search_result.results = [SearchResult({"key": "val"})]
        mock_search_post.return_value = search_result
        await result.__anext__()
        result._first_page_iterator_instance.continuation_token = "fake token"
        await result.get_count()
        assert not result._first_page_iterator_instance.continuation_token

    @await_prepared_test
    @mock.patch(
        "azure.search.documents.aio._operations._operations._SearchClientOperationsMixin._search_post"
    )
    async def test_search_enable_elevated_read(self, mock_search_post):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        result = await client.search(
            search_text="search text",
            x_ms_enable_elevated_read=True,
            x_ms_query_source_authorization="aad:fake-user",
        )
        search_result = SearchDocumentsResult()
        search_result.results = [SearchResult({"key": "val"})]
        mock_search_post.return_value = search_result
        await result.__anext__()

        assert mock_search_post.called
        assert mock_search_post.call_args[1]["x_ms_enable_elevated_read"] is True
        assert mock_search_post.call_args[1]["x_ms_query_source_authorization"] == "aad:fake-user"

    @await_prepared_test
    @mock.patch(
        "azure.search.documents.aio._operations._operations._SearchClientOperationsMixin._search_post"
    )
    async def test_get_facets_with_aggregations(self, mock_search_post):
        client = SearchClient("endpoint", "index name", CREDENTIAL)
        result = await client.search(search_text="*")

        search_result = SearchDocumentsResult()
        search_result.results = [SearchResult({"id": "1"})]

        facet_bucket = FacetResult()
        facet_bucket.count = 4
        facet_bucket.avg = 120.5
        facet_bucket.min = 75.0
        facet_bucket.max = 240.0
        facet_bucket.cardinality = 3

        search_result.facets = {"baseRate": [facet_bucket]}
        mock_search_post.return_value = search_result

        await result.__anext__()
        facets = await result.get_facets()

        assert facets is not None
        assert "baseRate" in facets
        assert len(facets["baseRate"]) == 1
        bucket = facets["baseRate"][0]
        assert bucket["count"] == 4
        assert bucket["avg"] == 120.5
        assert bucket["min"] == 75.0
        assert bucket["max"] == 240.0
        assert bucket["cardinality"] == 3
