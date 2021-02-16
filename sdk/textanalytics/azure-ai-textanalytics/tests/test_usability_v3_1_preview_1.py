# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from typing import Text
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.textanalytics.protocol import TextAnalyticsPreparers
from azure.identity import DefaultAzureCredential
from azure.core.pipeline.transport import HttpRequest

client = TextAnalyticsClient(endpoint="https://python-textanalytics.cognitiveservices.azure.com/", credential=DefaultAzureCredential())

documents = [
    """
    Microsoft was founded by Bill Gates and Paul Allen. I like the food Microsoft serves, it's very good.
    """,
    """
    最近由于工作压力太大，我们决定去富酒店度假。那儿的温泉实在太舒服了，我跟我丈夫都完全恢复了工作前的青春精神！加油！
    """,
    """
    My SSN is 859-98-0987
    """
]
documents = [{"id": str(idx), "text": doc} for idx, doc in enumerate(documents)]

def test_entities_recognition_general():
    request = HttpRequest(
        "POST",
        url='/text/analytics/v3.1-preview.1/entities/recognition/general',
        json={
            "documents": documents
        },
    )
    response = client.send_request(request)
    response.raise_for_status()

    json_response = response.json()
    assert len(json_response['documents'][0]['entities']) == 4

def test_entities_recognition_general_full_path():
    request = HttpRequest(
        "POST",
        url='https://python-textanalytics.cognitiveservices.azure.com/text/analytics/v3.1-preview.1/entities/recognition/general',
        json={
            "documents": documents
        },
    )
    response = client.send_request(request)
    response.raise_for_status()
    json_response = response.json()
    assert len(json_response['documents'][0]['entities']) == 4

def test_entities_recognition_general_preparer():
    request = TextAnalyticsPreparers.prepare_entities_recognition_general(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )
    response = client.send_request(request)
    response.raise_for_status()
    json_response = response.json()
    assert len(json_response['documents'][0]['entities']) == 4

def test_entities_linking_preparer():
    request = TextAnalyticsPreparers.prepare_entities_linking(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )
    response = client.send_request(request)
    response.raise_for_status()
    json_response = response.json()
    assert json_response['documents'][0]['entities'][0]['matches'][0]['text'] == "Microsoft"

def test_entities_recognition_pii_preparer():
    request = TextAnalyticsPreparers.prepare_entities_recognition_pii(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )

    response = client.send_request(request)
    response.raise_for_status()
    json_response = response.json()
    assert json_response['documents'][2]["entities"][0]['category'] == "U.S. Social Security Number (SSN)"

def test_languages_preparer():
    request = TextAnalyticsPreparers.prepare_languages(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )
    response = client.send_request(request)
    response.raise_for_status()
    json_response = response.json()
    assert json_response['documents'][0]['detectedLanguage']['name'] == 'English'
    assert json_response['documents'][1]['detectedLanguage']['name'] == 'Chinese_Simplified'

def test_sentiment_preparer():
    request = TextAnalyticsPreparers.prepare_sentiment(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )
    response = client.send_request(request)
    response.raise_for_status()
    json_response = response.json()
    assert json_response['documents'][0]['sentiment'] == 'positive'
    assert json_response['documents'][1]['sentiment'] == 'positive'

def test_sentiment_preparer_opinion_mining():
    request = TextAnalyticsPreparers.prepare_sentiment(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
        opinion_mining=True,
    )
    response = client.send_request(request)
    response.raise_for_status()
    json_response = response.json()
    assert json_response['documents'][0]['sentiment'] == 'positive'
    assert json_response['documents'][1]['sentiment'] == 'positive'

    assert json_response['documents'][0]['sentences'][1]['aspects'][0]['text'] == "food Microsoft"


def test_query_params():
    request = TextAnalyticsPreparers.prepare_sentiment(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
        show_stats=True
    )
    response = client.send_request(request)
    response.raise_for_status()
    json_response = response.json()
    assert json_response['documents'][0]['sentiment'] == 'positive'
    assert json_response['documents'][1]['sentiment'] == 'positive'
    assert json_response['statistics']['documentsCount'] == 3