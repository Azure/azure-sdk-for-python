# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Semantic reranking behavior for the asynchronous client."""

from copy import deepcopy
from importlib.metadata import version
from importlib.util import find_spec
import inspect
import json
import logging
from urllib.parse import parse_qs, urlsplit

import pytest
from azure.core import AsyncPipelineClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
    ServiceRequestError,
)

import azure.data.ai
from azure.data.ai.aio import InferenceClient as AsyncInferenceClient
from azure.data.ai.models import (
    SemanticRerankingInferenceResult,
    SemanticRerankingScore,
    SentenceScore,
    TokenUsageResult,
)


def test_public_api_exposes_generated_models_without_embeddings():
    assert azure.data.ai.__version__ == version("azure-data-ai")
    assert azure.data.ai.aio.__all__ == ["InferenceClient"]
    assert find_spec("azure.data.ai.models") is not None
    assert find_spec("azure.data.ai.types") is not None
    assert hasattr(AsyncInferenceClient, "semantic_rerank")
    assert not hasattr(AsyncInferenceClient, "generate_embeddings")
    assert hasattr(AsyncInferenceClient, "send_request")
    assert inspect.iscoroutinefunction(AsyncInferenceClient.semantic_rerank)
    assert AsyncInferenceClient.__module__ == "azure.data.ai.aio._client"


