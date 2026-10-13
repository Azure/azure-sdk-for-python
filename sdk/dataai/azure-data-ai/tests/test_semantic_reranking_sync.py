# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Semantic reranking behavior for the synchronous client."""

from copy import deepcopy
from importlib.metadata import version
from importlib.util import find_spec
import inspect
import json
import logging
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from azure.core import PipelineClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
    ServiceRequestError,
)

import azure.data.ai
from azure.data.ai import InferenceClient
from azure.data.ai.models import (
    SemanticRerankingInferenceResult,
    SemanticRerankingScore,
    SentenceScore,
    TokenUsageResult,
)


def test_public_api_exposes_generated_models_without_embeddings():
    assert azure.data.ai.__version__ == version("azure-data-ai")
    assert azure.data.ai.__all__ == ["InferenceClient"]
    assert find_spec("azure.data.ai.models") is not None
    assert find_spec("azure.data.ai.types") is not None
    assert hasattr(InferenceClient, "semantic_rerank")
    assert not hasattr(InferenceClient, "generate_embeddings")
    assert hasattr(InferenceClient, "send_request")
    assert not inspect.iscoroutinefunction(InferenceClient.semantic_rerank)
    assert InferenceClient.__module__ == "azure.data.ai._client"


def test_contract_metadata_uses_azure_data_ai_namespace():
    package = Path(__file__).resolve().parents[1]
    metadata = json.loads((package / "_metadata.json").read_text(encoding="utf-8"))
    properties = json.loads((package / "apiview-properties.json").read_text(encoding="utf-8"))
    assert metadata["apiVersions"] == {"Azure.Data.AI": metadata["apiVersion"]}
    assert properties["CrossLanguagePackageId"] == "Azure.Data.AI"
    expected = {
        "azure.data.ai.InferenceClient.semantic_rerank": "Azure.Data.AI.InferenceOperationGroup.semanticRerank",
        "azure.data.ai.aio.InferenceClient.semantic_rerank": "Azure.Data.AI.InferenceOperationGroup.semanticRerank",
    }
    for name, definition in expected.items():
        assert properties["CrossLanguageDefinitionId"][name] == definition
    assert properties["CrossLanguageDefinitionId"]["azure.data.ai.models.SemanticRerankingMetaResult"] == (
        "Azure.Data.AI.MetaResult"
    )
    assert properties["CrossLanguageDefinitionId"]["azure.data.ai.models.SemanticRerankingDocumentType"] == (
        "Azure.Data.AI.DocumentType"
    )


def test_sentence_scores_follow_updated_contract_without_normalization(transport, respond, request_payload):
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
    with InferenceClient(
        "https://example.inference.azure.com", AzureKeyCredential("test-key"), transport=transport, retry_total=0
    ) as client:
        result = client.semantic_rerank(request_payload)
    assert result == payload
    assert [sentence["index"] for sentence in result["scores"][0]["sentenceScores"]] == [0, 3, 12]


def test_dictionary_round_trip(respond, transport, request_payload, result_payload):
    original = deepcopy(request_payload)
    respond((200, result_payload, {}))
    with InferenceClient(
        "https://example.inference.azure.com", AzureKeyCredential("test-key"), transport=transport, retry_total=0
    ) as client:
        assert not hasattr(client, "inference")
        assert isinstance(client._client, PipelineClient)
        assert hasattr(client, "_serialize")
        result = client.semantic_rerank(request_payload)

    sent = transport.send.call_args.args[0]
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


@pytest.mark.parametrize("payload", [{"scores": []}, {}, {"scores": [], "futureMetadata": {"value": 0}}])
def test_response_is_not_normalized(transport, respond, request_payload, payload):
    respond((200, payload, {}))
    with InferenceClient(
        "https://example.inference.azure.com", AzureKeyCredential("test-key"), transport=transport, retry_total=0
    ) as client:
        result = client.semantic_rerank(request_payload)
    assert isinstance(result, SemanticRerankingInferenceResult)
    assert result == payload


