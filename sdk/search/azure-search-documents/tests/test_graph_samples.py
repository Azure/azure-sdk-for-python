# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""Resource ownership and synchronization safety in the EKG samples."""

import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError, ResourceExistsError

from _capabilities import require_capability


@pytest.fixture(name="graph_sample_environment")
def _graph_sample_environment(monkeypatch):
    samples = Path(__file__).resolve().parents[1] / "samples"
    monkeypatch.syspath_prepend(str(samples))
    for name, value in {
        "AZURE_SEARCH_SERVICE_ENDPOINT": "https://sample.search.windows.net",
        "AZURE_SEARCH_API_KEY": "fake-search-key",
        "AZURE_STORAGE_CONNECTION_STRING": "ResourceId=/sample/storage;",
        "AZURE_STORAGE_CONTAINER": "sample",
        "AZURE_STORAGE_FOLDER": "approved/",
        "AZURE_SEARCH_GRAPH_CACHE_CONNECTION_STRING": "ResourceId=/sample/cache;",
        "AZURE_OPENAI_ENDPOINT": "https://sample.openai.azure.com",
        "AZURE_OPENAI_CHAT_DEPLOYMENT": "chat",
        "AZURE_OPENAI_CHAT_MODEL": "gpt-5.4-mini",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "embedding",
        "AZURE_OPENAI_EMBEDDING_MODEL": "text-embedding-3-large",
    }.items():
        monkeypatch.setenv(name, value)
    return samples


