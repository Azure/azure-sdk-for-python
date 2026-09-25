# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Mock only the transport, leaving the client and Azure Core policies intact."""

from contextlib import asynccontextmanager
from http import HTTPStatus
import json
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.credentials import AccessToken, AzureKeyCredential, TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import AsyncHttpTransport, HttpTransport
from azure.core.rest import AsyncHttpResponse, HttpResponse
from azure.core.utils import case_insensitive_dict

from azure.data.ai import InferenceClient
from azure.data.ai.aio import InferenceClient as AsyncInferenceClient


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def asynchronous(request):
    return request.param


@pytest.fixture
def transport(asynchronous):
    if asynchronous:
        result = AsyncMock(spec=AsyncHttpTransport)
        result.__aenter__.return_value = result
    else:
        result = MagicMock(spec=HttpTransport)
        result.__enter__.return_value = result
    return result


@pytest.fixture
def respond(transport, asynchronous):
    def configure(*replies):
        queue = iter(replies)

        def send(request, **kwargs):
            status, payload, headers = next(queue)
            content = json.dumps(payload).encode("utf-8")
            response = MagicMock(spec=AsyncHttpResponse if asynchronous else HttpResponse)
            response.request = request
            response.status_code = status
            response.reason = HTTPStatus(status).phrase
            response.headers = case_insensitive_dict(
                {
                    "Content-Type": "application/json",
                    "X-Correlation-ID": "test-correlation-id",
                    **headers,
                }
            )
            response.content_type = "application/json"
            response.content = content
            response.is_closed = True
            response.is_stream_consumed = True
            response.text.return_value = content.decode("utf-8")
            response.json.side_effect = lambda: json.loads(content)
            response.read.return_value = content
            if status >= 400:
                response.raise_for_status.side_effect = HttpResponseError(response=response)
            return response

        transport.send.side_effect = send

    return configure


@pytest.fixture
def open_client(transport, asynchronous):
    @asynccontextmanager
    async def create(credential=None, **kwargs):
        if credential is None:
            credential = AzureKeyCredential("test-key")
        kwargs.setdefault("retry_total", 0)
        endpoint = kwargs.pop("endpoint", "https://example.inference.azure.com")
        if asynchronous:
            async with AsyncInferenceClient(endpoint, credential, transport=transport, **kwargs) as client:
                yield client
        else:
            with InferenceClient(endpoint, credential, transport=transport, **kwargs) as client:
                yield client

    return create


@pytest.fixture
def invoke(asynchronous):
    async def call(client, request, **kwargs):
        if asynchronous:
            return await client.semantic_rerank(request, **kwargs)
        return client.semantic_rerank(request, **kwargs)

    return call


@pytest.fixture
def token_credential(asynchronous):
    credential = MagicMock(spec=AsyncTokenCredential if asynchronous else TokenCredential)
    credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
    return credential


@pytest.fixture(params=["text", "json"], ids=["text-documents", "json-documents"])
def document_type(request):
    return request.param


@pytest.fixture
def request_payload(document_type):
    documents = ["Paris is the capital of France.", "Berlin is the capital of Germany."]
    if document_type == "json":
        documents = [
            json.dumps({"id": index, "description": text, "metadata": {"source": "test"}})
            for index, text in enumerate(documents)
        ]
    payload = {
        "query": "What is the capital of France?",
        "documents": documents,
        "topK": 1,
        "returnDocuments": True,
        "returnSentenceScore": True,
        "batchSize": 2,
        "sort": False,
        "documentType": document_type,
    }
    if document_type == "json":
        payload["targetPaths"] = "description"
    return payload


@pytest.fixture
def result_payload(request_payload):
    return {
        "scores": [
            {
                "index": 0,
                "score": 0.98,
                "document": request_payload["documents"][0],
                "sentenceScores": [{"index": 0, "score": 0.98}],
            }
        ],
        "meta": {
            "tokenUsage": {"totalTokens": 12},
            "latency": {"dataPreprocessTime": 0.1, "inferenceTime": 1.2, "postProcessTime": 0.1},
            "modelName": "test-model",
            "modelVersion": "test-version",
        },
    }
