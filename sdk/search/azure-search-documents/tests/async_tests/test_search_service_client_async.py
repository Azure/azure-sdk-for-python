# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import functools
import pytest

try:
    from unittest import mock
except ImportError:
    import mock
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient, SearchIndexerClient

CREDENTIAL = AzureKeyCredential(key="test_api_key")

def await_prepared_test(test_fn):
    """Synchronous wrapper for async test methods. Used to avoid making changes
    upstream to AbstractPreparer (which doesn't await the functions it wraps)
    """

    @functools.wraps(test_fn)
    def run(test_class_instance, *args, **kwargs):
        trim_kwargs_from_test_function(test_fn, kwargs)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_fn(test_class_instance, **kwargs))

    return run

class TestSearchIndexClient(object):
    def test_index_init(self):
        client = SearchIndexClient("endpoint", CREDENTIAL)
        assert client._headers == {
            "api-key": "test_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }

    def test_index_credential_roll(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchIndexClient("endpoint", credential)
        assert client._headers == {
            "api-key": "old_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }
        credential.update("new_api_key")
        assert client._headers == {
            "api-key": "new_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }

    def test_get_search_client(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchIndexClient("endpoint", credential)
        search_client = client.get_search_client('index')
        assert isinstance(search_client, SearchClient)

    def test_index_endpoint_https(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchIndexClient("endpoint", credential)
        assert client._endpoint.startswith('https')

        client = SearchIndexClient("https://endpoint", credential)
        assert client._endpoint.startswith('https')

        with pytest.raises(ValueError):
            client = SearchIndexClient("http://endpoint", credential)

        with pytest.raises(ValueError):
            client = SearchIndexClient(12345, credential)


class TestSearchIndexerClient(object):
    def test_indexer_init(self):
        client = SearchIndexerClient("endpoint", CREDENTIAL)
        assert client._headers == {
            "api-key": "test_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }

    def test_indexer_credential_roll(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchIndexerClient("endpoint", credential)
        assert client._headers == {
            "api-key": "old_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }
        credential.update("new_api_key")
        assert client._headers == {
            "api-key": "new_api_key",
            "Accept": "application/json;odata.metadata=minimal",
        }

    def test_indexer_endpoint_https(self):
        credential = AzureKeyCredential(key="old_api_key")
        client = SearchIndexerClient("endpoint", credential)
        assert client._endpoint.startswith('https')

        client = SearchIndexerClient("https://endpoint", credential)
        assert client._endpoint.startswith('https')

        with pytest.raises(ValueError):
            client = SearchIndexerClient("http://endpoint", credential)

        with pytest.raises(ValueError):
            client = SearchIndexerClient(12345, credential)
