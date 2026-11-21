# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Recorded execution of preview samples using isolated resources."""

import importlib.util
import json
import os
from pathlib import Path
import re
import sys
from types import ModuleType, SimpleNamespace
from unittest import mock

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import ResourceNotFoundError
from azure.core.credentials import AzureKeyCredential
from devtools_testutils import get_credential, remove_batch_sanitizers
from devtools_testutils.helpers import get_recording_id
from devtools_testutils.sanitizers import add_body_key_sanitizer, add_general_regex_sanitizer

from _capabilities import require_capability
from search_service_preparer import (
    FAKE_AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    FAKE_AZURE_OPENAI_EMBEDDING_MODEL,
)


def load_preview_sample(test, monkeypatch, scenario, endpoint, variables, *, is_async=False):
    index_owner = "azure.search.documents.indexes" + (".aio" if is_async else "") + ".SearchIndexClient"
    capabilities = {
        "agentic_search": "azure.search.documents.models.AgenticSearchDebugInfo",
        "microsoft_retriever": "azure.search.documents.indexes.models.KnowledgeBaseMicrosoftRetriever1Model",
        "file_lro": index_owner + ".begin_ingest_knowledge_source_file_multipart",
        "compatible_chat": "azure.search.documents.indexes.models.KnowledgeBaseOpenAICompatibleModel",
        "gpt6": "azure.search.documents.indexes.models.AzureOpenAIModelName.GPT6_SOL",
        "automatic_hints": (
            "azure.search.documents.indexes.models.SearchIndexKnowledgeSourceFilterHint." "auto_configuration"
        ),
        "topic_graph": "azure.search.documents.indexes.models.VectorSearchTopicGraphProfile",
        "graph_index": "azure.search.documents.indexes.models.GraphProfile",
        "graph_extraction": "azure.search.documents.knowledgebases.models.KnowledgeSourceIngestionParameters.cache",
        "graph_hydration": "azure.search.documents.knowledgebases.models.AgentRuntimeGraphHydrateDocumentsParams",
    }
    require_capability(capabilities[scenario])
    if scenario == "agentic_search":
        require_capability(
            "azure.search.documents" + (".aio" if is_async else "") + ".SearchClient.search.agentic_options",
            "azure.search.documents.models.AgenticSearchOptions.max_runtime_in_seconds",
        )
    if scenario == "file_lro":
        require_capability(index_owner + ".begin_ingest_knowledge_source_file_replacement")
    if scenario.startswith("graph_"):
        require_capability("azure.search.documents" + (".aio" if is_async else "") + ".SearchClient.graph")
    if scenario == "graph_hydration":
        require_capability("azure.search.documents.knowledgebases.models.KnowledgeSourceIngestionParameters.cache")
    samples = Path(__file__).resolve().parents[1] / "samples"
    monkeypatch.syspath_prepend(str(samples))
    variables = variables if not test.is_live else {"run_tag": test.get_resource_name("gap")}
    assert variables and variables.get("run_tag"), "A matching sample recording is required."
    monkeypatch.setenv("SAMPLE_RUN_TAG", variables["run_tag"])
    monkeypatch.setenv("AZURE_SEARCH_SERVICE_ENDPOINT", endpoint)
    if not test.is_live:
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "fake-search-key")
    model_live = test.is_live and scenario not in {"agentic_search", "microsoft_retriever", "graph_index"}
    openai_endpoint = (
        os.environ["AZURE_OPENAI_ENDPOINT"] if model_live else "https://fake-openai.openai.azure.com/"
    ).rstrip("/")
    provider_key = os.environ.get("AZURE_OPENAI_API_KEY") if model_live else "fake-provider-key"
    for name, fake in {
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": FAKE_AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        "AZURE_OPENAI_EMBEDDING_MODEL": FAKE_AZURE_OPENAI_EMBEDDING_MODEL,
    }.items():
        if test.is_live:
            variables[name] = os.environ.get(name, "text-embedding-3-large")
        monkeypatch.setenv(name, variables[name] if test.is_live else fake)
    if not test.is_live and scenario == "topic_graph":
        dimensions = len(json.loads(variables["topic_embeddings"])[0][1])
        monkeypatch.setenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", str(dimensions))
    for name, value in {
        "AZURE_OPENAI_ENDPOINT": openai_endpoint,
        "AZURE_OPENAI_API_KEY": provider_key,
        "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-5-mini",
        "AZURE_OPENAI_CHAT_MODEL": "gpt-5-mini",
        "AZURE_OPENAI_GPT6_DEPLOYMENT": "gpt-6-sol",
        "AZURE_OPENAI_GPT6_MODEL": "gpt-6-sol",
        "AZURE_SEARCH_GPT6_NATIVE": str(scenario == "gpt6").lower(),
        "AZURE_SEARCH_HINT_REFRESH": "true",
        "AZURE_SEARCH_FILE_COMPATIBLE_EMBEDDINGS": "false",
        "AZURE_SEARCH_COMPATIBLE_CHAT_URI": (
            openai_endpoint + "/openai/deployments/gpt-5-mini/chat/completions?api-version=2025-04-01-preview"
        ),
        "AZURE_SEARCH_COMPATIBLE_CHAT_MODEL": "gpt-5-mini",
        "AZURE_SEARCH_COMPATIBLE_CHAT_HEADERS_JSON": json.dumps({"api-key": provider_key}) if provider_key else None,
        "AZURE_SEARCH_GRAPH_HYDRATE": str(scenario == "graph_hydration").lower(),
    }.items():
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)
    for name in (
        "AZURE_SEARCH_INDEX_NAME",
        "AZURE_SEARCH_TOPIC_GRAPH_INDEX_NAME",
        "AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME",
        "AZURE_SEARCH_KNOWLEDGE_BASE_NAME",
        "AZURE_SEARCH_GRAPH_INDEX_NAME",
        "AZURE_SEARCH_GRAPH_SOURCE_INDEX_NAME",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("AZURE_SEARCH_COMPATIBLE_CHAT_MI_AUDIENCE", raising=False)
    add_body_key_sanitizer(json_path="$..headers['api-key']", value="fake-provider-key", function_scoped=True)
    add_body_key_sanitizer(json_path="$..apiKey", value="fake-provider-key", function_scoped=True)
    remove_batch_sanitizers(["AZSDK3430"], headers={"x-recording-id": get_recording_id()})
    if scenario.startswith("graph_") and scenario != "graph_index":
        configure_graph_storage(test, monkeypatch, variables)
    stem = {
        "agentic_search": "agentic_search",
        "microsoft_retriever": "microsoft_retriever",
        "file_lro": "knowledge_source_file",
        "compatible_chat": "openai_compatible_retrieval",
        "gpt6": "openai_compatible_retrieval",
        "automatic_hints": "query_hints_auto_configuration",
        "topic_graph": "topic_graph",
        "graph_index": "graph_index",
        "graph_extraction": "graph_extraction_cache",
        "graph_hydration": "graph_extraction_cache",
    }[scenario]
    name = "sample_" + stem + "_preview" + ("_async" if is_async else "")
    spec = importlib.util.spec_from_file_location(name, samples / (name + ".py"))
    sample = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sample)
    if hasattr(sample, "uuid"):
        monkeypatch.setattr(sample, "uuid", SimpleNamespace(uuid4=lambda: SimpleNamespace(hex="abcdef")))
    if not test.is_live and scenario == "automatic_hints":
        if is_async:
            monkeypatch.setattr(sample, "asyncio", SimpleNamespace(sleep=mock.AsyncMock()))
        else:
            monkeypatch.setattr(sample, "time", SimpleNamespace(sleep=mock.Mock()))
    return sample, variables


