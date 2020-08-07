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

CREDENTIAL = AzureKeyCredential(key="test_api_key")

class TestSearchBatchingClient(object):
    def test_search_index_document_batching_client_kwargs(self):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL, window=100, batch_size=100)

        assert client.batch_size == 100
        assert client._window == 100
        assert client._auto_flush
        client.close()


    def test_batch_queue(self):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL)

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


    def test_succeeded_queue(self):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL)

        assert client._index_documents_batch
        client.add_upload_actions(["upload1"])
        client.add_delete_actions(["delete1", "delete2"])
        client.add_merge_actions(["merge1", "merge2", "merge3"])
        client.add_merge_or_upload_actions(["merge_or_upload1"])
        actions = client._index_documents_batch.dequeue_actions()
        client._index_documents_batch.enqueue_succeeded_actions(actions)
        assert len(client.succeeded_actions) == 7


    def test_failed_queue(self):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL)

        assert client._index_documents_batch
        client.add_upload_actions(["upload1"])
        client.add_delete_actions(["delete1", "delete2"])
        client.add_merge_actions(["merge1", "merge2", "merge3"])
        client.add_merge_or_upload_actions(["merge_or_upload1"])
        actions = client._index_documents_batch.dequeue_actions()
        client._index_documents_batch.enqueue_failed_actions(actions)
        assert len(client.failed_actions) == 7


    @mock.patch(
        "azure.search.documents._internal._search_index_document_batching_client.SearchIndexDocumentBatchingClient.flush"
    )
    def test_flush_if_needed(self, mock_flush):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL, window=1000, batch_size=2)

        client.add_upload_actions(["upload1"])
        client.add_delete_actions(["delete1", "delete2"])
        assert mock_flush.called
        client.close()


    @mock.patch(
        "azure.search.documents._internal._search_index_document_batching_client.SearchIndexDocumentBatchingClient._cleanup"
    )
    def test_context_manager(self, mock_cleanup):
        with SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL) as client:
            client.add_upload_actions(["upload1"])
            client.add_delete_actions(["delete1", "delete2"])
        assert mock_cleanup.called
