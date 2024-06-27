# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
import functools
from azure.core.credentials import AzureKeyCredential
from devtools_testutils import (
    AzureMgmtPreparer,
    get_credential,
    is_live,
)
from azure.ai.textanalytics import (
    RecognizeEntitiesResult,
    RecognizeLinkedEntitiesResult,
    RecognizePiiEntitiesResult,
    AnalyzeSentimentResult,
    ExtractKeyPhrasesResult,
    _AnalyzeActionsType,
    TextAnalyticsClient,
)
from azure.ai.textanalytics.aio import TextAnalyticsClient as AsyncTextAnalyticsClient
from devtools_testutils import PowerShellPreparer, AzureRecordedTestCase


def is_public_cloud():
    return (".microsoftonline.com" in os.getenv('AZURE_AUTHORITY_HOST', ''))


TextAnalyticsPreparer = functools.partial(
    PowerShellPreparer,
    'textanalytics',
    textanalytics_test_endpoint="https://fakeendpoint.cognitiveservices.azure.com/",
    textanalytics_test_api_key="fakeZmFrZV9hY29jdW50X2tleQ==",
)


def get_textanalytics_client(**kwargs):
    if is_live():
        textanalytics_test_endpoint = os.environ["TEXTANALYTICS_TEST_ENDPOINT"]
    else:
        textanalytics_test_endpoint = "https://fakeendpoint.cognitiveservices.azure.com"
    if "textanalytics_test_api_key" in kwargs:
            textanalytics_test_api_key = kwargs.pop("textanalytics_test_api_key")
            client = TextAnalyticsClient(
            textanalytics_test_endpoint,
            AzureKeyCredential(textanalytics_test_api_key),
            **kwargs
        )
    else:
        client = TextAnalyticsClient(
            textanalytics_test_endpoint,
            get_credential(),
            **kwargs
        )
    return client


def get_async_textanalytics_client(**kwargs):
    if is_live():
        textanalytics_test_endpoint = os.environ["TEXTANALYTICS_TEST_ENDPOINT"]
    else:
        textanalytics_test_endpoint = "https://fakeendpoint.cognitiveservices.azure.com"
    if "textanalytics_test_api_key" in kwargs:
            textanalytics_test_api_key = kwargs.pop("textanalytics_test_api_key")
            client = AsyncTextAnalyticsClient(
            textanalytics_test_endpoint,
            AzureKeyCredential(textanalytics_test_api_key),
            **kwargs
        )
    else:
        client = AsyncTextAnalyticsClient(
            textanalytics_test_endpoint,
            get_credential(is_async=True),
            **kwargs
        )
    return client


class TextAnalyticsTest(AzureRecordedTestCase):

    def assertOpinionsEqual(self, opinion_one, opinion_two):
        assert opinion_one.sentiment == opinion_two.sentiment
        assert opinion_one.confidence_scores.positive == opinion_two.confidence_scores.positive
        assert opinion_one.confidence_scores.neutral == opinion_two.confidence_scores.neutral
        assert opinion_one.confidence_scores.negative == opinion_two.confidence_scores.negative
        self.validateConfidenceScores(opinion_one.confidence_scores)
        assert opinion_one.offset == opinion_two.offset
        assert opinion_one.text == opinion_two.text
        assert opinion_one.is_negated == opinion_two.is_negated

    def validateConfidenceScores(self, confidence_scores):
        # FIXME https://dev.azure.com/msazure/Cognitive%20Services/_workitems/edit/15794991
        return
        # assert confidence_scores.positive is not None
        # assert confidence_scores.neutral is not None
        # assert confidence_scores.negative is not None
        # assert confidence_scores.positive + confidence_scores.neutral + confidence_scores.negative == 1

    def assert_healthcare_data_sources_equal(self, data_sources_a, data_sources_b):
        assert len(data_sources_a) == len(data_sources_b)
        for data_source_a, data_source_b in zip(data_sources_a, data_sources_b):
            assert data_source_a.entity_id == data_source_b.entity_id
            assert data_source_a.name == data_source_b.name


    def assert_healthcare_entities_equal(self, entity_a, entity_b):
        assert entity_a.text == entity_b.text
        assert entity_a.category == entity_b.category
        assert entity_a.subcategory == entity_b.subcategory
        assert len(entity_a.data_sources) == len(entity_b.data_sources)
        self.assert_healthcare_data_sources_equal(entity_a.data_sources, entity_b.data_sources)
        assert entity_a.length == entity_b.length
        assert entity_a.offset == entity_b.offset

    def document_result_to_action_type(self, document_result):
        if isinstance(document_result, RecognizePiiEntitiesResult):
            return _AnalyzeActionsType.RECOGNIZE_PII_ENTITIES
        if isinstance(document_result, RecognizeEntitiesResult):
            return _AnalyzeActionsType.RECOGNIZE_ENTITIES
        if isinstance(document_result, RecognizeLinkedEntitiesResult):
            return _AnalyzeActionsType.RECOGNIZE_LINKED_ENTITIES
        if isinstance(document_result, AnalyzeSentimentResult):
            return _AnalyzeActionsType.ANALYZE_SENTIMENT
        if isinstance(document_result, ExtractKeyPhrasesResult):
            return _AnalyzeActionsType.EXTRACT_KEY_PHRASES
        raise ValueError("Your action result doesn't match any of the action types")