def test_json_documents(respond, transport, result_payload):
    payload = {
        "query": "caf\u00e9",
        "documents": [json.dumps({"meta": {"content": "a caf\u00e9 in Paris"}})],
        "documentType": "json",
        "targetPaths": "meta.content",
        "model": "test-model",
        "returnDocuments": False,
    }
    respond((200, result_payload, {}))
    with InferenceClient(
        "https://example.inference.azure.com", AzureKeyCredential("test-key"), transport=transport, retry_total=0
    ) as client:
        client.semantic_rerank(payload)
    sent = transport.send.call_args.args[0].content
    assert json.loads(sent) == payload


@pytest.mark.parametrize("model", ["semantic-reranker-v1", "future-model"])
def test_all_reranking_options_are_forwarded(respond, transport, result_payload, model):
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
    with InferenceClient(
        "https://example.inference.azure.com", AzureKeyCredential("test-key"), transport=transport, retry_total=0
    ) as client:
        result = client.semantic_rerank(payload)
    assert json.loads(transport.send.call_args.args[0].content) == original
    assert payload == original
    assert result == result_payload


def test_omitted_options_are_not_added(respond, transport):
    payload = {"query": "capital of France", "documents": ["Paris"]}
    respond((200, {"scores": []}, {}))
    with InferenceClient(
        "https://example.inference.azure.com", AzureKeyCredential("test-key"), transport=transport, retry_total=0
    ) as client:
        client.semantic_rerank(payload)
    assert json.loads(transport.send.call_args.args[0].content) == payload


def test_key_authentication(respond, transport, request_payload, result_payload):
    credential = AzureKeyCredential("first-test-key")
    respond((200, result_payload, {}), (200, result_payload, {}))
    with InferenceClient(
        "https://example.inference.azure.com", credential, transport=transport, retry_total=0
    ) as client:
        client.semantic_rerank(request_payload)
        first = transport.send.call_args.args[0]
        assert first.headers["Ocp-Apim-Subscription-Key"] == "first-test-key"
        assert "Authorization" not in first.headers
        credential.update("second-test-key")
        client.semantic_rerank(request_payload)
        second = transport.send.call_args.args[0]
        assert second.headers["Ocp-Apim-Subscription-Key"] == "second-test-key"


def test_raw_keys_require_azure_key_credential(transport):
    with pytest.raises(TypeError, match="Unsupported credential"):
        with InferenceClient("https://example.inference.azure.com", "raw-test-key", transport=transport, retry_total=0):
            pytest.fail("The generated client must require AzureKeyCredential for API keys.")
    transport.send.assert_not_called()


def test_key_is_redacted_from_http_logs(transport, respond, request_payload, caplog):
    caplog.set_level(logging.INFO, logger="azure.core.pipeline.policies.http_logging_policy")
    respond((200, {"scores": []}, {}))
    with InferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("wrapped-test-key"),
        transport=transport,
        retry_total=0,
        logging_enable=True,
    ) as client:
        client.semantic_rerank(request_payload)
    assert "Ocp-Apim-Subscription-Key" in caplog.text
    assert "raw-test-key" not in caplog.text
    assert "wrapped-test-key" not in caplog.text


@pytest.mark.parametrize("scopes", [None, ["https://custom.example/.default"]])
def test_token_authentication(respond, transport, token_credential, request_payload, result_payload, scopes):
    respond((200, result_payload, {}))
    options = {} if scopes is None else {"credential_scopes": scopes}
    with InferenceClient(
        "https://example.inference.azure.com", token_credential, transport=transport, retry_total=0, **options
    ) as client:
        client.semantic_rerank(request_payload)
    token_credential.get_token.assert_called_once()
    assert token_credential.get_token.call_args.args == tuple(scopes or ["https://dbinference.azure.com/.default"])
    sent = transport.send.call_args.args[0]
    assert sent.headers["Authorization"] == "Bearer test-token"
    assert "Ocp-Apim-Subscription-Key" not in sent.headers


