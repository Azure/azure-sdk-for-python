
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from azure.core.credentials import AccessToken, AzureKeyCredential
from devtools_testutils import (
    AzureTestCase,
    AzureMgmtPreparer,
    FakeResource,
    ResourceGroupPreparer,
)
from devtools_testutils.cognitiveservices_testcase import CognitiveServicesAccountPreparer
from azure_devtools.scenario_tests import ReplayableTest

REGION = 'westus2'


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
        return self.get_settings_value("TEXT_ANALYTICS_ENDPOINT_STABLE")

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity import ClientSecretCredential
            return ClientSecretCredential(
                self.get_settings_value("TENANT_ID"),
                self.get_settings_value("CLIENT_ID"),
                self.get_settings_value("CLIENT_SECRET"),
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


class GlobalResourceGroupPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalResourceGroupPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        rg = TextAnalyticsTest._RESOURCE_GROUP
        if self.is_live:
            self.test_class_instance.scrubber.register_name_pair(
                rg.name,
                "rgname"
            )
        else:
            rg = FakeResource(
                name="rgname",
                id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname"
            )

        return {
            'location': REGION,
            'resource_group': rg,
        }


class GlobalTextAnalyticsAccountPreparer(AzureMgmtPreparer):
    def __init__(self):
        super(GlobalTextAnalyticsAccountPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        text_analytics_account = TextAnalyticsTest._TEXT_ANALYTICS_ACCOUNT

        return {
            'location': REGION,
            'resource_group': TextAnalyticsTest._RESOURCE_GROUP,
            'text_analytics_account': text_analytics_account,
            'text_analytics_account_key': TextAnalyticsTest._TEXT_ANALYTICS_KEY,
        }

class TextAnalyticsClientPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        super(TextAnalyticsClientPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )
        self.client_kwargs = client_kwargs
        self.client_cls = client_cls

    def create_resource(self, name, **kwargs):
        client = self.create_text_analytics_client(**kwargs)
        return {"client": client}

    def create_text_analytics_client(self, **kwargs):
        text_analytics_account = self.client_kwargs.pop("text_analytics_account", None)
        if text_analytics_account is None:
            text_analytics_account = kwargs.pop("text_analytics_account")

        text_analytics_account_key = self.client_kwargs.pop("text_analytics_account_key", None)
        if text_analytics_account_key is None:
            text_analytics_account_key = kwargs.pop("text_analytics_account_key")

        return self.client_cls(
            text_analytics_account,
            AzureKeyCredential(text_analytics_account_key),
            **self.client_kwargs
        )


@pytest.fixture(scope="session")
def text_analytics_account():
    test_case = AzureTestCase("__init__")
    rg_preparer = ResourceGroupPreparer(random_name_enabled=True, name_prefix='pycog')
    text_analytics_preparer = CognitiveServicesAccountPreparer(
        random_name_enabled=True, name_prefix='pycog', location=REGION
    )

    try:
        rg_name, rg_kwargs = rg_preparer._prepare_create_resource(test_case)
        TextAnalyticsTest._RESOURCE_GROUP = rg_kwargs['resource_group']
        try:
            text_analytics_name, text_analytics_kwargs = text_analytics_preparer._prepare_create_resource(test_case, **rg_kwargs)
            TextAnalyticsTest._TEXT_ANALYTICS_ACCOUNT = text_analytics_kwargs['cognitiveservices_account']
            TextAnalyticsTest._TEXT_ANALYTICS_KEY = text_analytics_kwargs['cognitiveservices_account_key']
            yield
        finally:
            text_analytics_preparer.remove_resource(
                text_analytics_name,
                resource_group=rg_kwargs['resource_group']
            )
            TextAnalyticsTest._TEXT_ANALYTICS_ACCOUNT = None
            TextAnalyticsTest._TEXT_ANALYTICS_KEY = None
    finally:
        rg_preparer.remove_resource(rg_name)
        TextAnalyticsTest._RESOURCE_GROUP = None
