# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Generated API behavior, including native configuration and protocol overloads."""

from io import BytesIO
import json

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.core.rest import HttpRequest

from azure.data.ai import AzureDataAIClient
from azure.data.ai.aio import AzureDataAIClient as AsyncAzureDataAIClient
from azure.data.ai.models import (
    SemanticRerankingDocumentType,
    SemanticRerankingInferenceRequest,
    SemanticRerankingMetaResult,
    SemanticRerankingResult,
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
    respond(*[(status, {"status": status}, {}) for _ in range(3)], (200, result_payload, {}))
    async with open_client(retry_total=3, retry_backoff_max=60) as client:
        result = await invoke(client, request_payload, retry_on_methods=["POST"])
    assert result.as_dict() == result_payload
    assert transport.send.call_count == 4


@pytest.mark.asyncio
async def test_explicit_transport_timeouts(asynchronous):
    client_type = AsyncAzureDataAIClient if asynchronous else AzureDataAIClient
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
