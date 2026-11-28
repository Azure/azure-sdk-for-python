# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline tests for live-test preparation without service-wide cleanup."""

from types import SimpleNamespace
from unittest import mock

import pytest

from search_service_preparer import FAKE_SEARCH_ENDPOINT, search_decorator


class TestSearchServicePreparer:
    @pytest.mark.parametrize("is_live", [False, True])
    def test_search_decorator_forwards_endpoint_without_accessing_service(self, is_live):
        @search_decorator()
        def scenario(test, endpoint):
            assert test.is_live is is_live
            return endpoint

        with (
            mock.patch("search_service_preparer.get_credential", create=True) as credential,
            mock.patch("azure.search.documents.indexes.SearchIndexClient") as index_client,
            mock.patch("azure.search.documents.indexes.SearchIndexerClient") as indexer_client,
        ):
            result = scenario(
                SimpleNamespace(is_live=is_live),
                search_service_endpoint=FAKE_SEARCH_ENDPOINT,
                unused_setting="ignored",
            )

        assert result == FAKE_SEARCH_ENDPOINT
        credential.assert_not_called()
        index_client.assert_not_called()
        indexer_client.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("is_live", [False, True])
    async def test_search_decorator_forwards_settings_without_accessing_service_async(self, is_live):
        @search_decorator()
        async def scenario(test, endpoint, **kwargs):
            assert test.is_live is is_live
            return endpoint, kwargs["search_storage_container_name"]

        with (
            mock.patch("search_service_preparer.get_credential", create=True) as credential,
            mock.patch("azure.search.documents.indexes.SearchIndexClient") as index_client,
            mock.patch("azure.search.documents.indexes.SearchIndexerClient") as indexer_client,
        ):
            result = await scenario(
                SimpleNamespace(is_live=is_live),
                search_service_endpoint=FAKE_SEARCH_ENDPOINT,
                search_storage_container_name="test-container",
            )

        assert result == (FAKE_SEARCH_ENDPOINT, "test-container")
        credential.assert_not_called()
        index_client.assert_not_called()
        indexer_client.assert_not_called()
