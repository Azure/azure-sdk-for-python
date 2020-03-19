# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

try:
    from unittest import mock
except ImportError:
    import mock

from azure.search.documents import SearchApiKeyCredential, SearchServiceClient

CREDENTIAL = SearchApiKeyCredential(api_key="test_api_key")


class TestSearchServiceClient(object):
    def test_init(self):
        client = SearchServiceClient("endpoint", CREDENTIAL)
        assert client._client._config.headers_policy.headers == {
            "api-key": "test_api_key",
            "Accept": "application/json;odata.metadata=none",
        }

    def test_repr(self):
        client = SearchServiceClient("endpoint", CREDENTIAL)
        assert repr(client) == "<SearchServiceClient [endpoint={}]>".format(
            repr("endpoint")
        )

    @mock.patch(
        "azure.search.documents._service._generated._search_service_client.SearchServiceClient.get_service_statistics"
    )
    def test_get_service_statistics(self, mock_get_stats):
        client = SearchServiceClient("endpoint", CREDENTIAL)
        client.get_service_statistics()
        assert mock_get_stats.called
        assert mock_get_stats.call_args[0] == ()
        assert mock_get_stats.call_args[1] == {}
