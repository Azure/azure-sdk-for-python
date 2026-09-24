# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Offline regression tests for generated models and dictionary inputs."""

from copy import deepcopy
from importlib.metadata import version
from importlib.util import find_spec
import inspect
import json
import logging
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from azure.core import AsyncPipelineClient, PipelineClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
    ServiceRequestError,
)

import azure.data.ai
from azure.data.ai import AzureDataAIClient
from azure.data.ai.aio import AzureDataAIClient as AsyncAzureDataAIClient
from azure.data.ai.models import SemanticRerankingResult, SemanticRerankingScore, SentenceScore, TokenUsageResult


def test_public_api_exposes_generated_models_without_embeddings():
    assert azure.data.ai.__version__ == version("azure-data-ai")
    assert azure.data.ai.__all__ == ["AzureDataAIClient"]
    assert find_spec("azure.data.ai.models") is not None
    assert find_spec("azure.data.ai.types") is not None
    for client_type in (AzureDataAIClient, AsyncAzureDataAIClient):
        assert hasattr(client_type, "semantic_rerank")
        assert not hasattr(client_type, "generate_embeddings")
        assert hasattr(client_type, "send_request")
    assert not inspect.iscoroutinefunction(AzureDataAIClient.semantic_rerank)
    assert inspect.iscoroutinefunction(AsyncAzureDataAIClient.semantic_rerank)
    assert AzureDataAIClient.__module__ == "azure.data.ai._client"
    assert AsyncAzureDataAIClient.__module__ == "azure.data.ai.aio._client"


def test_contract_metadata_uses_azure_data_ai_namespace():
    package = Path(__file__).resolve().parents[1]
    metadata = json.loads((package / "_metadata.json").read_text(encoding="utf-8"))
    properties = json.loads((package / "apiview-properties.json").read_text(encoding="utf-8"))
    assert metadata["apiVersions"] == {"Azure.Data.AI": metadata["apiVersion"]}
    assert properties["CrossLanguagePackageId"] == "Azure.Data.AI"
    expected = {
        "azure.data.ai.AzureDataAIClient.semantic_rerank": "Azure.Data.AI.InferenceOperationGroup.semanticRerank",
        "azure.data.ai.aio.AzureDataAIClient.semantic_rerank": "Azure.Data.AI.InferenceOperationGroup.semanticRerank",
    }
    for name, definition in expected.items():
        assert properties["CrossLanguageDefinitionId"][name] == definition
    assert properties["CrossLanguageDefinitionId"]["azure.data.ai.models.SemanticRerankingMetaResult"] == (
        "Azure.Data.AI.MetaResult"
    )
    assert properties["CrossLanguageDefinitionId"]["azure.data.ai.models.SemanticRerankingDocumentType"] == (
        "Azure.Data.AI.DocumentType"
    )


@pytest.mark.asyncio
async def test_sentence_scores_follow_updated_contract_without_normalization(
    open_client, invoke, respond, request_payload
):
    payload = {
        "scores": [
            {
                "index": 0,
                "score": 0.9,
                "sentenceScores": [
                    {"index": 0, "score": 0.0},
                    {"index": 3, "score": 0.6},
                    {"index": 12, "score": 1.0},
                ],
            }
        ]
    }
    respond((200, payload, {}))
    async with open_client() as client:
        result = await invoke(client, request_payload)
    assert result == payload
    assert [sentence["index"] for sentence in result["scores"][0]["sentenceScores"]] == [0, 3, 12]


@pytest.mark.asyncio
async def test_dictionary_round_trip(open_client, invoke, respond, transport, request_payload, result_payload):
    original = deepcopy(request_payload)
    respond((200, result_payload, {}))
    async with open_client() as client:
        assert not hasattr(client, "inference")
        assert isinstance(client._client, (PipelineClient, AsyncPipelineClient))
        assert hasattr(client, "_serialize")
        result = await invoke(client, request_payload)

    sent = transport.send.call_args.args[0]
    assert sent.method == "POST"
    assert sent.url == (
        "https://example.inference.azure.com/inference/semanticReranking?api-version=2026-09-01-preview"
    )
    assert sent.headers["Content-Type"] == "application/json"
    assert sent.headers["Accept"] == "application/json"
    assert json.loads(sent.content) == original
    assert request_payload == original
    assert isinstance(result, SemanticRerankingResult)
    assert result == result_payload
    assert isinstance(result.scores[0], SemanticRerankingScore)
    assert isinstance(result.scores[0].sentence_scores[0], SentenceScore)
    assert isinstance(result.meta.token_usage, TokenUsageResult)
    assert result.as_dict() == result_payload


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [{"scores": []}, {}, {"scores": [], "futureMetadata": {"value": 0}}])
async def test_response_is_not_normalized(open_client, invoke, respond, request_payload, payload):
    respond((200, payload, {}))
    async with open_client() as client:
        result = await invoke(client, request_payload)
    assert isinstance(result, SemanticRerankingResult)
    assert result == payload