def load_sample(samples, stem, is_async):
    name = stem + ("_async" if is_async else "")
    spec = importlib.util.spec_from_file_location(name, samples / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_sample(sample, is_async):
    if is_async:
        asyncio.run(sample.main())
    else:
        sample.main()


class TestGraphSamples:
    @pytest.mark.parametrize("is_async", [False, True])
    @pytest.mark.parametrize("collision", [1, 2])
    def test_graph_index_stops_before_upload_on_existing_index(
        self, monkeypatch, graph_sample_environment, is_async, collision
    ):
        require_capability("azure.search.documents.indexes.models.GraphProfile")
        import azure.search.documents as sync_search
        import azure.search.documents.aio as async_search
        import azure.search.documents.indexes as sync_indexes
        import azure.search.documents.indexes.aio as async_indexes

        sample = load_sample(graph_sample_environment, "sample_graph_index_preview", is_async)
        client = mock.MagicMock()
        client.__enter__.return_value = client
        client.__aenter__.return_value = client
        operation = mock.AsyncMock if is_async else mock.Mock
        submitted = []

        def create(index, *, match_condition):
            submitted.append((index, match_condition))
            if len(submitted) == collision:
                raise ResourceExistsError("Existing index must not be overwritten")

        client.create_or_update_index = operation(side_effect=create)
        monkeypatch.setattr(
            async_indexes if is_async else sync_indexes,
            "SearchIndexClient",
            mock.Mock(return_value=client),
        )
        search_factory = mock.Mock(side_effect=AssertionError("Must not upload after an index collision"))
        monkeypatch.setattr(async_search if is_async else sync_search, "SearchClient", search_factory)
        with pytest.raises(ResourceExistsError):
            run_sample(sample, is_async)
        assert len(submitted) == collision
        assert all(condition == MatchConditions.IfMissing for _, condition in submitted)
        client.delete_index.assert_not_called()
        search_factory.assert_not_called()

    @pytest.mark.parametrize("is_async", [False, True])
    def test_graph_extraction_stops_on_existing_source(self, monkeypatch, graph_sample_environment, is_async):
        require_capability("azure.search.documents.knowledgebases.models.KnowledgeSourceIngestionParameters.cache")
        import azure.search.documents.indexes as sync_indexes
        import azure.search.documents.indexes.aio as async_indexes

        sample = load_sample(graph_sample_environment, "sample_graph_extraction_cache_preview", is_async)
        client = mock.MagicMock()
        client.__enter__.return_value = client
        client.__aenter__.return_value = client
        operation = mock.AsyncMock if is_async else mock.Mock
        client.create_or_update_knowledge_source = operation(
            side_effect=ResourceExistsError("Existing source must not be overwritten")
        )
        indexer = mock.MagicMock()
        indexer.__enter__.return_value = indexer
        indexer.__aenter__.return_value = indexer
        indexes_module = async_indexes if is_async else sync_indexes
        monkeypatch.setattr(indexes_module, "SearchIndexClient", mock.Mock(return_value=client))
        monkeypatch.setattr(indexes_module, "SearchIndexerClient", mock.Mock(return_value=indexer))
        with pytest.raises(ResourceExistsError):
            run_sample(sample, is_async)
        assert client.create_or_update_knowledge_source.call_count == 1
        assert client.create_or_update_knowledge_source.call_args.kwargs["match_condition"] == MatchConditions.IfMissing
        client.get_knowledge_source.assert_not_called()
        indexer.get_indexer.assert_not_called()
        client.delete_knowledge_source.assert_not_called()
        client.delete_index.assert_not_called()
        client.create_or_update_knowledge_base.assert_not_called()

    @pytest.mark.parametrize("is_async", [False, True])
    @pytest.mark.usefixtures("graph_sample_environment")
    def test_graph_synchronization_waits_for_new_completed_generation(self, monkeypatch, is_async):
        import sample_utils

        old = "2026-11-12T00:00:00Z"
        new = "2026-11-12T00:01:00Z"
        states = [
            {"lastSynchronizationState": {"endTime": old, "itemsUpdatesFailed": 0}},
            {
                "lastSynchronizationState": {"endTime": old, "itemsUpdatesFailed": 0},
                "currentSynchronizationState": {"startTime": old},
            },
            {"lastSynchronizationState": {"endTime": new, "itemsUpdatesFailed": 0}},
        ]
        operation = mock.AsyncMock if is_async else mock.Mock
        indexes = mock.Mock()
        indexes.get_knowledge_source_status = operation(
            side_effect=[mock.Mock(as_dict=mock.Mock(return_value=state)) for state in states]
        )
        indexers = mock.Mock()
        indexers.get_indexer_status = operation(
            return_value=SimpleNamespace(
                last_result=SimpleNamespace(status="success", failed_item_count=0, warnings=[])
            )
        )
        if is_async:
            monkeypatch.setattr(asyncio, "sleep", mock.AsyncMock())
            completed = asyncio.run(
                sample_utils.wait_for_graph_synchronization_async(indexes, indexers, "source", "indexer", old)
            )
        else:
            import time

            monkeypatch.setattr(time, "sleep", mock.Mock())
            completed = sample_utils.wait_for_graph_synchronization(indexes, indexers, "source", "indexer", old)
        assert completed["endTime"] == new
        assert indexes.get_knowledge_source_status.call_count == 3

    @pytest.mark.usefixtures("graph_sample_environment")
    def test_graph_synchronization_rejects_failed_source_documents(self):
        import sample_utils

        status = mock.Mock()
        status.as_dict.return_value = {
            "lastSynchronizationState": {
                "endTime": "2026-11-12T00:01:00Z",
                "itemsUpdatesFailed": 1,
            }
        }
        with pytest.raises(RuntimeError, match="failed source documents"):
            sample_utils.completed_graph_synchronization(status)

    @pytest.mark.parametrize("is_async", [False, True])
    @pytest.mark.parametrize("running_after_conflict", [False, True])
    @pytest.mark.usefixtures("graph_sample_environment")
    def test_graph_indexer_only_accepts_conflict_when_execution_is_running(self, is_async, running_after_conflict):
        import sample_utils

        operation = mock.AsyncMock if is_async else mock.Mock
        indexers = mock.Mock()
        indexers.get_indexer_status = operation(
            side_effect=[
                SimpleNamespace(last_result=SimpleNamespace(status="success")),
                SimpleNamespace(
                    last_result=SimpleNamespace(status="inProgress" if running_after_conflict else "success")
                ),
            ]
        )
        error = HttpResponseError(message="Conflict")
        error.status_code = 409
        indexers.run_indexer = operation(side_effect=error)

        def run():
            if is_async:
                asyncio.run(sample_utils.run_graph_indexer_async(indexers, "indexer"))
            else:
                sample_utils.run_graph_indexer(indexers, "indexer")

        if running_after_conflict:
            run()
        else:
            with pytest.raises(HttpResponseError):
                run()
        indexers.run_indexer.assert_called_once_with("indexer")
