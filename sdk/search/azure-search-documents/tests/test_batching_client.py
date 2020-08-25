# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
try:
    from unittest import mock
except ImportError:
    import mock

from azure.search.documents import (
    SearchIndexDocumentBatchingClient,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

CREDENTIAL = AzureKeyCredential(key="test_api_key")

class TestSearchBatchingClient(object):
    def test_search_index_document_batching_client_kwargs(self):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL, window=100)

        assert client.batch_size == 1000
        assert client._window == 100
        assert client._auto_flush
        client.close()


    def test_batch_queue(self):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL, auto_flush=False)

        assert client._index_documents_batch
        client.add_upload_actions(["upload1"])
        client.add_delete_actions(["delete1", "delete2"])
        client.add_merge_actions(["merge1", "merge2", "merge3"])
        client.add_merge_or_upload_actions(["merge_or_upload1"])
        assert len(client.actions) == 7
        actions = client._index_documents_batch.dequeue_actions()
        assert len(client.actions) == 0
        client._index_documents_batch.enqueue_actions(actions)
        assert len(client.actions) == 7
        actions = client._index_documents_batch.dequeue_actions()
        assert len(client.actions) == 0
        for action in actions:
            client._index_documents_batch.enqueue_action(action)
        assert len(client.actions) == 7


    @mock.patch(
        "azure.search.documents._internal._search_index_document_batching_client.SearchIndexDocumentBatchingClient._process_if_needed"
    )
    def test_process_if_needed(self, mock_process_if_needed):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL, window=1000, auto_flush=False)

        client.add_upload_actions(["upload1"])
        client.add_delete_actions(["delete1", "delete2"])
        assert mock_process_if_needed.called


    @mock.patch(
        "azure.search.documents._internal._search_index_document_batching_client.SearchIndexDocumentBatchingClient._cleanup"
    )
    def test_context_manager(self, mock_cleanup):
        with SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL, auto_flush=False) as client:
            client.add_upload_actions(["upload1"])
            client.add_delete_actions(["delete1", "delete2"])
        assert mock_cleanup.called

    def test_flush(self):
        DOCUMENT = {
            'Category': 'Hotel',
            'HotelId': '1000',
            'Rating': 4.0,
            'Rooms': [],
            'HotelName': 'Azure Inn',
        }
        with mock.patch.object(SearchIndexDocumentBatchingClient, "_index_documents_actions", side_effect=HttpResponseError("Error")):
            with SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL, auto_flush=False) as client:
                client._index_key = "HotelId"
                client.add_upload_actions([DOCUMENT])
                client.flush()
                assert len(client.actions) == 0
