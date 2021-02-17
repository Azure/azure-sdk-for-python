# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.ai.textanalytics.protocol import TextAnalyticsPreparers
from azure.identity.aio import DefaultAzureCredential
from azure.core.pipeline.transport import HttpRequest
@pytest.mark.asyncio
async def test_entities_recognition_general(client, documents):
    request = HttpRequest(
        "POST",
        url='/text/analytics/v3.1-preview.1/entities/recognition/general',
        json={
            "documents": documents
        },
    )
    response = await client.send_request(request)
    response.raise_for_status()

    await response.load_body()
    json_response = response.json()
    assert len(json_response['documents'][0]['entities']) == 4

@pytest.mark.asyncio
async def test_entities_recognition_general_full_path(client, documents):
    request = HttpRequest(
        "POST",
        url='https://python-textanalytics.cognitiveservices.azure.com/text/analytics/v3.1-preview.1/entities/recognition/general',
        json={
            "documents": documents
        },
    )
    response = await client.send_request(request)
    response.raise_for_status()
    await response.load_body()
    json_response = response.json()
    assert len(json_response['documents'][0]['entities']) == 4

@pytest.mark.asyncio
async def test_entities_recognition_general_preparer(client, documents):
    request = TextAnalyticsPreparers.prepare_entities_recognition_general(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )
    response = await client.send_request(request)
    response.raise_for_status()
    await response.load_body()
    json_response = response.json()
    assert len(json_response['documents'][0]['entities']) == 4

@pytest.mark.asyncio
async def test_entities_linking_preparer(client, documents):
    request = TextAnalyticsPreparers.prepare_entities_linking(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )
    response = await client.send_request(request)
    response.raise_for_status()
    await response.load_body()
    json_response = response.json()
    assert json_response['documents'][0]['entities'][0]['matches'][0]['text'] == "Microsoft"

@pytest.mark.asyncio
async def test_entities_recognition_pii_preparer(client, documents):
    request = TextAnalyticsPreparers.prepare_entities_recognition_pii(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )

    response = await client.send_request(request)
    response.raise_for_status()
    await response.load_body()
    json_response = response.json()
    assert json_response['documents'][2]["entities"][0]['category'] == "U.S. Social Security Number (SSN)"

@pytest.mark.asyncio
async def test_languages_preparer(client, documents):
    request = TextAnalyticsPreparers.prepare_languages(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )
    response = await client.send_request(request)
    response.raise_for_status()
    await response.load_body()
    json_response = response.json()
    assert json_response['documents'][0]['detectedLanguage']['name'] == 'English'
    assert json_response['documents'][1]['detectedLanguage']['name'] == 'Chinese_Simplified'

@pytest.mark.asyncio
async def test_sentiment_preparer(client, documents):
    request = TextAnalyticsPreparers.prepare_sentiment(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )
    response = await client.send_request(request)
    response.raise_for_status()
    await response.load_body()
    json_response = response.json()
    assert json_response['documents'][0]['sentiment'] == 'positive'
    assert json_response['documents'][1]['sentiment'] == 'positive'

@pytest.mark.asyncio
async def test_sentiment_preparer_opinion_mining(client, documents):
    request = TextAnalyticsPreparers.prepare_sentiment(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
        opinion_mining=True,
    )
    response = await client.send_request(request)
    response.raise_for_status()
    await response.load_body()
    json_response = response.json()
    assert json_response['documents'][0]['sentiment'] == 'positive'
    assert json_response['documents'][1]['sentiment'] == 'positive'

    assert json_response['documents'][0]['sentences'][1]['aspects'][0]['text'] == "food Microsoft"


@pytest.mark.asyncio
async def test_query_params(client, documents):
    request = TextAnalyticsPreparers.prepare_sentiment(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
        show_stats=True
    )
    response = await client.send_request(request)
    response.raise_for_status()
    await response.load_body()
    json_response = response.json()
    assert json_response['documents'][0]['sentiment'] == 'positive'
    assert json_response['documents'][1]['sentiment'] == 'positive'
    assert json_response['statistics']['documentsCount'] == 3