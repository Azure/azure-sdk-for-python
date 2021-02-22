# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.core.pipeline.transport import HttpRequest
from azure.ai.textanalytics.protocol import *

def test_entities_recognition_general(client, documents):
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

def test_entities_recognition_general_full_path(client, documents):
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

def test_entities_recognition_general_preparer(client, documents):
    request = prepare_entities_recognition_general(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )
    response = client.send_request(request)
    response.raise_for_status()
    json_response = response.json()
    assert len(json_response['documents'][0]['entities']) == 4

def test_entities_linking_preparer(client, documents):
    request = prepare_entities_linking(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )
    response = client.send_request(request)
    response.raise_for_status()
    json_response = response.json()
    assert json_response['documents'][0]['entities'][0]['matches'][0]['text'] == "Microsoft"

def test_entities_recognition_pii_preparer(client, documents):
    request = prepare_entities_recognition_pii(
        api_version="v3.1-preview.1",
        body={
            "documents": documents
        },
    )

    response = client.send_request(request)
    response.raise_for_status()
    json_response = response.json()
    assert json_response['documents'][2]["entities"][0]['category'] == "U.S. Social Security Number (SSN)"

def test_languages_preparer(client, documents):
    request = prepare_languages(
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

def test_sentiment_preparer(client, documents):
    request = prepare_sentiment(
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

def test_sentiment_preparer_opinion_mining(client, documents):
    request = prepare_sentiment(
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


def test_query_parameters_preparers(client, documents):
    request = prepare_sentiment(
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

def test_query_parameters_raw(client, documents):

    request = HttpRequest(
        "POST",
        url='/text/analytics/v3.1-preview.1/sentiment',
        json={
            "documents": documents
        },
        query={"showStats": True}
    )
    response = client.send_request(request)
    response.raise_for_status()
    json_response = response.json()
    assert json_response['documents'][0]['sentiment'] == 'positive'
    assert json_response['documents'][1]['sentiment'] == 'positive'
    assert json_response['statistics']['documentsCount'] == 3

def test_azure_key_credential(documents):
    import os
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    client = TextAnalyticsClient(endpoint="https://python-textanalytics.cognitiveservices.azure.com/", credential=AzureKeyCredential(os.environ['AZURE_TEXT_ANALYTICS_KEY']))

    request = prepare_sentiment(
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

