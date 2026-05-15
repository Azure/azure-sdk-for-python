# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async unit tests for ``SearchIndexClient`` preview list-paging kwargs."""

from __future__ import annotations

from unittest import mock

import pytest
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureKeyCredential

from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex

from _capabilities import require_capability

ENDPOINT = "https://my-search-service.search.windows.net"
KEY = "fake-api-key"


def _client() -> SearchIndexClient:
    return SearchIndexClient(ENDPOINT, AzureKeyCredential(KEY))


def _empty_async_pager(*_args, **_kwargs):
    pager = mock.MagicMock(spec=AsyncItemPaged)

    async def _aiter():
        for _ in ():
            yield _

    pager.__aiter__ = lambda self: _aiter()
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
    response.e_tag = '"etag"'
    return response


@pytest.mark.asyncio
class TestListIndexesAsync:
    async def test_list_indexes_forwards_top_skip_count(self):
        require_capability(
            "azure.search.documents.indexes.aio.SearchIndexClient.list_indexes.top",
            "azure.search.documents.indexes.aio.SearchIndexClient.list_indexes.skip",
            "azure.search.documents.indexes.aio.SearchIndexClient.list_indexes.count",
        )

        with mock.patch(
            "azure.search.documents.indexes.aio._operations._operations."
            "_SearchIndexClientOperationsMixin._list_indexes",
            side_effect=_empty_async_pager,
        ) as mock_list:
            pager = _client().list_indexes(top=10, skip=5, count=True)
            async for _ in pager:
                pass

        mock_list.assert_called_once()
        kwargs = mock_list.call_args.kwargs
        assert kwargs["top"] == 10
        assert kwargs["skip"] == 5
        assert kwargs["count"] is True

    async def test_list_indexes_with_select_forwards_paging_kwargs(self):
        require_capability(
            "azure.search.documents.indexes.aio.SearchIndexClient.list_indexes.top",
            "azure.search.documents.indexes.aio.SearchIndexClient.list_indexes.skip",
            "azure.search.documents.indexes.aio.SearchIndexClient.list_indexes.count",
        )

        with mock.patch(
            "azure.search.documents.indexes.aio._operations._operations."
            "_SearchIndexClientOperationsMixin._list_indexes_with_selected_properties",
            side_effect=_empty_async_pager,
        ) as mock_list_select:
            pager = _client().list_indexes(select=["name"], top=3, skip=1, count=False)
            async for _ in pager:
                pass

        mock_list_select.assert_called_once()
        kwargs = mock_list_select.call_args.kwargs
        assert kwargs["select"] == ["name"]
        assert kwargs["top"] == 3
        assert kwargs["skip"] == 1
        assert kwargs["count"] is False
        converted = kwargs["cls"]([_index_response_stub()])
        assert isinstance(converted[0], SearchIndex)
        assert converted[0].name == "hotels"


@pytest.mark.asyncio
class TestListIndexNamesAsync:
    async def test_list_index_names_forwards_top_skip_count(self):
        require_capability(
            "azure.search.documents.indexes.aio.SearchIndexClient.list_index_names.top",
            "azure.search.documents.indexes.aio.SearchIndexClient.list_index_names.skip",
            "azure.search.documents.indexes.aio.SearchIndexClient.list_index_names.count",
        )

        with mock.patch(
            "azure.search.documents.indexes.aio._operations._operations."
            "_SearchIndexClientOperationsMixin._list_indexes",
            side_effect=_empty_async_pager,
        ) as mock_list:
            pager = _client().list_index_names(top=20, skip=0, count=True)
            async for _ in pager:
                pass

        mock_list.assert_called_once()
        kwargs = mock_list.call_args.kwargs
        assert kwargs["top"] == 20
        assert kwargs["skip"] == 0
        assert kwargs["count"] is True
        assert callable(kwargs["cls"])