@pytest.mark.asyncio
async def test_sentence_scores_follow_updated_contract_without_normalization(
    async_transport, async_respond, request_payload
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
    async_respond((200, payload, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        result = await client.semantic_rerank(request_payload)
    assert result == payload
    assert [sentence["index"] for sentence in result["scores"][0]["sentenceScores"]] == [0, 3, 12]


@pytest.mark.asyncio
async def test_dictionary_round_trip(async_respond, async_transport, request_payload, result_payload):
    original = deepcopy(request_payload)
    async_respond((200, result_payload, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        assert not hasattr(client, "inference")
        assert isinstance(client._client, AsyncPipelineClient)
        assert hasattr(client, "_serialize")
        result = await client.semantic_rerank(request_payload)

    sent = async_transport.send.call_args.args[0]
    assert sent.method == "POST"
    assert sent.url == (
        "https://example.inference.azure.com/inference/semanticReranking?api-version=2026-09-01-preview"
    )
    assert sent.headers["Content-Type"] == "application/json"
    assert sent.headers["Accept"] == "application/json"
    assert json.loads(sent.content) == original
    assert request_payload == original
    assert isinstance(result, SemanticRerankingInferenceResult)
    assert result == result_payload
    assert isinstance(result.scores[0], SemanticRerankingScore)
    assert isinstance(result.scores[0].sentence_scores[0], SentenceScore)
    assert isinstance(result.meta.token_usage, TokenUsageResult)
    assert result.as_dict() == result_payload


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [{"scores": []}, {}, {"scores": [], "futureMetadata": {"value": 0}}])
async def test_response_is_not_normalized(async_transport, async_respond, request_payload, payload):
    async_respond((200, payload, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        result = await client.semantic_rerank(request_payload)
    assert isinstance(result, SemanticRerankingInferenceResult)
    assert result == payload


@pytest.mark.asyncio
async def test_json_documents(async_respond, async_transport, result_payload):
    payload = {
        "query": "caf\u00e9",
        "documents": [json.dumps({"meta": {"content": "a caf\u00e9 in Paris"}})],
        "documentType": "json",
        "targetPaths": "meta.content",
        "model": "test-model",
        "returnDocuments": False,
    }
    async_respond((200, result_payload, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        await client.semantic_rerank(payload)
    sent = async_transport.send.call_args.args[0].content
    assert json.loads(sent) == payload


@pytest.mark.asyncio
@pytest.mark.parametrize("model", ["semantic-reranker-v1", "future-model"])
async def test_all_reranking_options_are_forwarded(async_respond, async_transport, result_payload, model):
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
    async_respond((200, result_payload, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        result = await client.semantic_rerank(payload)
    assert json.loads(async_transport.send.call_args.args[0].content) == original
    assert payload == original
    assert result == result_payload


@pytest.mark.asyncio
async def test_omitted_options_are_not_added(async_respond, async_transport):
    payload = {"query": "capital of France", "documents": ["Paris"]}
    async_respond((200, {"scores": []}, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        await client.semantic_rerank(payload)
    assert json.loads(async_transport.send.call_args.args[0].content) == payload


@pytest.mark.asyncio
async def test_key_authentication(async_respond, async_transport, request_payload, result_payload):
    credential = AzureKeyCredential("first-test-key")
    async_respond((200, result_payload, {}), (200, result_payload, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com", credential, transport=async_transport, retry_total=0
    ) as client:
        await client.semantic_rerank(request_payload)
        first = async_transport.send.call_args.args[0]
        assert first.headers["Ocp-Apim-Subscription-Key"] == "first-test-key"
        assert "Authorization" not in first.headers
        credential.update("second-test-key")
        await client.semantic_rerank(request_payload)
        second = async_transport.send.call_args.args[0]
        assert second.headers["Ocp-Apim-Subscription-Key"] == "second-test-key"


@pytest.mark.asyncio
async def test_raw_keys_require_azure_key_credential(async_transport):
    with pytest.raises(TypeError, match="Unsupported credential"):
        async with AsyncInferenceClient(
            "https://example.inference.azure.com", "raw-test-key", transport=async_transport, retry_total=0
        ):
            pytest.fail("The generated client must require AzureKeyCredential for API keys.")
    async_transport.send.assert_not_awaited()


@pytest.mark.asyncio
async def test_key_is_redacted_from_http_logs(async_transport, async_respond, request_payload, caplog):
    caplog.set_level(logging.INFO, logger="azure.core.pipeline.policies.http_logging_policy")
    async_respond((200, {"scores": []}, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("wrapped-test-key"),
        transport=async_transport,
        retry_total=0,
        logging_enable=True,
    ) as client:
        await client.semantic_rerank(request_payload)
    assert "Ocp-Apim-Subscription-Key" in caplog.text
    assert "raw-test-key" not in caplog.text
    assert "wrapped-test-key" not in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("scopes", [None, ["https://custom.example/.default"]])
async def test_token_authentication(
    async_respond, async_transport, async_token_credential, request_payload, result_payload, scopes
):
    async_respond((200, result_payload, {}))
    options = {} if scopes is None else {"credential_scopes": scopes}
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        async_token_credential,
        transport=async_transport,
        retry_total=0,
        **options,
    ) as client:
        await client.semantic_rerank(request_payload)
    async_token_credential.get_token.assert_awaited_once()
    assert async_token_credential.get_token.call_args.args == tuple(
        scopes or ["https://dbinference.azure.com/.default"]
    )
    sent = async_transport.send.call_args.args[0]
    assert sent.headers["Authorization"] == "Bearer test-token"
    assert "Ocp-Apim-Subscription-Key" not in sent.headers


@pytest.mark.asyncio
@pytest.mark.parametrize("api_version", ["2026-09-01-preview", "test-api-version"])
async def test_diagnostic_hook_and_request_options(
    async_respond, async_transport, request_payload, result_payload, api_version
):
    captured = []
    async_respond((200, result_payload, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com/",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
        api_version=api_version,
    ) as client:
        await client.semantic_rerank(
            request_payload,
            raw_response_hook=captured.append,
            headers={"x-test-header": "value"},
            connection_timeout=5,
            read_timeout=10,
        )
    sent = async_transport.send.call_args.args[0]
    assert urlsplit(sent.url).path == "/inference/semanticReranking"
    assert parse_qs(urlsplit(sent.url).query) == {"api-version": [api_version]}
    assert sent.headers["x-test-header"] == "value"
    assert async_transport.send.call_args.kwargs["connection_timeout"] == 5
    assert async_transport.send.call_args.kwargs["read_timeout"] == 10
    assert len(captured) == 1
    assert captured[0].http_response.headers["X-Correlation-ID"] == "test-correlation-id"


@pytest.mark.asyncio
async def test_request_options_and_endpoint_path_are_preserved(async_respond, async_transport, request_payload):
    headers = {"accept": "application/json", "x-test-header": "value"}
    params = {"api-version": "ignored-override", "custom": "value"}
    original_headers = dict(headers)
    original_params = dict(params)
    async_respond((200, {"scores": []}, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com/prefix/",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        await client.semantic_rerank(request_payload, headers=headers, params=params)
    sent = async_transport.send.call_args.args[0]
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
async def test_custom_error_map_is_preserved(async_transport, async_respond, request_payload):
    async_respond((400, {"error": {"code": "CustomError", "message": "Custom error", "status": 400}}, {}))
    error_map = {400: ResourceNotFoundError}
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        with pytest.raises(ResourceNotFoundError) as caught:
            await client.semantic_rerank(request_payload, error_map=error_map)
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
async def test_service_errors_are_propagated(async_respond, async_transport, request_payload, status, error_type):
    problem = {
        "code": "ServiceError",
        "message": "The request could not be completed.",
        "type": None,
        "title": "Service error",
        "status": status,
        "detail": "The request could not be completed.",
        "instance": "/inference/semanticReranking",
        "extensions": {"diagnostic": "test"},
    }
    response_body = {"error": problem}
    async_respond((status, response_body, {"Retry-After": "3", "x-ms-error-code": "ServiceError"}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        with pytest.raises(error_type) as caught:
            await client.semantic_rerank(request_payload)
    assert caught.value.status_code == status
    assert caught.value.response.json() == response_body
    assert caught.value.error.code == "ServiceError"
    assert caught.value.response.headers["X-Correlation-ID"] == "test-correlation-id"
    assert caught.value.response.headers["Retry-After"] == "3"
    assert caught.value.response.headers["x-ms-error-code"] == "ServiceError"
    async_transport.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_retry_after_uses_core_policy(async_respond, async_transport, request_payload, result_payload):
    async_respond(
        (
            429,
            {"error": {"code": "TooManyRequests", "message": "Too many requests", "status": 429}},
            {"Retry-After": "3", "x-ms-error-code": "TooManyRequests"},
        ),
        (200, result_payload, {}),
    )
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=1,
    ) as client:
        result = await client.semantic_rerank(request_payload)
    assert result == result_payload
    assert async_transport.send.await_count == 2
    async_transport.sleep.assert_awaited_once_with(3.0)


@pytest.mark.asyncio
async def test_transport_errors_are_not_swallowed(async_transport, request_payload):
    async_transport.send.side_effect = ServiceRequestError("transport failed")
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        with pytest.raises(ServiceRequestError, match="transport failed"):
            await client.semantic_rerank(request_payload)
    async_transport.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_token_policy_requires_https(async_transport, async_token_credential, request_payload):
    async with AsyncInferenceClient(
        "http://example.inference.azure.com", async_token_credential, transport=async_transport, retry_total=0
    ) as client:
        with pytest.raises(ServiceRequestError, match="non-https"):
            await client.semantic_rerank(request_payload)
    async_token_credential.get_token.assert_not_awaited()
    async_transport.send.assert_not_awaited()


@pytest.mark.asyncio
async def test_context_manager_closes_transport(async_respond, async_transport, request_payload):
    async_respond((200, {"scores": []}, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        await client.semantic_rerank(request_payload)
    async_transport.__aenter__.assert_awaited_once()
    async_transport.__aexit__.assert_awaited_once()


def test_missing_or_unsupported_credentials_fail():
    with pytest.raises(ValueError, match="credential"):
        AsyncInferenceClient("https://example.inference.azure.com", None)
    with pytest.raises(TypeError, match="Unsupported credential"):
        AsyncInferenceClient("https://example.inference.azure.com", object())


@pytest.mark.parametrize("raw_key", [False, True])
def test_unsupported_credentials_are_not_formatted(raw_key):
    class UnsupportedCredential:
        def __str__(self):
            raise AssertionError("Credential must not be stringified")

        def __repr__(self):
            raise AssertionError("Credential must not be represented")

    secret = "dummy-secret-for-redaction-test"
    credential = secret if raw_key else UnsupportedCredential()
    with pytest.raises(TypeError) as caught:
        AsyncInferenceClient("https://example.inference.azure.com", credential)

    assert str(caught.value) == f"Unsupported credential type: {type(credential).__name__}"
    assert secret not in str(caught.value)
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None


def test_none_endpoint_fails():
    with pytest.raises(ValueError, match="endpoint"):
        AsyncInferenceClient(None, AzureKeyCredential("test-key"))
