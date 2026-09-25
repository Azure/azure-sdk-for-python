# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Generated API behavior, including native configuration and protocol overloads."""

from datetime import timedelta
from copy import deepcopy
from io import BytesIO
import inspect
import json
from typing import get_args, get_type_hints

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ODataV4Format
from azure.core.rest import HttpRequest

from azure.data.ai import InferenceClient
from azure.data.ai.aio import InferenceClient as AsyncInferenceClient
from azure.data.ai.models import (
    InferenceErrorResponse,
    InnerError,
    LatencyResult,
    ProblemDetails,
    SemanticRerankingDocumentType,
    SemanticRerankingInferenceRequest,
    SemanticRerankingMetaResult,
    SemanticRerankingResult,
    TooManyRequestsResponse,
)


@pytest.mark.asyncio
async def test_renamed_document_type_and_metadata(
    open_client, invoke, respond, transport, request_payload, result_payload, document_type
):
    request = SemanticRerankingInferenceRequest(request_payload)
    request.document_type = SemanticRerankingDocumentType(document_type)
    respond((200, result_payload, {}))
    async with open_client() as client:
        result = await invoke(client, request)
    assert isinstance(result.meta, SemanticRerankingMetaResult)
    assert result.meta.token_usage.total_tokens == result_payload["meta"]["tokenUsage"]["totalTokens"]
    assert json.loads(transport.send.call_args.args[0].content) == request_payload
    assert result.as_dict() == result_payload


@pytest.mark.asyncio
async def test_latency_deserializes_millisecond_durations(open_client, invoke, respond, request_payload):
    latency = {"dataPreprocessTime": 1.25, "inferenceTime": 0.125, "postProcessTime": 1500.5}
    respond((200, {"scores": [], "meta": {"latency": latency}}, {}))

    async with open_client() as client:
        result = await invoke(client, request_payload)

    assert isinstance(result.meta.latency, LatencyResult)
    assert result.meta.latency.data_preprocess_time == timedelta(milliseconds=1.25)
    assert result.meta.latency.inference_time == timedelta(milliseconds=0.125)
    assert result.meta.latency.post_process_time == timedelta(milliseconds=1500.5)
    assert result.meta.latency.as_dict() == latency
    assert result["meta"]["latency"] == latency


@pytest.mark.parametrize("milliseconds", [0, 0.001, 0.125, 1500.5])
def test_latency_serializes_durations_as_numeric_milliseconds(milliseconds):
    duration = timedelta(milliseconds=milliseconds)
    latency = LatencyResult(data_preprocess_time=duration, inference_time=duration, post_process_time=duration)

    assert latency.as_dict() == pytest.approx(
        {
            "dataPreprocessTime": milliseconds,
            "inferenceTime": milliseconds,
            "postProcessTime": milliseconds,
        }
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,error_code,response_type",
    [
        (400, "InvalidRequestBody", InferenceErrorResponse),
        (429, "TooManyRequests", TooManyRequestsResponse),
        (500, "InternalServerError", InferenceErrorResponse),
    ],
)
async def test_azure_error_envelope_preserves_details(
    open_client, invoke, respond, request_payload, status, error_code, response_type
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
    respond((status, body, headers))

    async with open_client() as client:
        with pytest.raises(HttpResponseError) as caught:
            await invoke(client, request_payload)

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


@pytest.mark.parametrize("details", [None, [], [{"code": "Detail", "message": "Details", "target": None}]])
def test_error_details_preserve_null_and_empty_fields(details):
    payload = {"code": "Error", "message": "Failed", "details": details}
    original = deepcopy(payload)
    model = InferenceErrorResponse({"error": payload})

    projected = model.error.details
    if projected:
        assert projected[0].target is None
    assert json.loads(json.dumps(model.as_dict())) == {"error": original}
    assert payload == original


def test_error_details_preserve_missing_and_normalized_fields():
    payload = {
        "code": "Error",
        "message": "Failed",
        "details": [
            {"code": "Missing", "message": "No optional fields"},
            {"code": "Null", "message": "Null fields", "details": None, "innererror": None},
            {"code": "Empty", "message": "Empty fields", "details": [], "innererror": {}},
        ],
    }
    model = ProblemDetails(payload)
    for detail in model.details:
        assert detail.details == []
    assert json.loads(json.dumps(model.as_dict())) == payload

    missing_details = ProblemDetails(code="Error", message="Failed")
    assert missing_details.details is None
    assert "details" not in missing_details.as_dict()
    assert not hasattr(ODataV4Format, "as_dict")


def test_error_detail_mutations_and_extensions_are_preserved():
    payload = {
        "code": "Error",
        "message": "Failed",
        "details": [
            {
                "code": "Original",
                "message": "Details",
                "innererror": {"source": "original"},
                "additionalProperty": {"value": True},
            }
        ],
    }
    original = deepcopy(payload)
    model = ProblemDetails(payload)
    detail = model.details[0]
    detail.code = "Changed"
    detail.innererror["source"] = "changed"
    detail.details.append(ODataV4Format({"code": "Nested", "message": "Nested detail"}))
    model.details.append(ODataV4Format({"code": "Appended", "message": "Appended detail"}))

    serialized = json.loads(json.dumps(model.as_dict()))
    assert serialized["details"][0]["code"] == "Changed"
    assert serialized["details"][0]["innererror"] == {"source": "changed"}
    assert serialized["details"][0]["additionalProperty"] == {"value": True}
    assert serialized["details"][0]["details"][0]["code"] == "Nested"
    assert serialized["details"][1]["code"] == "Appended"
    assert payload == original


def test_error_details_accept_core_objects_and_reassignment():
    core_error = ODataV4Format({"code": "Original", "message": "Details"})
    model = ProblemDetails(code="Error", message="Failed", details=[core_error])
    assert json.loads(json.dumps(model.as_dict()))["details"][0]["code"] == "Original"
    assert model.details[0] is core_error

    model["details"] = [{"code": "Replacement", "message": "Replaced", "additionalProperty": 1}]
    assert model.details[0].code == "Replacement"
    assert model.as_dict()["details"][0]["additionalProperty"] == 1
    model.details = []
    assert model.as_dict()["details"] == []
    model.details = None
    assert "details" not in model.as_dict()


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["model", "bytes", "stream"])
async def test_generated_request_forms(open_client, invoke, respond, transport, request_payload, result_payload, kind):
    if kind == "model":
        request = SemanticRerankingInferenceRequest(request_payload)
    else:
        encoded = json.dumps(request_payload).encode()
        request = encoded if kind == "bytes" else BytesIO(encoded)
    respond((200, result_payload, {}))
    async with open_client() as client:
        result = await invoke(client, request)
    assert isinstance(result, SemanticRerankingResult)
    assert result.as_dict() == result_payload
    sent = transport.send.call_args.args[0].content
    assert json.loads(sent.getvalue() if isinstance(sent, BytesIO) else sent) == request_payload


