# pylint: disable=line-too-long,useless-suppression
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Multimodal embedding tests that mock only the transport."""

import base64
import datetime
import json
import struct
from urllib.parse import parse_qs, urlparse

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

from azure.data.ai import InferenceClient
from azure.data.ai.models import (
    EmbeddingWarningCode,
    MultimodalDenseAndMultiVectorEmbedding,
    MultimodalDenseEmbedding,
    EmbeddingData,
    MultimodalEmbeddingOutput,
    EmbeddingResult,
    MultimodalEmbeddingWarning,
    MultimodalMultiVectorEmbedding,
)

ENDPOINT = "https://example.inference.azure.com"
MODEL = "microsoft-embedding-1-large"
BLOB_URL = "https://contoso.blob.core.windows.net/pages/p1.jpg"
# A placeholder in the shape of a user delegation SAS; it isn't a credential.
SAS_TOKEN = "sv=2025-07-05&sr=b&sp=r&spr=https&sig=REDACTED"
MULTI_VALUES = (0.5, -0.25, 1.0, 0.0, 0.75, -1.0)
MULTI_BASE64 = base64.b64encode(struct.pack("<6e", *MULTI_VALUES)).decode("ascii")


def _blob_image(item_id="page-1"):
    return {"id": item_id, "kind": "image", "url": BLOB_URL, "sasToken": SAS_TOKEN}


DENSE_RESULT = {
    "object": "list",
    "model": MODEL,
    "modelVersion": "3",
    "outputDataKind": "float32",
    "data": [
        {
            "index": 0,
            "id": "doc-1",
            "contentKind": "text",
            "kind": "multimodal_dense",
            "vectorKind": "dense",
            "embedding": [0.25, -0.5, 0.75],
        }
    ],
    "usage": {"kind": "multimodal", "promptTokens": 11, "totalTokens": 11, "textTokens": 11, "imageCount": 0},
}

MULTI_RESULT = {
    "object": "list",
    "model": MODEL,
    "modelVersion": "3",
    "outputDataKind": "float16",
    "data": [
        {
            "index": 0,
            "id": "page-1",
            "contentKind": "image",
            "kind": "multimodal_multi",
            "vectorKind": "multi",
            "shape": [3, 2],
            "width": 1280,
            "height": 1281,
            "format": "jpeg",
            "tokens": 1236,
            "visualTokens": 1225,
            "multiEmbedding": MULTI_BASE64,
        }
    ],
    "usage": {
        "kind": "multimodal",
        "promptTokens": 1236,
        "totalTokens": 1236,
        "textTokens": 11,
        "imageCount": 1,
        "visualTokens": 1225,
    },
}

BOTH_RESULT = {
    "object": "list",
    "model": MODEL,
    "modelVersion": "3",
    "outputDataKind": "float16",
    "data": [
        {
            "index": 0,
            "id": "q-1",
            "contentKind": "query",
            "kind": "multimodal_dense_multi",
            "vectorKind": "dense_multi",
            "shape": [3, 2],
            "tokens": 20,
            "embedding": [0.5, -0.25, 0.75],
            "multiEmbedding": MULTI_BASE64,
        }
    ],
    "usage": {"kind": "multimodal", "promptTokens": 20, "totalTokens": 20, "textTokens": 20, "imageCount": 0},
}

TRUNCATED_RESULT = {
    "object": "list",
    "model": MODEL,
    "modelVersion": "3",
    "outputDataKind": "float32",
    "data": [
        {
            "index": 0,
            "id": "contract-7",
            "contentKind": "text",
            "kind": "multimodal_dense",
            "vectorKind": "dense",
            "tokens": 8192,
            "truncated": True,
            "inputTokens": 23171,
            "embedding": [0.5],
        }
    ],
    "usage": {"kind": "multimodal", "promptTokens": 8192, "totalTokens": 8192, "textTokens": 8192, "imageCount": 0},
    "warnings": [
        {
            "code": "EMBEDDING_INPUT_TRUNCATED",
            "codeNumber": 1001,
            "index": 0,
            "inputTokens": 23171,
            "tokens": 8192,
            "message": "inputs[0] has 23171 tokens; only the first 8192 were embedded.",
        }
    ],
}

LINK_OUTPUT = {
    "id": "306ee79f632d0d288070105933aa2cfa",
    "url": "https://contosoresults.blob.core.windows.net/embedding-outputs/tenant/account/306ee79f632d0d288070105933aa2cfa.json",
    "sasToken": SAS_TOKEN,
    "expiresAt": "2026-11-05T14:36:01.5279618+00:00",
    "recordCount": 4,
    "sizeInBytes": 129960,
    "sha256": "772f422e1ea48b4f5f51d3ec58af37f9f32acda77c3f9ca7aaa2a4c36d643025",
    "contentType": "application/json",
}

LINK_RESULT = {
    "object": "list",
    "model": MODEL,
    "modelVersion": "3",
    "outputDataKind": "float32",
    "data": [],
    "usage": {
        "kind": "multimodal",
        "promptTokens": 3728,
        "totalTokens": 3728,
        "textTokens": 53,
        "imageCount": 3,
        "visualTokens": 3675,
    },
    "output": LINK_OUTPUT,
}


def _sent_json(request):
    return json.loads(request.content)


def _query(request):
    return parse_qs(urlparse(request.url).query)


def test_embed_sends_camel_case_wire_names_and_returns_dense_vectors(transport, respond):
    respond((200, DENSE_RESULT, {}))
    request = {
        "inputs": [{"id": "doc-1", "kind": "text", "content": "Invoice terms: net 30."}],
        "model": MODEL,
        "modelVersion": "3",
        "vectorKind": "dense",
        "dimensions": 1536,
        "outputDataKind": "float32",
        "encodingFormat": "float",
        "delivery": "inline",
    }

    with InferenceClient(ENDPOINT, AzureKeyCredential("test-key"), transport=transport, retry_total=0) as client:
        result = client.get_embeddings(request)

    sent = transport.send.call_args.args[0]
    assert sent.method == "POST"
    assert urlparse(sent.url).path == "/inference/embedding"
    assert _query(sent)["api-version"] == ["2026-11-01-preview"]
    assert sent.headers["Ocp-Apim-Subscription-Key"] == "test-key"
    assert _sent_json(sent) == request

    assert isinstance(result, EmbeddingResult)
    assert result.model == MODEL
    assert result.model_version == "3"
    assert result.output_data_kind == "float32"
    assert isinstance(result.data[0], MultimodalDenseEmbedding)
    assert result.data[0].kind == "multimodal_dense"
    assert result.data[0].vector_kind == "dense"
    assert result.usage.kind == "multimodal"
    assert result.data[0].embedding == [0.25, -0.5, 0.75]
    assert result.usage.prompt_tokens == 11
    assert result.usage.text_tokens == 11
    assert result.output is None


def test_keyword_arguments_serialize_items_and_options(transport, respond):
    respond((200, BOTH_RESULT, {}))

    with InferenceClient(ENDPOINT, AzureKeyCredential("test-key"), transport=transport, retry_total=0) as client:
        client.get_embeddings(
            inputs=[
                {"kind": "query", "content": "invoice due date"},
                {"id": "page-1", "kind": "image", "url": BLOB_URL, "sasToken": SAS_TOKEN},
            ],
            model=MODEL,
            model_version="3",
            vector_kind="dense_multi",
            dimensions=1536,
            multi_dimensions=128,
            max_vector_count=256,
            output_data_kind="float16",
            encoding_format="base64",
            delivery="link",
        )

    assert _sent_json(transport.send.call_args.args[0]) == {
        "inputs": [{"kind": "query", "content": "invoice due date"}, _blob_image()],
        "model": MODEL,
        "modelVersion": "3",
        "vectorKind": "dense_multi",
        "dimensions": 1536,
        "multiDimensions": 128,
        "maxVectorCount": 256,
        "outputDataKind": "float16",
        "encodingFormat": "base64",
        "delivery": "link",
    }


def test_blob_image_item_has_no_content(transport, respond):
    respond((200, MULTI_RESULT, {}))
    item = {"kind": "image", "url": BLOB_URL, "sasToken": SAS_TOKEN}
    with InferenceClient(ENDPOINT, AzureKeyCredential("test-key"), transport=transport, retry_total=0) as client:
        client.get_embeddings(inputs=[item])
    assert _sent_json(transport.send.call_args.args[0])["inputs"] == [item]
    assert "content" not in item


def test_multi_vector_result_decodes_with_shape(transport, respond, token_credential):
    respond((200, MULTI_RESULT, {}))
    request = {"inputs": [_blob_image()], "vectorKind": "multi", "encodingFormat": "base64", "delivery": "inline"}

    with InferenceClient(ENDPOINT, token_credential, transport=transport, retry_total=0) as client:
        result = client.get_embeddings(request)

    sent = transport.send.call_args.args[0]
    assert sent.headers["Authorization"] == "Bearer test-token"
    assert _sent_json(sent) == request
    item = result.data[0]
    assert isinstance(item, MultimodalMultiVectorEmbedding)
    assert item.kind == "multimodal_multi"
    assert item.vector_kind == "multi"
    assert (item.width, item.height, item.format) == (1280, 1281, "jpeg")
    rows, dims = item.shape
    values = struct.unpack(f"<{rows * dims}e", base64.b64decode(item.multi_embedding))
    assert [list(values[i * dims : (i + 1) * dims]) for i in range(rows)] == [[0.5, -0.25], [1.0, 0.0], [0.75, -1.0]]
    assert item.tokens == 1236
    assert item.visual_tokens == 1225
    assert result.usage.image_count == 1
    assert result.usage.text_tokens == 11
    assert result.usage.visual_tokens == 1225


def test_both_result_has_dense_and_multi_vectors(transport, respond):
    respond((200, BOTH_RESULT, {}))
    request = {"inputs": [{"id": "q-1", "kind": "query", "content": "q"}], "vectorKind": "dense_multi"}

    with InferenceClient(ENDPOINT, AzureKeyCredential("test-key"), transport=transport, retry_total=0) as client:
        result = client.get_embeddings(request)

    assert _sent_json(transport.send.call_args.args[0]) == request
    item = result.data[0]
    assert isinstance(item, MultimodalDenseAndMultiVectorEmbedding)
    assert item.kind == "multimodal_dense_multi"
    assert item.vector_kind == "dense_multi"
    assert item.embedding == [0.5, -0.25, 0.75]
    assert item.shape == [3, 2]
    assert struct.unpack("<6e", base64.b64decode(item.multi_embedding)) == MULTI_VALUES
    assert result.output_data_kind == "float16"


def test_link_result_has_empty_data_and_output(transport, respond, token_credential):
    respond((200, LINK_RESULT, {}))
    request = {"inputs": [{"kind": "query", "content": "q"}, _blob_image()], "delivery": "link"}

    with InferenceClient(ENDPOINT, token_credential, transport=transport, retry_total=0) as client:
        result = client.get_embeddings(request)

    assert result.data == []
    assert result.usage.image_count == 3
    output = result.output
    assert isinstance(output, MultimodalEmbeddingOutput)
    assert output.id == LINK_OUTPUT["id"]
    assert output.url == LINK_OUTPUT["url"]
    assert output.sas_token == SAS_TOKEN
    assert output.expires_at == datetime.datetime(2026, 11, 5, 14, 36, 1, 527961, tzinfo=datetime.timezone.utc)
    assert output.record_count == 4
    assert output.size_in_bytes == 129960
    assert output.sha256 == LINK_OUTPUT["sha256"]
    assert output.content_type == "application/json"


def test_truncated_item_and_warning_deserialize(transport, respond):
    respond((200, TRUNCATED_RESULT, {}))

    with InferenceClient(ENDPOINT, AzureKeyCredential("test-key"), transport=transport, retry_total=0) as client:
        result = client.get_embeddings({"inputs": [{"kind": "text", "content": "t"}]})

    document = result.data[0]
    assert document.tokens == 8192
    assert document.truncated is True
    assert document.input_tokens == 23171

    assert len(result.warnings) == 1
    warning = result.warnings[0]
    assert isinstance(warning, MultimodalEmbeddingWarning)
    assert warning.code == EmbeddingWarningCode.INPUT_TRUNCATED
    assert warning.code_number == 1001
    assert warning.index == 0
    assert warning.input_tokens == 23171
    assert warning.tokens == 8192
    assert warning.message.startswith("inputs[0]")


def test_sas_long_lived_warning_has_no_token_fields(transport, respond, token_credential):
    message = (
        "inputs[1].sasToken stays valid for 119 more minutes. A SAS that expires within 15 minutes is "
        "recommended: it limits what a leaked token would expose."
    )
    body = dict(
        MULTI_RESULT,
        warnings=[{"code": "EMBEDDING_SAS_LONG_LIVED", "codeNumber": 1002, "index": 1, "message": message}],
    )
    respond((200, body, {}))

    with InferenceClient(ENDPOINT, token_credential, transport=transport, retry_total=0) as client:
        result = client.get_embeddings({"inputs": [{"kind": "query", "content": "q"}, _blob_image()]})

    warning = result.warnings[0]
    assert warning.code == EmbeddingWarningCode.SAS_LONG_LIVED
    assert warning.code_number == 1002
    assert warning.index == 1
    assert warning.input_tokens is None
    assert warning.tokens is None
    assert warning.message == message


def test_result_without_token_counts_or_warnings_leaves_them_unset(transport, respond):
    body = dict(DENSE_RESULT, usage={"kind": "multimodal", "imageCount": 0})
    respond((200, body, {}))

    with InferenceClient(ENDPOINT, AzureKeyCredential("test-key"), transport=transport, retry_total=0) as client:
        result = client.get_embeddings({"inputs": [{"kind": "text", "content": "t"}]})

    item = result.data[0]
    assert item.tokens is None
    assert item.visual_tokens is None
    assert item.truncated is None
    assert item.input_tokens is None
    assert result.usage.prompt_tokens is None
    assert result.usage.text_tokens is None
    assert result.warnings is None


def test_unknown_warning_code_is_kept(transport, respond):
    body = dict(DENSE_RESULT, warnings=[{"code": "EMBEDDING_SOMETHING_NEW", "index": 0, "message": "New warning."}])
    respond((200, body, {}))

    with InferenceClient(ENDPOINT, AzureKeyCredential("test-key"), transport=transport, retry_total=0) as client:
        result = client.get_embeddings({"inputs": [{"kind": "text", "content": "t"}]})

    assert result.warnings[0].code == "EMBEDDING_SOMETHING_NEW"
    assert result.warnings[0].code_number is None


def test_unknown_kind_deserializes_to_base_item(transport, respond):
    respond(
        (
            200,
            {
                "object": "list",
                "model": MODEL,
                "data": [{"index": 0, "contentKind": "text", "kind": "sparse", "values": [1, 2]}],
            },
            {},
        )
    )

    with InferenceClient(ENDPOINT, AzureKeyCredential("test-key"), transport=transport, retry_total=0) as client:
        result = client.get_embeddings({"inputs": [{"kind": "text", "content": "hello"}]})

    item = result.data[0]
    assert isinstance(item, EmbeddingData)
    assert not isinstance(
        item, (MultimodalDenseEmbedding, MultimodalMultiVectorEmbedding, MultimodalDenseAndMultiVectorEmbedding)
    )
    assert item.kind == "sparse"
    assert item["values"] == [1, 2]


@pytest.mark.parametrize(
    "status, code",
    [
        (400, "EMBEDDING_URL_NOT_ALLOWED"),
        (400, "EMBEDDING_BLOB_READ_FAILED"),
        (400, "EMBEDDING_DELIVERY_NOT_SUPPORTED"),
        (403, "Forbidden"),
        (413, "EMBEDDING_BLOB_READ_FAILED"),
        (502, "EMBEDDING_BLOB_READ_FAILED"),
        (503, "EMBEDDING_OUTPUT_WRITE_FAILED"),
        (504, "EMBEDDING_BLOB_READ_FAILED"),
    ],
)
def test_embed_errors_expose_service_error_code(transport, respond, token_credential, status, code):
    respond((status, {"error": {"code": code, "message": "Explains what to fix."}}, {}))
    request = {"inputs": [_blob_image()], "delivery": "link"}

    with InferenceClient(ENDPOINT, token_credential, transport=transport, retry_total=0) as client:
        with pytest.raises(HttpResponseError) as caught:
            client.get_embeddings(request)

    assert _sent_json(transport.send.call_args.args[0]) == request
    assert caught.value.status_code == status
    assert caught.value.model.error.code == code
    assert caught.value.model.error.message == "Explains what to fix."


@pytest.mark.parametrize("api_version", ["2026-09-01-preview", "2099-01-01-preview"])
def test_embedding_api_version_validation_is_left_to_service(transport, respond, token_credential, api_version):
    respond((400, {"error": {"code": "UnsupportedApiVersion", "message": "Unsupported API version."}}, {}))
    with InferenceClient(
        ENDPOINT, token_credential, transport=transport, retry_total=0, api_version=api_version
    ) as client:
        with pytest.raises(HttpResponseError) as caught:
            client.get_embeddings({"inputs": [{"kind": "query", "content": "q"}]})

    transport.send.assert_called_once()
    assert _query(transport.send.call_args.args[0])["api-version"] == [api_version]
    assert caught.value.status_code == 400
    assert caught.value.model.error.code == "UnsupportedApiVersion"
