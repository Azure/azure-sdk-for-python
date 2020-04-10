# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

try:
    from unittest import mock
except ImportError:
    import mock

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchServiceClient

CREDENTIAL = AzureKeyCredential(key="test_api_key")


class TestSearchServiceClient(object):
    def test_init(self):
        client = SearchServiceClient("endpoint", CREDENTIAL)
        assert client._headers == {
            "api-key": "test_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }

    def test_credential_roll(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchServiceClient("endpoint", credential)
        assert client._headers == {
            "api-key": "old_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }
        credential.update("new_api_key")
        assert client._headers == {
            "api-key": "new_api_key",
            "Accept": "application/json;odata.metadata=minimal",
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
        assert mock_get_stats.call_args[1] == {"headers": client._headers}