def configure_graph_storage(test, monkeypatch, variables):
    fake_connection = (
        "DefaultEndpointsProtocol=https;AccountName=fakestoragecs;AccountKey=FAKE;EndpointSuffix=core.windows.net"
    )
    if test.is_live:
        variables["blob_folder"] = os.environ["AZURE_STORAGE_FOLDER"]
    monkeypatch.setenv("AZURE_STORAGE_FOLDER", variables["blob_folder"])
    for name in ("AZURE_STORAGE_CONNECTION_STRING", "AZURE_SEARCH_GRAPH_CACHE_CONNECTION_STRING"):
        if test.is_live:
            add_general_regex_sanitizer(value=fake_connection, regex=re.escape(os.environ[name]), function_scoped=True)
        else:
            monkeypatch.setenv(name, fake_connection)
    if test.is_live:
        add_general_regex_sanitizer(
            value="fakestoragecontainer",
            regex=re.escape(os.environ["AZURE_STORAGE_CONTAINER"]),
            function_scoped=True,
        )
    else:
        monkeypatch.setenv("AZURE_STORAGE_CONTAINER", "fakestoragecontainer")


def record_topic_embeddings(test, monkeypatch, variables, *, is_async=False):
    """Keep actual provider vectors for playback without contacting the provider again."""
    client_name = "AsyncAzureOpenAI" if is_async else "AzureOpenAI"
    if not test.is_live:

        def playback_client(*_args, **_kwargs):
            data = [
                SimpleNamespace(index=index, embedding=vector)
                for index, vector in json.loads(variables["topic_embeddings"])
            ]
            client = mock.MagicMock()
            client.__enter__.return_value = client
            client.__aenter__.return_value = client
            operation = mock.AsyncMock if is_async else mock.Mock
            client.embeddings.create = operation(return_value=SimpleNamespace(data=data))
            return client

        provider = ModuleType("openai")
        setattr(provider, client_name, playback_client)
        monkeypatch.setitem(sys.modules, "openai", provider)
        return

    openai = pytest.importorskip("openai", reason="Live Topic Graph samples require the optional OpenAI SDK.")
    original = getattr(openai, client_name, None)
    if original is None:
        pytest.skip(f"Live Topic Graph samples require openai.{client_name}.")

    def factory(*args, **kwargs):
        client = original(*args, **kwargs)
        create = client.embeddings.create
        if is_async:

            async def capture(*, input, model, **kwargs):
                result = await create(input=input, model=model, **kwargs)
                variables["topic_embeddings"] = json.dumps([(item.index, item.embedding) for item in result.data])
                return result

        else:

            def capture(*, input, model, **kwargs):
                result = create(input=input, model=model, **kwargs)
                variables["topic_embeddings"] = json.dumps([(item.index, item.embedding) for item in result.data])
                return result

        monkeypatch.setattr(client.embeddings, "create", capture)
        return client

    monkeypatch.setattr(openai, client_name, factory)