@pytest.mark.asyncio
async def test_json_documents(open_client, invoke, respond, transport, result_payload):
    payload = {
        "query": "caf\u00e9",
        "documents": [json.dumps({"description": "a caf\u00e9 in Paris"})],
        "documentType": "json",
        "targetPaths": "/description",
        "model": "test-model",
        "returnDocuments": False,
    }
    respond((200, result_payload, {}))
    async with open_client() as client:
        await invoke(client, payload)
    sent = transport.send.call_args.args[0].content
    assert json.loads(sent) == payload


@pytest.mark.asyncio
@pytest.mark.parametrize("model", ["semantic-reranker-v1", "future-model"])
async def test_all_reranking_options_are_forwarded(open_client, invoke, respond, transport, result_payload, model):
    payload = {
        "query": "capital of France",
        "documents": [
            json.dumps({"description": "Paris is the capital of France."}),
            json.dumps({"description": "Berlin is the capital of Germany."}),
        ],
        "model": model,
        "topK": 1,
        "batchSize": 2,
        "sort": False,
        "returnDocuments": False,
        "returnSentenceScore": False,
        "documentType": "json",
        "targetPaths": "description",
        "futureOption": {"enabled": True},
    }
    original = deepcopy(payload)
    respond((200, result_payload, {}))
    async with open_client() as client:
        result = await invoke(client, payload)
    assert json.loads(transport.send.call_args.args[0].content) == original
    assert payload == original
    assert result == result_payload


@pytest.mark.asyncio
async def test_omitted_options_are_not_added(open_client, invoke, respond, transport):
    payload = {"query": "capital of France", "documents": ["Paris"]}
    respond((200, {"scores": []}, {}))
    async with open_client() as client:
        await invoke(client, payload)
    assert json.loads(transport.send.call_args.args[0].content) == payload


@pytest.mark.asyncio
async def test_key_authentication(open_client, invoke, respond, transport, request_payload, result_payload):
    credential = AzureKeyCredential("first-test-key")
    respond((200, result_payload, {}), (200, result_payload, {}))
    async with open_client(credential) as client:
        await invoke(client, request_payload)
        first = transport.send.call_args.args[0]
        assert first.headers["Ocp-Apim-Subscription-Key"] == "first-test-key"
        assert "Authorization" not in first.headers
        credential.update("second-test-key")
        await invoke(client, request_payload)
        second = transport.send.call_args.args[0]
        assert second.headers["Ocp-Apim-Subscription-Key"] == "second-test-key"


@pytest.mark.asyncio
async def test_raw_keys_require_azure_key_credential(open_client, transport):
    with pytest.raises(TypeError, match="Unsupported credential"):
        async with open_client("raw-test-key"):
            pytest.fail("The generated client must require AzureKeyCredential for API keys.")
    transport.send.assert_not_called()


@pytest.mark.asyncio
async def test_key_is_redacted_from_http_logs(open_client, invoke, respond, request_payload, caplog):
    caplog.set_level(logging.INFO, logger="azure.core.pipeline.policies.http_logging_policy")
    respond((200, {"scores": []}, {}))
    async with open_client(AzureKeyCredential("wrapped-test-key"), logging_enable=True) as client:
        await invoke(client, request_payload)
    assert "Ocp-Apim-Subscription-Key" in caplog.text
    assert "raw-test-key" not in caplog.text
    assert "wrapped-test-key" not in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("scopes", [None, ["https://custom.example/.default"]])
async def test_token_authentication(
    open_client, invoke, respond, transport, token_credential, request_payload, result_payload, scopes
):
    respond((200, result_payload, {}))
    options = {} if scopes is None else {"credential_scopes": scopes}
    async with open_client(token_credential, **options) as client:
        await invoke(client, request_payload)
    token_credential.get_token.assert_called_once()
    assert token_credential.get_token.call_args.args == tuple(scopes or ["https://dbinference.azure.com/.default"])
    sent = transport.send.call_args.args[0]
    assert sent.headers["Authorization"] == "Bearer test-token"
    assert "Ocp-Apim-Subscription-Key" not in sent.headers


@pytest.mark.asyncio
@pytest.mark.parametrize("api_version", ["2026-09-01-preview", "test-api-version"])
async def test_diagnostic_hook_and_request_options(
    open_client, invoke, respond, transport, request_payload, result_payload, api_version
):
    captured = []
    respond((200, result_payload, {}))
    async with open_client(endpoint="https://example.inference.azure.com/", api_version=api_version) as client:
        await invoke(
            client,
            request_payload,
            raw_response_hook=captured.append,
            headers={"x-test-header": "value"},
            connection_timeout=5,
            read_timeout=10,
        )
    sent = transport.send.call_args.args[0]
    assert urlsplit(sent.url).path == "/inference/semanticReranking"
    assert parse_qs(urlsplit(sent.url).query) == {"api-version": [api_version]}
    assert sent.headers["x-test-header"] == "value"
    assert transport.send.call_args.kwargs["connection_timeout"] == 5
    assert transport.send.call_args.kwargs["read_timeout"] == 10
    assert len(captured) == 1
    assert captured[0].http_response.headers["X-Correlation-ID"] == "test-correlation-id"


