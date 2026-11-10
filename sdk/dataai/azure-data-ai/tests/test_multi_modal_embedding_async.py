# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Multimodal embedding tests for the asynchronous client that mock only the transport."""

import inspect
import json
from urllib.parse import parse_qs, urlparse

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

from azure.data.ai.aio import InferenceClient as AsyncInferenceClient
from azure.data.ai.models import (
    MultimodalDenseAndMultiVectorEmbedding,
    MultimodalDenseEmbedding,
    MultimodalEmbeddingResult,
    MultimodalMultiVectorEmbedding,
)

from test_multi_modal_embedding_sync import (
    BOTH_RESULT,
    DENSE_RESULT,
    ENDPOINT,
    LINK_RESULT,
    MULTI_BASE64,
    MULTI_RESULT,
    SAS_TOKEN,
    TRUNCATED_RESULT,
    _blob_image,
)


def _query(request):
    return parse_qs(urlparse(request.url).query)


def test_embedding_operation_is_coroutine():
    assert inspect.iscoroutinefunction(AsyncInferenceClient.multi_modal_embed)
    assert not hasattr(AsyncInferenceClient, "get_multi_modal_embedding_output")


@pytest.mark.asyncio
async def test_embed_sends_keyword_arguments_and_returns_dense_vectors(async_transport, async_respond):
    async_respond((200, DENSE_RESULT, {}))
    contents = [{"id": "doc-1", "type": "text", "content": "Invoice terms: net 30."}]

    async with AsyncInferenceClient(
        ENDPOINT, AzureKeyCredential("test-key"), transport=async_transport, retry_total=0
    ) as client:
        result = await client.multi_modal_embed(contents=contents, vector_type="dense", dimensions=1536)

    sent = async_transport.send.call_args.args[0]
    assert sent.method == "POST"
    assert urlparse(sent.url).path == "/inference/embedding"
    assert _query(sent)["api-version"] == ["2026-11-01-preview"]
    assert json.loads(sent.content) == {"contents": contents, "vectorType": "dense", "dimensions": 1536}
    assert isinstance(result, MultimodalEmbeddingResult)
    assert isinstance(result.data[0], MultimodalDenseEmbedding)
    assert result.data[0].embedding == [0.25, -0.5, 0.75]
    assert result.usage.text_tokens == 11


@pytest.mark.asyncio
async def test_blob_image_returns_multi_vectors(async_transport, async_respond, async_token_credential):
    async_respond((200, MULTI_RESULT, {}))
    request = {"contents": [_blob_image()], "vectorType": "multi", "encodingFormat": "base64", "delivery": "inline"}

    async with AsyncInferenceClient(
        ENDPOINT, async_token_credential, transport=async_transport, retry_total=0
    ) as client:
        result = await client.multi_modal_embed(request)

    assert json.loads(async_transport.send.call_args.args[0].content) == request
    item = result.data[0]
    assert isinstance(item, MultimodalMultiVectorEmbedding)
    assert item.shape == [3, 2]
    assert item.multi_embedding == MULTI_BASE64
    assert result.usage.visual_tokens == 1225


@pytest.mark.asyncio
async def test_both_returns_dense_and_multi_vectors(async_transport, async_respond):
    async_respond((200, BOTH_RESULT, {}))

    async with AsyncInferenceClient(
        ENDPOINT, AzureKeyCredential("test-key"), transport=async_transport, retry_total=0
    ) as client:
        result = await client.multi_modal_embed({"contents": [{"type": "query", "content": "q"}], "vectorType": "both"})

    item = result.data[0]
    assert isinstance(item, MultimodalDenseAndMultiVectorEmbedding)
    assert item.embedding == [0.5, -0.25, 0.75]
    assert item.multi_embedding == MULTI_BASE64


@pytest.mark.asyncio
async def test_link_result_has_output(async_transport, async_respond, async_token_credential):
    async_respond((200, LINK_RESULT, {}))

    async with AsyncInferenceClient(
        ENDPOINT, async_token_credential, transport=async_transport, retry_total=0
    ) as client:
        result = await client.multi_modal_embed({"contents": [_blob_image()], "delivery": "link"})

    assert result.data == []
    assert result.output.sas_token == SAS_TOKEN
    assert result.output.records == 4


@pytest.mark.asyncio
async def test_truncated_text_returns_warning(async_transport, async_respond):
    async_respond((200, TRUNCATED_RESULT, {}))

    async with AsyncInferenceClient(
        ENDPOINT, AzureKeyCredential("test-key"), transport=async_transport, retry_total=0
    ) as client:
        result = await client.multi_modal_embed({"contents": [{"type": "text", "content": "t"}]})

    assert result.data[0].truncated is True
    assert result.data[0].input_tokens == 23171
    assert [(w.code, w.number, w.index) for w in result.warnings] == [("EMBEDDING_INPUT_TRUNCATED", 1001, 0)]


@pytest.mark.asyncio
async def test_blob_read_error_exposes_service_error_code(async_transport, async_respond, async_token_credential):
    message = "The model service couldn't read the blob: contents[0].url: storage returned 404 (BlobNotFound)"
    async_respond((400, {"code": "EMBEDDING_BLOB_READ_FAILED", "message": message}, {}))

    async with AsyncInferenceClient(
        ENDPOINT, async_token_credential, transport=async_transport, retry_total=0
    ) as client:
        with pytest.raises(HttpResponseError) as caught:
            await client.multi_modal_embed({"contents": [_blob_image()]})

    assert caught.value.status_code == 400
    assert caught.value.model.code == "EMBEDDING_BLOB_READ_FAILED"
    assert caught.value.model.message == message
