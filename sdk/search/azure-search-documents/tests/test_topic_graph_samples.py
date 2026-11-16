# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""Safety checks for the Topic Graph setup samples."""

import asyncio
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from unittest import mock

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError

from _capabilities import require_capability


@pytest.fixture(name="sample_environment")
def _sample_environment(monkeypatch):
    samples_dir = Path(__file__).resolve().parents[1] / "samples"
    monkeypatch.syspath_prepend(str(samples_dir))
    for name, value in {
        "AZURE_SEARCH_SERVICE_ENDPOINT": "https://sample.search.windows.net",
        "AZURE_SEARCH_API_KEY": "fake-search-key",
        "AZURE_OPENAI_ENDPOINT": "https://sample.openai.azure.com",
        "AZURE_OPENAI_API_KEY": "fake-embedding-key",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "embeddings",
        "AZURE_OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "AZURE_SEARCH_INDEX_NAME": "new-corpus",
        "AZURE_SEARCH_TOPIC_GRAPH_INDEX_NAME": "new-topicgraph",
    }.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", raising=False)
    embedding_factory = mock.Mock(side_effect=AssertionError("Must stop before generating embeddings"))
    openai = ModuleType("openai")
    openai.AzureOpenAI = embedding_factory
    openai.AsyncAzureOpenAI = embedding_factory
    monkeypatch.setitem(sys.modules, "openai", openai)
    return samples_dir, embedding_factory


class TestTopicGraphSamples:
    @pytest.mark.parametrize("is_async", [False, True])
    @pytest.mark.parametrize("failure_point", ["corpus_exists", "sidecar_exists", "link_changed"])
    def test_main_stops_on_resource_collision_or_concurrent_link_update(
        self, monkeypatch, sample_environment, is_async, failure_point
    ):
        require_capability(
            "azure.search.documents.indexes.models.VectorSearch.topic_graph_profiles",
            "azure.search.documents.indexes.models.SearchField.topic_graph_profile",
            "azure.search.documents.indexes.models.VectorSearchTopicGraphProfile",
            "azure.search.documents.models.NoneVectorQueryTopicGraph",
            "azure.search.documents.models.BalancedVectorQueryTopicGraph",
            "azure.search.documents.models.DiverseVectorQueryTopicGraph",
        )
        import azure.search.documents.indexes as sync_indexes
        import azure.search.documents.indexes.aio as async_indexes

        samples_dir, embedding_factory = sample_environment
        filename = "sample_topic_graph_preview_async" if is_async else "sample_topic_graph_preview"
        spec = importlib.util.spec_from_file_location(filename, samples_dir / f"{filename}.py")
        sample = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sample)
        client = mock.MagicMock()
        client.__enter__.return_value = client
        client.__aenter__.return_value = client
        submitted = []
        indexes = {}

        def submit(index, *, match_condition):
            submitted.append((index.as_dict(), match_condition))
            if len(submitted) == 1 and failure_point == "corpus_exists":
                raise ResourceExistsError("Corpus already exists")
            if len(submitted) == 2 and failure_point == "sidecar_exists":
                raise ResourceExistsError("Sidecar already exists")
            if match_condition == MatchConditions.IfNotModified:
                raise ResourceModifiedError("Corpus changed after it was read")
            index.e_tag = '"original-etag"'
            indexes[index.name] = index

        operation_mock = mock.AsyncMock if is_async else mock.Mock
        client.create_or_update_index = operation_mock(side_effect=submit)
        client.get_index = operation_mock(side_effect=lambda name: indexes[name])
        factory = mock.Mock(return_value=client)
        monkeypatch.setattr(async_indexes if is_async else sync_indexes, "SearchIndexClient", factory)

        expected_error = ResourceModifiedError if failure_point == "link_changed" else ResourceExistsError
        with pytest.raises(expected_error):
            if is_async:
                asyncio.run(sample.main())
            else:
                sample.main()

        assert submitted[0][1] == MatchConditions.IfMissing
        if failure_point != "corpus_exists":
            assert submitted[1][1] == MatchConditions.IfMissing
        if failure_point == "link_changed":
            linked, condition = submitted[2]
            assert condition == MatchConditions.IfNotModified
            assert linked["@odata.etag"] == '"original-etag"'
            assert linked["vectorSearch"]["vectorizers"][0]["azureOpenAIParameters"]["deploymentId"] == "embeddings"
            assert linked["semantic"]["configurations"][0]["name"] == "hotels"
        client.delete_index.assert_not_called()
        client.create_or_update_knowledge_source.assert_not_called()
        client.create_or_update_knowledge_base.assert_not_called()
        embedding_factory.assert_not_called()
