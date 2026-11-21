# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Ownership and observable-result checks for the new preview feature samples."""

import asyncio
import importlib.util
import inspect
import json
import os
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest import mock

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import ResourceExistsError

from _capabilities import require_capability


@pytest.fixture(name="feature_samples")
def _feature_samples(monkeypatch):
    samples = Path(__file__).resolve().parents[1] / "samples"
    monkeypatch.syspath_prepend(str(samples))
    monkeypatch.setenv("AZURE_SEARCH_SERVICE_ENDPOINT", "https://sample.search.windows.net")
    monkeypatch.setenv("AZURE_SEARCH_API_KEY", "fake-search-key")
    return samples


@pytest.mark.usefixtures("feature_samples")
class TestPreviewFeatureSamples:
    @pytest.mark.parametrize("is_async", [False, True])
    @pytest.mark.parametrize("scenario", ["agentic_search", "microsoft_retriever", "graph_index", "file_lro"])
    def test_load_preview_sample_preserves_keyless_live_configuration(self, monkeypatch, scenario, is_async):
        import _preview_sample_helpers as helpers

        monkeypatch.delenv("AZURE_SEARCH_API_KEY", raising=False)
        monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
        if scenario == "file_lro":
            monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fake-openai.openai.azure.com/")
        monkeypatch.setattr(helpers, "get_recording_id", lambda: "recording-id")
        monkeypatch.setattr(helpers, "remove_batch_sanitizers", mock.Mock())
        monkeypatch.setattr(helpers, "add_body_key_sanitizer", mock.Mock())
        sample, variables = helpers.load_preview_sample(
            SimpleNamespace(is_live=True, get_resource_name=lambda _prefix: "live-sample"),
            monkeypatch,
            scenario,
            "https://sample.search.windows.net",
            None,
            is_async=is_async,
        )

        assert callable(sample.main)
        assert variables["run_tag"] == "live-sample"
        assert "AZURE_SEARCH_API_KEY" not in os.environ
        if scenario == "file_lro":
            assert "AZURE_OPENAI_API_KEY" not in os.environ

    @pytest.mark.parametrize("is_async", [False, True])
    @pytest.mark.parametrize("use_key", [False, True])
    def test_cleanup_retained_sample_preserves_authentication_and_conditional_delete(
        self, monkeypatch, is_async, use_key
    ):
        import _preview_sample_helpers as helpers
        import azure.search.documents.indexes as sync_indexes
        import azure.search.documents.indexes.aio as async_indexes

        if not use_key:
            monkeypatch.delenv("AZURE_SEARCH_API_KEY", raising=False)
        identity = mock.Mock()
        credential_factory = mock.Mock(return_value=identity)
        monkeypatch.setattr(helpers, "get_credential", credential_factory)
        operation = mock.AsyncMock if is_async else mock.Mock
        client = mock.MagicMock()
        client.__enter__.return_value = client
        client.__aenter__.return_value = client
        owned = SimpleNamespace(e_tag="owned-etag")
        client.get_index = operation(return_value=owned)
        client.delete_index = operation()
        indexes_factory = mock.Mock(return_value=client)
        indexers_factory = mock.MagicMock()
        module = async_indexes if is_async else sync_indexes
        monkeypatch.setattr(module, "SearchIndexClient", indexes_factory)
        monkeypatch.setattr(module, "SearchIndexerClient", indexers_factory)

        if is_async:
            asyncio.run(
                helpers.cleanup_retained_sample_async("https://sample.search.windows.net", [("index", "owned")])
            )
        else:
            helpers.cleanup_retained_sample("https://sample.search.windows.net", [("index", "owned")])

        credential = indexes_factory.call_args.args[1]
        assert indexers_factory.call_args.args[1] is credential
        if use_key:
            assert credential.key == "fake-search-key"
            credential_factory.assert_not_called()
        else:
            assert credential is identity
            credential_factory.assert_called_once_with(**({"is_async": True} if is_async else {}))
        client.get_index.assert_called_once_with("owned")
        client.delete_index.assert_called_once_with(owned, match_condition=MatchConditions.IfNotModified)

    @pytest.mark.parametrize("is_async", [False, True])
    def test_file_sample_uses_and_closes_identity_without_search_key(self, feature_samples, monkeypatch, is_async):
        require_capability(
            "azure.search.documents.indexes.SearchIndexClient.begin_ingest_knowledge_source_file_multipart"
        )
        import azure.identity as sync_identity
        import azure.identity.aio as async_identity
        import azure.search.documents.indexes as sync_indexes
        import azure.search.documents.indexes.aio as async_indexes

        monkeypatch.delenv("AZURE_SEARCH_API_KEY", raising=False)
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fake-openai.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        monkeypatch.setenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        monkeypatch.setenv("AZURE_SEARCH_FILE_COMPATIBLE_EMBEDDINGS", "false")
        name = "sample_knowledge_source_file_preview" + ("_async" if is_async else "")
        spec = importlib.util.spec_from_file_location(name, feature_samples / (name + ".py"))
        sample = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sample)
        identity = mock.MagicMock()
        identity.__aenter__.return_value = identity
        identity_factory = mock.Mock(return_value=identity)
        monkeypatch.setattr(
            async_identity if is_async else sync_identity,
            "DefaultAzureCredential",
            identity_factory,
        )
        client = mock.MagicMock()
        client.__aenter__.return_value = client
        operation = mock.AsyncMock if is_async else mock.Mock
        client.create_or_update_knowledge_source = operation(side_effect=ResourceExistsError("existing source"))
        client.close = operation()
        indexes_factory = mock.Mock(return_value=client)
        monkeypatch.setattr(
            async_indexes if is_async else sync_indexes,
            "SearchIndexClient",
            indexes_factory,
        )

        with pytest.raises(ResourceExistsError):
            if is_async:
                asyncio.run(sample.main())
            else:
                sample.main()

        assert indexes_factory.call_args.args[1] is identity
        identity_factory.assert_called_once_with()
        if is_async:
            identity.__aexit__.assert_awaited_once()
        else:
            identity.close.assert_called_once_with()
        client.delete_knowledge_source.assert_not_called()

    @pytest.mark.parametrize("is_async", [False, True])
    def test_preview_sample_entrypoints_allow_unrecorded_live_execution(self, monkeypatch, is_async):
        import devtools_testutils.proxy_testcase as sync_recordings
        import devtools_testutils.aio.proxy_testcase_async as async_recordings

        recordings = async_recordings if is_async else sync_recordings
        monkeypatch.setattr(recordings, "is_live_and_not_recording", lambda: True)
        start_recording = mock.Mock(side_effect=AssertionError("Unrecorded execution must not start the proxy."))
        monkeypatch.setattr(recordings, "start_record_or_playback", start_recording)
        name = "test_preview_feature_samples_live" + ("_async" if is_async else "")
        module = importlib.import_module(name)
        tests = getattr(module, "TestPreviewFeatureSamples" + ("Async" if is_async else ""))
        operation = mock.AsyncMock if is_async else mock.Mock
        for name in vars(tests):
            if not name.startswith("test_"):
                continue
            expected = object()
            run_sample = operation(return_value=expected)
            entrypoint = inspect.unwrap(getattr(tests, name))
            result = entrypoint(
                SimpleNamespace(_run_sample=run_sample),
                endpoint="https://sample.search.windows.net",
            )
            if is_async:
                result = asyncio.run(result)
            assert result is expected
            assert run_sample.call_args.args[0] == "https://sample.search.windows.net"
            assert run_sample.call_args.args[2] is None
        start_recording.assert_not_called()

    @pytest.mark.parametrize("is_async", [False, True])
    @pytest.mark.parametrize("provider_state", ["missing", "namespace"])
    def test_record_topic_embeddings_skips_live_without_openai_sdk(self, monkeypatch, is_async, provider_state):
        from _preview_sample_helpers import record_topic_embeddings

        provider = None if provider_state == "missing" else ModuleType("openai")
        monkeypatch.setitem(sys.modules, "openai", provider)
        with pytest.raises(pytest.skip.Exception, match="Live Topic Graph samples require"):
            record_topic_embeddings(SimpleNamespace(is_live=True), monkeypatch, {}, is_async=is_async)

    @pytest.mark.parametrize("is_async", [False, True])
    def test_record_topic_embeddings_captures_live_vectors_and_restores_provider(self, monkeypatch, is_async):
        from _preview_sample_helpers import record_topic_embeddings

        provider = ModuleType("openai")
        client_name = "AsyncAzureOpenAI" if is_async else "AzureOpenAI"
        response = SimpleNamespace(data=[SimpleNamespace(index=0, embedding=[0.25, 0.75])])
        operation = mock.AsyncMock if is_async else mock.Mock
        client = SimpleNamespace(embeddings=SimpleNamespace(create=operation(return_value=response)))
        constructor = mock.Mock(return_value=client)
        setattr(provider, client_name, constructor)
        monkeypatch.setitem(sys.modules, "openai", provider)
        variables = {}
        with pytest.MonkeyPatch.context() as sample_patch:
            record_topic_embeddings(
                SimpleNamespace(is_live=True),
                sample_patch,
                variables,
                is_async=is_async,
            )
            wrapped = getattr(provider, client_name)()
            result = wrapped.embeddings.create(input=["hotel"], model="recorded-model")
            if is_async:
                result = asyncio.run(result)
            assert result is response
            assert json.loads(variables["topic_embeddings"]) == [[0, [0.25, 0.75]]]
        assert getattr(provider, client_name) is constructor

    @pytest.mark.parametrize("is_async", [False, True])
    @pytest.mark.parametrize("provider_state", ["missing", "namespace"])
    def test_record_topic_embeddings_replays_vectors_without_openai_sdk(self, monkeypatch, is_async, provider_state):
        from _preview_sample_helpers import record_topic_embeddings

        unavailable_provider = None if provider_state == "missing" else ModuleType("openai")
        monkeypatch.setitem(sys.modules, "openai", unavailable_provider)
        recorded = [[0, [0.25, 0.75]], [1, [0.5, 0.5]]]
        with pytest.MonkeyPatch.context() as sample_patch:
            record_topic_embeddings(
                SimpleNamespace(is_live=False),
                sample_patch,
                {"topic_embeddings": json.dumps(recorded)},
                is_async=is_async,
            )
            provider = importlib.import_module("openai")
            client_type = getattr(provider, "AsyncAzureOpenAI" if is_async else "AzureOpenAI")
            if is_async:

                async def read_embeddings():
                    async with client_type() as client:
                        return await client.embeddings.create(input=["hotel", "topic"], model="recorded-model")

                response = asyncio.run(read_embeddings())
            else:
                with client_type() as client:
                    response = client.embeddings.create(input=["hotel", "topic"], model="recorded-model")

            assert [(item.index, item.embedding) for item in response.data] == [
                (index, vector) for index, vector in recorded
            ]
        assert sys.modules["openai"] is unavailable_provider

    @pytest.mark.parametrize("scenario", ["file_lro", "topic_graph"])
    def test_sample_playback_preserves_sanitized_models_and_recorded_vector_dimensions(self, monkeypatch, scenario):
        import _preview_sample_helpers as helpers
        from search_service_preparer import (
            FAKE_AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            FAKE_AZURE_OPENAI_EMBEDDING_MODEL,
        )

        variables = {
            "run_tag": "recorded-sample",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "live-only-deployment",
            "AZURE_OPENAI_EMBEDDING_MODEL": "text-embedding-3-large",
            "topic_embeddings": json.dumps([[0, [0.1, 0.2, 0.3]]]),
        }
        monkeypatch.setenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "unrelated-local-deployment")
        monkeypatch.setenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
        monkeypatch.delenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", raising=False)
        monkeypatch.setattr(helpers, "get_recording_id", lambda: "recording-id")
        monkeypatch.setattr(helpers, "remove_batch_sanitizers", mock.Mock())
        monkeypatch.setattr(helpers, "add_body_key_sanitizer", mock.Mock())
        helpers.load_preview_sample(
            SimpleNamespace(is_live=False), monkeypatch, scenario, "https://sample.search.windows.net", variables
        )

        assert os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"] == FAKE_AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        assert os.environ["AZURE_OPENAI_EMBEDDING_MODEL"] == FAKE_AZURE_OPENAI_EMBEDDING_MODEL
        if scenario == "topic_graph":
            assert os.environ["AZURE_OPENAI_EMBEDDING_DIMENSIONS"] == "3"

    @pytest.mark.parametrize("is_async", [False, True])
    @pytest.mark.parametrize("kind", ["agentic_search", "microsoft_retriever", "knowledge_source_file"])
    def test_new_sample_collisions_never_delete_existing_resources(self, feature_samples, monkeypatch, is_async, kind):
        require_capability("azure.search.documents.models.AgenticSearchDebugInfo")
        import azure.search.documents.indexes as sync_indexes
        import azure.search.documents.indexes.aio as async_indexes

        for name, value in {
            "AZURE_OPENAI_ENDPOINT": "https://fake-openai.openai.azure.com",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "text-embedding-3-large",
            "AZURE_OPENAI_EMBEDDING_MODEL": "text-embedding-3-large",
            "AZURE_SEARCH_FILE_COMPATIBLE_EMBEDDINGS": "false",
        }.items():
            monkeypatch.setenv(name, value)
        name = "sample_" + kind + "_preview" + ("_async" if is_async else "")
        spec = importlib.util.spec_from_file_location(name, feature_samples / (name + ".py"))
        sample = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sample)
        operation = mock.AsyncMock if is_async else mock.Mock
        client = mock.MagicMock()
        client.__enter__.return_value = client
        client.__aenter__.return_value = client
        client.close = operation()
        client.create_or_update_index = operation(side_effect=ResourceExistsError("existing index"))
        client.create_or_update_knowledge_source = operation(side_effect=ResourceExistsError("existing source"))
        monkeypatch.setattr(
            async_indexes if is_async else sync_indexes, "SearchIndexClient", mock.Mock(return_value=client)
        )
        with pytest.raises(ResourceExistsError):
            if is_async:
                asyncio.run(sample.main())
            else:
                sample.main()
        client.delete_index.assert_not_called()
        client.delete_knowledge_source.assert_not_called()
        client.delete_knowledge_base.assert_not_called()

    @pytest.mark.parametrize("is_async", [False, True])
    def test_random_scoring_collisions_never_delete_existing_resources(self, feature_samples, monkeypatch, is_async):
        require_capability("azure.search.documents.indexes.models.RandomScoringFunction")
        import azure.search.documents.indexes as sync_indexes
        import azure.search.documents.indexes.aio as async_indexes

        name = "sample_random_scoring_preview" + ("_async" if is_async else "")
        spec = importlib.util.spec_from_file_location(name, feature_samples / (name + ".py"))
        sample = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sample)
        operation = mock.AsyncMock if is_async else mock.Mock
        client = mock.MagicMock()
        client.__enter__.return_value = client
        client.__aenter__.return_value = client
        client.create_or_update_index = operation(side_effect=ResourceExistsError("existing index"))
        client.delete_index = operation()
        client.delete_knowledge_source = operation()
        monkeypatch.setattr(
            async_indexes if is_async else sync_indexes, "SearchIndexClient", mock.Mock(return_value=client)
        )
        with pytest.raises(ResourceExistsError):
            if is_async:
                asyncio.run(sample.main())
            else:
                sample.main()
        client.delete_index.assert_not_called()
        client.delete_knowledge_source.assert_not_called()

    @pytest.mark.parametrize("is_async", [False, True])
    def test_random_scoring_upload_failure_deletes_only_owned_index(self, feature_samples, monkeypatch, is_async):
        require_capability("azure.search.documents.indexes.models.RandomScoringFunction")
        import azure.search.documents as sync_search
        import azure.search.documents.aio as async_search
        import azure.search.documents.indexes as sync_indexes
        import azure.search.documents.indexes.aio as async_indexes

        name = "sample_random_scoring_preview" + ("_async" if is_async else "")
        spec = importlib.util.spec_from_file_location(name, feature_samples / (name + ".py"))
        sample = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sample)
        operation = mock.AsyncMock if is_async else mock.Mock
        client = mock.MagicMock()
        client.__enter__.return_value = client
        client.__aenter__.return_value = client
        profile = SimpleNamespace(
            name="randomUnseeded", functions=[SimpleNamespace(as_dict=lambda: {"type": "random", "magnitude": None})]
        )
        owned = SimpleNamespace(e_tag="etag", scoring_profiles=[profile])
        client.create_or_update_index = operation()
        client.get_index = operation(return_value=owned)
        client.delete_index = operation()
        search = mock.MagicMock()
        search.__enter__.return_value = search
        search.__aenter__.return_value = search
        search.upload_documents = operation(return_value=[SimpleNamespace(succeeded=False)])
        monkeypatch.setattr(
            async_indexes if is_async else sync_indexes, "SearchIndexClient", mock.Mock(return_value=client)
        )
        monkeypatch.setattr(async_search if is_async else sync_search, "SearchClient", mock.Mock(return_value=search))
        with pytest.raises(RuntimeError, match="could not be uploaded"):
            if is_async:
                asyncio.run(sample.main())
            else:
                sample.main()
        client.delete_index.assert_called_once_with(owned, match_condition=MatchConditions.IfNotModified)

    @pytest.mark.parametrize("is_async", [False, True])
    @pytest.mark.parametrize("collision", ["source", "base"])
    def test_kb_tools_collision_cleans_only_successfully_created_resources(
        self, feature_samples, monkeypatch, is_async, collision
    ):
        require_capability("azure.search.documents.indexes.models.KnowledgeBaseTool")
        import azure.search.documents.indexes as sync_indexes
        import azure.search.documents.indexes.aio as async_indexes

        name = "sample_knowledge_base_tools_preview" + ("_async" if is_async else "")
        spec = importlib.util.spec_from_file_location(name, feature_samples / (name + ".py"))
        sample = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sample)
        operation = mock.AsyncMock if is_async else mock.Mock
        client = mock.MagicMock()
        client.__enter__.return_value = client
        client.__aenter__.return_value = client
        client.create_or_update_knowledge_source = operation(
            side_effect=ResourceExistsError("existing source") if collision == "source" else None
        )
        client.create_or_update_knowledge_base = operation(side_effect=ResourceExistsError("existing KB"))
        for kind in ("index", "knowledge_source", "knowledge_base"):
            setattr(client, "get_" + kind, operation(return_value=SimpleNamespace(e_tag="etag")))
            setattr(client, "delete_" + kind, operation())

        def prepare(_client, _endpoint, _credential, index_name, _documents, created):
            created.append(("index", index_name))

        monkeypatch.setattr(
            sample,
            "prepare_preview_hotel_index_async" if is_async else "prepare_preview_hotel_index",
            operation(side_effect=prepare),
        )
        monkeypatch.setattr(
            sample,
            "wait_for_knowledge_source_active_async" if is_async else "wait_for_knowledge_source_active",
            operation(),
        )
        monkeypatch.setattr(
            async_indexes if is_async else sync_indexes, "SearchIndexClient", mock.Mock(return_value=client)
        )
        with pytest.raises(ResourceExistsError):
            if is_async:
                asyncio.run(sample.main())
            else:
                sample.main()
        client.delete_knowledge_base.assert_not_called()
        assert client.delete_index.call_count == (1 if collision == "source" else 2)
        assert client.delete_knowledge_source.call_count == (0 if collision == "source" else 2)
        for call in client.delete_index.call_args_list + client.delete_knowledge_source.call_args_list:
            assert call.kwargs["match_condition"] == MatchConditions.IfNotModified

    @pytest.mark.parametrize(
        "headers,audience",
        [
            (None, None),
            ('{"api-key":"fake-key"}', "00000000-0000-0000-0000-000000000001"),
            ("{}", None),
            ('{"api-key":""}', None),
            ('{"api-key":42}', None),
            (None, "https://cognitiveservices.azure.com"),
            (None, "api://00000000-0000-0000-0000-000000000001"),
        ],
    )
    def test_provider_auth_rejects_ambiguous_or_invalid_configuration(self, monkeypatch, headers, audience):
        from sample_utils import compatible_provider_auth

        prefix = "SAMPLE_PROVIDER"
        for suffix, value in (("_HEADERS_JSON", headers), ("_MI_AUDIENCE", audience)):
            if value is None:
                monkeypatch.delenv(prefix + suffix, raising=False)
            else:
                monkeypatch.setenv(prefix + suffix, value)
        with pytest.raises(ValueError):
            compatible_provider_auth(prefix)

    @pytest.mark.parametrize("missing", ["references", "activity", "filter", "scope", "error"])
    def test_auto_hints_require_references_and_observable_filter_without_errors(self, missing):
        require_capability("azure.search.documents.knowledgebases.models.KnowledgeBaseSearchIndexActivityRecord")
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseErrorDetail,
            KnowledgeBaseQueryHintProcessing,
            KnowledgeBaseSearchIndexActivityRecord,
            KnowledgeBaseSearchIndexReference,
        )
        from sample_utils import validate_preview_auto_hint

        activity = KnowledgeBaseSearchIndexActivityRecord(
            id=1,
            knowledge_source_name="source",
            query_hint_processing=KnowledgeBaseQueryHintProcessing(generated_filter="country eq 'Canada'"),
        )
        result = SimpleNamespace(
            references=[KnowledgeBaseSearchIndexReference(id="ref", activity_source=1, doc_key="hotel-ca-1")],
            activity=[activity],
        )
        if missing == "references":
            result.references = []
        elif missing == "activity":
            result.activity = []
        elif missing == "filter":
            activity.query_hint_processing = None
        elif missing == "scope":
            activity.knowledge_source_name = "other-source"
        else:
            activity.error = KnowledgeBaseErrorDetail(code="failed", message="query failed")
        with pytest.raises(RuntimeError):
            validate_preview_auto_hint(result, "Canada", "source", {"hotel-ca-1"})

    def test_auto_hints_accept_actual_filter_and_matching_references(self):
        require_capability("azure.search.documents.knowledgebases.models.KnowledgeBaseSearchIndexActivityRecord")
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseQueryHintProcessing,
            KnowledgeBaseSearchIndexActivityRecord,
            KnowledgeBaseSearchIndexReference,
        )
        from sample_utils import validate_preview_auto_hint

        result = SimpleNamespace(
            references=[KnowledgeBaseSearchIndexReference(id="ref", activity_source=1, doc_key="hotel-ca-1")],
            activity=[
                KnowledgeBaseSearchIndexActivityRecord(
                    id=1,
                    knowledge_source_name="source",
                    query_hint_processing=KnowledgeBaseQueryHintProcessing(generated_filter="country eq 'Canada'"),
                )
            ],
        )
        validate_preview_auto_hint(result, "Canada", "source", {"hotel-ca-1"})