@pytest.mark.asyncio
async def test_request_options_and_endpoint_path_are_preserved(
    open_client, invoke, respond, transport, request_payload
):
    headers = {"accept": "application/json", "x-test-header": "value"}
    params = {"api-version": "ignored-override", "custom": "value"}
    original_headers = dict(headers)
    original_params = dict(params)
    respond((200, {"scores": []}, {}))
    async with open_client(endpoint="https://example.inference.azure.com/prefix/") as client:
        await invoke(client, request_payload, headers=headers, params=params)
    sent = transport.send.call_args.args[0]
    assert urlsplit(sent.url).path == "/prefix/inference/semanticReranking"
    assert parse_qs(urlsplit(sent.url).query) == {
        "api-version": ["2026-09-01-preview"],
        "custom": ["value"],
    }
    assert sent.headers["Accept"] == "application/json"
    assert sent.headers["x-test-header"] == "value"
    assert headers == original_headers
    assert params == original_params


@pytest.mark.asyncio
async def test_custom_error_map_is_preserved(open_client, invoke, respond, request_payload):
    respond((400, {"title": "Custom error", "status": 400}, {}))
    error_map = {400: ResourceNotFoundError}
    async with open_client() as client:
        with pytest.raises(ResourceNotFoundError) as caught:
            await invoke(client, request_payload, error_map=error_map)
    assert caught.value.status_code == 400
    assert error_map == {400: ResourceNotFoundError}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,error_type",
    [
        (400, HttpResponseError),
        (401, ClientAuthenticationError),
        (403, HttpResponseError),
        (404, ResourceNotFoundError),
        (429, HttpResponseError),
        (500, HttpResponseError),
    ],
)
async def test_service_errors_are_propagated(
    open_client, invoke, respond, transport, request_payload, status, error_type
):
    problem = {
        "type": None,
        "title": "Service error",
        "status": status,
        "detail": "The request could not be completed.",
        "instance": "/inference/semanticReranking",
        "extensions": {"diagnostic": "test"},
    }
    respond((status, problem, {"Retry-After": "3"}))
    async with open_client(retry_total=0) as client:
        with pytest.raises(error_type) as caught:
            await invoke(client, request_payload)
    assert caught.value.status_code == status
    assert caught.value.response.json() == problem
    assert caught.value.response.headers["X-Correlation-ID"] == "test-correlation-id"
    assert caught.value.response.headers["Retry-After"] == "3"
    transport.send.assert_called_once()


@pytest.mark.asyncio
async def test_retry_after_uses_core_policy(
    open_client, invoke, respond, transport, request_payload, result_payload, asynchronous
):
    respond((429, {"title": "Too many requests", "status": 429}, {"Retry-After": "3"}), (200, result_payload, {}))
    async with open_client(retry_total=1) as client:
        result = await invoke(client, request_payload)
    assert result == result_payload
    assert transport.send.call_count == 2
    if asynchronous:
        transport.sleep.assert_awaited_once_with(3.0)
    else:
        transport.sleep.assert_called_once_with(3.0)


@pytest.mark.asyncio
async def test_transport_errors_are_not_swallowed(open_client, invoke, transport, request_payload):
    transport.send.side_effect = ServiceRequestError("transport failed")
    async with open_client(retry_total=0) as client:
        with pytest.raises(ServiceRequestError, match="transport failed"):
            await invoke(client, request_payload)
    transport.send.assert_called_once()


@pytest.mark.asyncio
async def test_token_policy_requires_https(open_client, invoke, transport, token_credential, request_payload):
    async with open_client(token_credential, endpoint="http://example.inference.azure.com") as client:
        with pytest.raises(ServiceRequestError, match="non-https"):
            await invoke(client, request_payload)
    token_credential.get_token.assert_not_called()
    transport.send.assert_not_called()


@pytest.mark.asyncio
async def test_context_manager_closes_transport(open_client, invoke, respond, transport, request_payload, asynchronous):
    respond((200, {"scores": []}, {}))
    async with open_client() as client:
        await invoke(client, request_payload)
    if asynchronous:
        transport.__aenter__.assert_awaited_once()
        transport.__aexit__.assert_awaited_once()
    else:
        transport.__enter__.assert_called_once()
        transport.__exit__.assert_called_once()


@pytest.mark.parametrize("client_type", [AzureDataAIClient, AsyncAzureDataAIClient])
def test_missing_or_unsupported_credentials_fail(client_type):
    with pytest.raises(ValueError, match="credential"):
        client_type("https://example.inference.azure.com", None)
    with pytest.raises(TypeError, match="Unsupported credential"):
        client_type("https://example.inference.azure.com", object())


@pytest.mark.parametrize("client_type", [AzureDataAIClient, AsyncAzureDataAIClient])
def test_none_endpoint_fails(client_type):
    with pytest.raises(ValueError, match="endpoint"):
        client_type(None, AzureKeyCredential("test-key"))