def track_sample_creations(monkeypatch, *, is_async=False):
    """Observe successful create-only writes; never replace service responses."""
    import azure.search.documents.indexes as sync_indexes
    import azure.search.documents.indexes.aio as async_indexes

    module = async_indexes if is_async else sync_indexes
    original = module.SearchIndexClient
    created = []

    def wrap(operation, kind):
        if is_async:

            async def observe(resource, *args, **kwargs):
                result = await operation(resource, *args, **kwargs)
                if kwargs.get("match_condition") == MatchConditions.IfMissing:
                    created.append((kind, resource.name))
                return result

        else:

            def observe(resource, *args, **kwargs):
                result = operation(resource, *args, **kwargs)
                if kwargs.get("match_condition") == MatchConditions.IfMissing:
                    created.append((kind, resource.name))
                return result

        return observe

    def factory(*args, **kwargs):
        client = original(*args, **kwargs)
        for kind in ("index", "knowledge_source", "knowledge_base"):
            name = "create_or_update_" + kind
            monkeypatch.setattr(client, name, wrap(getattr(client, name), kind))
        return client

    monkeypatch.setattr(module, "SearchIndexClient", factory)
    return created


def generated_graph_resources(source):
    resources = (source.as_dict().get("azureBlobParameters") or {}).get("createdResources") or {}
    mapping = (
        ("indexer", "indexer"),
        ("skillset", "skillset"),
        ("datasource", "data_source_connection"),
        ("graphIndex", "index"),
        ("index", "index"),
    )
    result = []
    for key, kind in mapping:
        if key in resources:
            assert resources[key].startswith(source.name + "-"), "Generated resource is not owned by this source."
            result.append((kind, resources[key]))
    return result


def cleanup_retained_sample(endpoint, created):
    from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
    from sample_utils import cleanup_preview_resources

    key = os.environ.get("AZURE_SEARCH_API_KEY")
    credential = AzureKeyCredential(key) if key else get_credential()
    with SearchIndexClient(endpoint, credential) as indexes, SearchIndexerClient(endpoint, credential) as indexers:
        generated = []
        for kind, name in created:
            if kind == "knowledge_source":
                generated.extend(generated_graph_resources(indexes.get_knowledge_source(name)))
        # Delete a corpus before its Topic Graph sidecar.
        ordered = sorted(created, key=lambda item: item[0] == "index" and item[1].endswith("-topicgraph"), reverse=True)
        cleanup_preview_resources(indexes, ordered)
        for kind, name in generated:
            client = indexes if kind == "index" else indexers
            try:
                resource = getattr(client, "get_" + kind)(name)
            except ResourceNotFoundError:
                continue
            assert resource.e_tag, "An ETag is required before cleaning a generated resource."
            getattr(client, "delete_" + kind)(resource, match_condition=MatchConditions.IfNotModified)


async def cleanup_retained_sample_async(endpoint, created):
    from azure.search.documents.indexes.aio import SearchIndexClient, SearchIndexerClient
    from sample_utils import cleanup_preview_resources_async

    key = os.environ.get("AZURE_SEARCH_API_KEY")
    credential = AzureKeyCredential(key) if key else get_credential(is_async=True)
    async with SearchIndexClient(endpoint, credential) as indexes, SearchIndexerClient(
        endpoint, credential
    ) as indexers:
        generated = []
        for kind, name in created:
            if kind == "knowledge_source":
                generated.extend(generated_graph_resources(await indexes.get_knowledge_source(name)))
        ordered = sorted(created, key=lambda item: item[0] == "index" and item[1].endswith("-topicgraph"), reverse=True)
        await cleanup_preview_resources_async(indexes, ordered)
        for kind, name in generated:
            client = indexes if kind == "index" else indexers
            try:
                resource = await getattr(client, "get_" + kind)(name)
            except ResourceNotFoundError:
                continue
            assert resource.e_tag, "An ETag is required before cleaning a generated resource."
            await getattr(client, "delete_" + kind)(resource, match_condition=MatchConditions.IfNotModified)