@pytest.mark.parametrize("client_type", [InferenceClient, AsyncInferenceClient])
def test_binary_request_annotation_accepts_bytes(client_type):
    request_type = get_type_hints(inspect.unwrap(client_type.semantic_rerank))["request"]
    assert bytes in get_args(request_type)


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [201, 204])
async def test_only_declared_200_is_success(open_client, invoke, respond, request_payload, status):
    respond((status, {}, {}))
    async with open_client() as client:
        with pytest.raises(HttpResponseError) as error:
            await invoke(client, request_payload)
    assert error.value.status_code == status


@pytest.mark.asyncio
async def test_protocol_send_request_preserves_raw_response(open_client, respond, transport, asynchronous):
    respond((400, {"status": 400}, {}))
    request = HttpRequest("POST", "/inference/semanticReranking", json={})
    async with open_client() as client:
        response = client.send_request(request)
        if asynchronous:
            response = await response
    assert response.status_code == 400
    assert response.json() == {"status": 400}
    assert transport.send.call_args.args[0].url == "https://example.inference.azure.com/inference/semanticReranking"
    assert request.url == "/inference/semanticReranking"


@pytest.mark.asyncio
async def test_response_callback(open_client, invoke, respond, request_payload, result_payload):
    respond((200, result_payload, {}))
    captured = []

    def capture(response, result, headers):
        captured.append((response.http_response.status_code, headers))
        return result

    async with open_client() as client:
        result = await invoke(client, request_payload, cls=capture)
    assert isinstance(result, SemanticRerankingResult)
    assert captured == [(200, {"X-Correlation-ID": "test-correlation-id"})]


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [429, 502])
async def test_explicit_retry_settings_remain_available(
    open_client, invoke, respond, transport, request_payload, result_payload, status
):
    problem = {"error": {"code": "ServiceError", "message": "Retry the request.", "status": status}}
    respond(
        *[(status, problem, {"x-ms-error-code": "ServiceError"}) for _ in range(3)],
        (200, result_payload, {}),
    )
    async with open_client(retry_total=3, retry_backoff_max=60) as client:
        result = await invoke(client, request_payload, retry_on_methods=["POST"])
    assert result.as_dict() == result_payload
    assert transport.send.call_count == 4


@pytest.mark.asyncio
async def test_explicit_transport_timeouts(asynchronous):
    client_type = AsyncInferenceClient if asynchronous else InferenceClient
    client = client_type(
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
        if asynchronous:
            await client.close()
        else:
            client.close()