@pytest.mark.parametrize("api_version", ["2026-09-01-preview", "test-api-version"])
def test_diagnostic_hook_and_request_options(respond, transport, request_payload, result_payload, api_version):
    captured = []
    respond((200, result_payload, {}))
    with InferenceClient(
        "https://example.inference.azure.com/",
        AzureKeyCredential("test-key"),
        transport=transport,
        retry_total=0,
        api_version=api_version,
    ) as client:
        client.semantic_rerank(
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


def test_request_options_and_endpoint_path_are_preserved(respond, transport, request_payload):
    headers = {"accept": "application/json", "x-test-header": "value"}
    params = {"api-version": "ignored-override", "custom": "value"}
    original_headers = dict(headers)
    original_params = dict(params)
    respond((200, {"scores": []}, {}))
    with InferenceClient(
        "https://example.inference.azure.com/prefix/",
        AzureKeyCredential("test-key"),
        transport=transport,
        retry_total=0,
    ) as client:
        client.semantic_rerank(request_payload, headers=headers, params=params)
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


def test_custom_error_map_is_preserved(transport, respond, request_payload):
    respond((400, {"error": {"code": "CustomError", "message": "Custom error", "status": 400}}, {}))
    error_map = {400: ResourceNotFoundError}
    with InferenceClient(
        "https://example.inference.azure.com", AzureKeyCredential("test-key"), transport=transport, retry_total=0
    ) as client:
        with pytest.raises(ResourceNotFoundError) as caught:
            client.semantic_rerank(request_payload, error_map=error_map)
    assert caught.value.status_code == 400
    assert error_map == {400: ResourceNotFoundError}


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
def test_service_errors_are_propagated(respond, transport, request_payload, status, error_type):
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
    respond((status, response_body, {"Retry-After": "3", "x-ms-error-code": "ServiceError"}))
    with InferenceClient(
        "https://example.inference.azure.com", AzureKeyCredential("test-key"), transport=transport, retry_total=0
    ) as client:
        with pytest.raises(error_type) as caught:
            client.semantic_rerank(request_payload)
    assert caught.value.status_code == status
    assert caught.value.response.json() == response_body
    assert caught.value.error.code == "ServiceError"
    assert caught.value.response.headers["X-Correlation-ID"] == "test-correlation-id"
    assert caught.value.response.headers["Retry-After"] == "3"
    assert caught.value.response.headers["x-ms-error-code"] == "ServiceError"
    transport.send.assert_called_once()


def test_retry_after_uses_core_policy(respond, transport, request_payload, result_payload):
    respond(
        (
            429,
            {"error": {"code": "TooManyRequests", "message": "Too many requests", "status": 429}},
            {"Retry-After": "3", "x-ms-error-code": "TooManyRequests"},
        ),
        (200, result_payload, {}),
    )
    with InferenceClient(
        "https://example.inference.azure.com", AzureKeyCredential("test-key"), transport=transport, retry_total=1
    ) as client:
        result = client.semantic_rerank(request_payload)
    assert result == result_payload
    assert transport.send.call_count == 2
    transport.sleep.assert_called_once_with(3.0)


def test_transport_errors_are_not_swallowed(transport, request_payload):
    transport.send.side_effect = ServiceRequestError("transport failed")
    with InferenceClient(
        "https://example.inference.azure.com", AzureKeyCredential("test-key"), transport=transport, retry_total=0
    ) as client:
        with pytest.raises(ServiceRequestError, match="transport failed"):
            client.semantic_rerank(request_payload)
    transport.send.assert_called_once()


def test_token_policy_requires_https(transport, token_credential, request_payload):
    with InferenceClient(
        "http://example.inference.azure.com", token_credential, transport=transport, retry_total=0
    ) as client:
        with pytest.raises(ServiceRequestError, match="non-https"):
            client.semantic_rerank(request_payload)
    token_credential.get_token.assert_not_called()
    transport.send.assert_not_called()


def test_context_manager_closes_transport(respond, transport, request_payload):
    respond((200, {"scores": []}, {}))
    with InferenceClient(
        "https://example.inference.azure.com", AzureKeyCredential("test-key"), transport=transport, retry_total=0
    ) as client:
        client.semantic_rerank(request_payload)
    transport.__enter__.assert_called_once()
    transport.__exit__.assert_called_once()


def test_missing_or_unsupported_credentials_fail():
    with pytest.raises(ValueError, match="credential"):
        InferenceClient("https://example.inference.azure.com", None)
    with pytest.raises(TypeError, match="Unsupported credential"):
        InferenceClient("https://example.inference.azure.com", object())


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
        InferenceClient("https://example.inference.azure.com", credential)

    assert str(caught.value) == f"Unsupported credential type: {type(credential).__name__}"
    assert secret not in str(caught.value)
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None


def test_none_endpoint_fails():
    with pytest.raises(ValueError, match="endpoint"):
        InferenceClient(None, AzureKeyCredential("test-key"))
