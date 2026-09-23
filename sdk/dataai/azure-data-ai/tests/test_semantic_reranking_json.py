# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""JSON-document wire coverage using real SDK policies and mocked transport."""

from copy import deepcopy
from contextlib import ExitStack
import importlib.util
import json
from pathlib import Path

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

from azure.data.ai import AzureDataAIClient


@pytest.fixture
def json_documents():
    return [
        {
            "id": 1,
            "title": 'A "caf\u00e9" in Paris',
            "description": "First line.\nSecond line with a backslash: \\ and \u6771\u4eac.",
            "metadata": {"enabled": True, "rating": 4.5, "tags": ["travel", None]},
        },
        {"id": 2, "title": "Azure Cosmos DB", "description": "Globally distributed data.", "metadata": {}},
    ]


@pytest.fixture(params=["raw-key", "key-credential", "entra"])
def json_credential(request, token_credential):
    if request.param == "entra":
        return token_credential
    if request.param == "raw-key":
        return "json-test-key"
    return AzureKeyCredential("json-test-key")


@pytest.mark.asyncio
@pytest.mark.parametrize("target_paths", [None, "description", "title,description"])
@pytest.mark.parametrize("return_documents", [False, True])
@pytest.mark.parametrize("return_sentence_score", [False, True])
async def test_json_round_trip_all_clients_and_credentials(
    open_client,
    invoke,
    respond,
    transport,
    json_documents,
    json_credential,
    target_paths,
    return_documents,
    return_sentence_score,
):
    serialized = [json.dumps(document, ensure_ascii=False) for document in json_documents]
    payload = {
        "query": "A globally distributed database",
        "documents": serialized,
        "topK": 2,
        "returnDocuments": return_documents,
        "returnSentenceScore": return_sentence_score,
        "batchSize": 2,
        "sort": True,
        "documentType": "json",
        "model": "test-model",
    }
    if target_paths is not None:
        payload["targetPaths"] = target_paths
    original = deepcopy(payload)
    scores = []
    for index, score in ((1, 0.99), (0, 0.1)):
        item = {"index": index, "score": score}
        if return_documents:
            item["document"] = serialized[index]
        if return_sentence_score:
            item["sentenceScores"] = [{"index": 0, "score": score}]
        scores.append(item)
    response = {"scores": scores, "meta": {"tokenUsage": {"totalTokens": 20}, "modelName": "test-model"}}
    respond((200, response, {}))

    async with open_client(json_credential) as client:
        result = await invoke(client, payload)

    sent = transport.send.call_args.args[0]
    wire = json.loads(sent.content)
    assert wire == original
    assert payload == original
    assert all(isinstance(document, str) for document in wire["documents"])
    assert [json.loads(document) for document in wire["documents"]] == json_documents
    assert sent.headers["Content-Type"] == "application/json"
    if hasattr(json_credential, "get_token"):
        assert sent.headers["Authorization"] == "Bearer test-token"
        assert "Ocp-Apim-Subscription-Key" not in sent.headers
    else:
        assert sent.headers["Ocp-Apim-Subscription-Key"] == "json-test-key"
        assert "Authorization" not in sent.headers
    assert result == response
    assert [item["index"] for item in result["scores"]] == [1, 0]
    for item in result["scores"]:
        assert ("document" in item) is return_documents
        assert ("sentenceScores" in item) is return_sentence_score
        if return_documents:
            assert isinstance(item["document"], str)
            assert json.loads(item["document"]) == json_documents[item["index"]]


@pytest.mark.asyncio
@pytest.mark.parametrize("documents", [['{"description":'], [{"description": "not a JSON-encoded string"}]])
async def test_invalid_json_document_errors_are_service_errors(
    open_client, invoke, respond, transport, json_credential, documents
):
    payload = {"query": "text", "documents": documents, "documentType": "json", "targetPaths": "description"}
    problem = {"code": "InvalidRequestBody", "message": "Invalid JSON document"}
    respond((400, problem, {}))
    async with open_client(json_credential) as client:
        with pytest.raises(HttpResponseError) as caught:
            await invoke(client, payload)
    assert caught.value.status_code == 400
    assert caught.value.response.json() == problem
    assert json.loads(transport.send.call_args.args[0].content) == payload
    transport.send.assert_called_once()
