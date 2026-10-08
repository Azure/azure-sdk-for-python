# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Generated API behavior for the asynchronous client."""

from datetime import timedelta
from io import BytesIO
import inspect
import json
from typing import get_args, get_type_hints

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ODataV4Format
from azure.core.rest import HttpRequest

from azure.data.ai.aio import InferenceClient as AsyncInferenceClient
from azure.data.ai.models import (
    InferenceErrorResult,
    InnerError,
    LatencyResult,
    ProblemDetails,
    SemanticRerankingDocumentType,
    SemanticRerankingInferenceContent,
    SemanticRerankingInferenceResult,
    SemanticRerankingMetaResult,
    TooManyRequestsResult,
)


@pytest.mark.asyncio
async def test_renamed_document_type_and_metadata(
    async_respond, async_transport, request_payload, result_payload, document_type
):
    request = SemanticRerankingInferenceContent(request_payload)
    request.document_type = SemanticRerankingDocumentType(document_type)
    async_respond((200, result_payload, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        result = await client.semantic_rerank(request)
    assert isinstance(result.meta, SemanticRerankingMetaResult)
    assert result.meta.token_usage.total_tokens == result_payload["meta"]["tokenUsage"]["totalTokens"]
    assert json.loads(async_transport.send.call_args.args[0].content) == request_payload
    assert result.as_dict() == result_payload


@pytest.mark.asyncio
async def test_latency_deserializes_millisecond_durations(async_transport, async_respond, request_payload):
    latency = {"dataPreprocessTime": 1.25, "inferenceTime": 0.125, "postProcessTime": 1500.5}
    async_respond((200, {"scores": [], "meta": {"latency": latency}}, {}))

    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        result = await client.semantic_rerank(request_payload)

    assert isinstance(result.meta.latency, LatencyResult)
    assert result.meta.latency.data_preprocess_duration == timedelta(milliseconds=1.25)
    assert result.meta.latency.inference_duration == timedelta(milliseconds=0.125)
    assert result.meta.latency.post_process_duration == timedelta(milliseconds=1500.5)
    assert result.meta.latency.as_dict() == latency
    assert result["meta"]["latency"] == latency


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,error_code,response_type",
    [
        (400, "InvalidRequestBody", InferenceErrorResult),
        (429, "TooManyRequests", TooManyRequestsResult),
        (500, "InternalServerError", InferenceErrorResult),
    ],
)
async def test_azure_error_envelope_preserves_details(
    async_transport, async_respond, request_payload, status, error_code, response_type
):
    problem = {
        "code": error_code,
        "message": "The request could not be completed.",
        "target": "documents",
        "details": [
            {
                "code": "InvalidDocument",
                "message": "Invalid document.",
                "target": "documents[0]",
                "details": [
                    {"code": "InvalidField", "message": "Invalid field.", "additionalProperty": {"value": None}}
                ],
                "additionalProperty": {"value": [1, None, {"nested": True}]},
                "error": {"serviceExtension": True},
            }
        ],
        "innererror": {"code": "DocumentError", "innererror": {"code": "InvalidField"}},
        "type": "https://example.inference.azure.com/errors/request-failed",
        "title": "Request failed",
        "status": status,
        "detail": "Additional service details.",
        "instance": "/inference/semanticReranking",
        "extensions": {"diagnostic": "test"},
        "additionalProperty": "preserved",
    }
    body = {"error": problem}
    headers = {"x-ms-error-code": error_code}
    if status == 429:
        headers["Retry-After"] = "3"
    async_respond((status, body, headers))

    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        with pytest.raises(HttpResponseError) as caught:
            await client.semantic_rerank(request_payload)

    error = caught.value
    serialized_before_access = json.dumps(error.model.as_dict(), sort_keys=True)
    assert error.status_code == status
    assert error.error.code == error_code
    assert isinstance(error.model, response_type)
    details = error.model.error
    assert isinstance(details, ProblemDetails)
    assert details.code == error_code
    assert details.message == problem["message"]
    assert details.target == "documents"
    assert isinstance(details.details[0], ODataV4Format)
    assert details.details[0].code == "InvalidDocument"
    assert details.details[0].details[0].code == "InvalidField"
    assert isinstance(details.innererror, InnerError)
    assert details.innererror.innererror.code == "InvalidField"
    assert details.detail == problem["detail"]
    assert details.extensions == {"diagnostic": "test"}
    assert details["additionalProperty"] == "preserved"
    assert json.dumps(error.model.as_dict(), sort_keys=True) == serialized_before_access
    assert json.loads(serialized_before_access) == body
    assert error.model.as_dict(exclude_readonly=True) == body
    assert error.response.json() == body
    assert error.response.headers["x-ms-error-code"] == error_code
    if status == 429:
        assert error.response.headers["Retry-After"] == "3"


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["model", "bytes", "stream"])
async def test_generated_request_forms(async_respond, async_transport, request_payload, result_payload, kind):
    if kind == "model":
        request = SemanticRerankingInferenceContent(request_payload)
    else:
        encoded = json.dumps(request_payload).encode()
        request = encoded if kind == "bytes" else BytesIO(encoded)
    async_respond((200, result_payload, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        result = await client.semantic_rerank(request)
    assert isinstance(result, SemanticRerankingInferenceResult)
    assert result.as_dict() == result_payload
    sent = async_transport.send.call_args.args[0].content
    assert json.loads(sent.getvalue() if isinstance(sent, BytesIO) else sent) == request_payload


def test_binary_request_annotation_accepts_bytes():
    request_type = get_type_hints(inspect.unwrap(AsyncInferenceClient.semantic_rerank))["request"]
    assert bytes in get_args(request_type)


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [201, 204])
async def test_only_declared_200_is_success(async_transport, async_respond, request_payload, status):
    async_respond((status, {}, {}))
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        with pytest.raises(HttpResponseError) as error:
            await client.semantic_rerank(request_payload)
    assert error.value.status_code == status


@pytest.mark.asyncio
async def test_protocol_send_request_preserves_raw_response(async_respond, async_transport):
    async_respond((400, {"status": 400}, {}))
    request = HttpRequest("POST", "/inference/semanticReranking", json={})
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        response = await client.send_request(request)
    assert response.status_code == 400
    assert response.json() == {"status": 400}
    assert (
        async_transport.send.call_args.args[0].url == "https://example.inference.azure.com/inference/semanticReranking"
    )
    assert request.url == "/inference/semanticReranking"


@pytest.mark.asyncio
async def test_response_callback(async_transport, async_respond, request_payload, result_payload):
    async_respond((200, result_payload, {}))
    captured = []

    def capture(response, result, headers):
        captured.append((response.http_response.status_code, headers))
        return result

    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=0,
    ) as client:
        result = await client.semantic_rerank(request_payload, cls=capture)
    assert isinstance(result, SemanticRerankingInferenceResult)
    assert captured == [(200, {"X-Correlation-ID": "test-correlation-id"})]


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [429, 502])
async def test_explicit_retry_settings_remain_available(
    async_respond, async_transport, request_payload, result_payload, status
):
    problem = {"error": {"code": "ServiceError", "message": "Retry the request.", "status": status}}
    async_respond(
        *[(status, problem, {"x-ms-error-code": "ServiceError"}) for _ in range(3)],
        (200, result_payload, {}),
    )
    async with AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        transport=async_transport,
        retry_total=3,
        retry_backoff_max=60,
    ) as client:
        result = await client.semantic_rerank(request_payload, retry_on_methods=["POST"])
    assert result.as_dict() == result_payload
    assert async_transport.send.await_count == 4


@pytest.mark.asyncio
async def test_explicit_transport_timeouts():
    client = AsyncInferenceClient(
        "https://example.inference.azure.com",
        AzureKeyCredential("test-key"),
        connection_timeout=100,
        read_timeout=100,
    )
    try:
        config = client._client._pipeline._transport.connection_config
        assert config.timeout == 100
        assert config.read_timeout == 100
    finally:
        await client.close()
