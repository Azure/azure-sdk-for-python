
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
import functools
from azure.core.credentials import AccessToken, AzureKeyCredential
from devtools_testutils import (
    AzureTestCase,
    AzureMgmtPreparer,
)
from azure.ai.textanalytics import (
    RecognizeEntitiesResult,
    RecognizeLinkedEntitiesResult,
    RecognizePiiEntitiesResult,
    AnalyzeSentimentResult,
    ExtractKeyPhrasesResult,
    ExtractSummaryResult,
    _AnalyzeActionsType
)
from devtools_testutils import PowerShellPreparer
from azure_devtools.scenario_tests import ReplayableTest


TextAnalyticsPreparer = functools.partial(
    PowerShellPreparer,
    'textanalytics',
    textanalytics_test_endpoint="https://westus2.api.cognitive.microsoft.com/",
    textanalytics_test_api_key="fakeZmFrZV9hY29jdW50X2tleQ==",
)


class TextAnalyticsClientPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        super(TextAnalyticsClientPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )
        self.client_kwargs = client_kwargs
        self.client_cls = client_cls

    def create_resource(self, name, **kwargs):
        textanalytics_test_endpoint = kwargs.get("textanalytics_test_endpoint")
        textanalytics_test_api_key = kwargs.get("textanalytics_test_api_key")

        if "textanalytics_test_api_key" in self.client_kwargs:
            textanalytics_test_api_key = self.client_kwargs.pop("textanalytics_test_api_key")

        client = self.client_cls(
            textanalytics_test_endpoint,
            AzureKeyCredential(textanalytics_test_api_key),
            **self.client_kwargs
        )
        kwargs.update({"client": client})
        return kwargs


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """
    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args):
        return self.token


class TextAnalyticsTest(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['Ocp-Apim-Subscription-Key']

    def __init__(self, method_name):
        super(TextAnalyticsTest, self).__init__(method_name)

    def get_oauth_endpoint(self):
        return os.getenv("TEXTANALYTICS_TEST_ENDPOINT")

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity import ClientSecretCredential
            return ClientSecretCredential(
                os.getenv("TEXTANALYTICS_TENANT_ID"),
                os.getenv("TEXTANALYTICS_CLIENT_ID"),
                os.getenv("TEXTANALYTICS_CLIENT_SECRET"),
            )
        return self.generate_fake_token()

    def generate_fake_token(self):
        return FakeTokenCredential()

    def assertOpinionsEqual(self, opinion_one, opinion_two):
        self.assertEqual(opinion_one.sentiment, opinion_two.sentiment)
        self.assertEqual(opinion_one.confidence_scores.positive, opinion_two.confidence_scores.positive)
        self.assertEqual(opinion_one.confidence_scores.neutral, opinion_two.confidence_scores.neutral)
        self.assertEqual(opinion_one.confidence_scores.negative, opinion_two.confidence_scores.negative)
        self.validateConfidenceScores(opinion_one.confidence_scores)
        self.assertEqual(opinion_one.offset, opinion_two.offset)
        self.assertEqual(opinion_one.text, opinion_two.text)
        self.assertEqual(opinion_one.is_negated, opinion_two.is_negated)

    def validateConfidenceScores(self, confidence_scores):
        self.assertIsNotNone(confidence_scores.positive)
        self.assertIsNotNone(confidence_scores.neutral)
        self.assertIsNotNone(confidence_scores.negative)
        self.assertEqual(
            confidence_scores.positive + confidence_scores.neutral + confidence_scores.negative, 1
        )

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
        if isinstance(document_result, ExtractSummaryResult):
            return _AnalyzeActionsType.EXTRACT_SUMMARY
        raise ValueError("Your action result doesn't match any of the action types")
