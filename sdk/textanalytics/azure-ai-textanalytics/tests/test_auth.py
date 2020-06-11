# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from testcase import TextAnalyticsTest, GlobalTextAnalyticsAccountPreparer
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

class TestAuth(TextAnalyticsTest):
    @pytest.mark.live_test_only
    def test_active_directory_auth(self):
        token = self.generate_oauth_token()
        endpoint = self.get_oauth_endpoint()
        text_analytics = TextAnalyticsClient(endpoint, token)

        docs = [{"id": "1", "text": "I should take my cat to the veterinarian."},
                {"id": "2", "text": "Este es un document escrito en Español."},
                {"id": "3", "text": "猫は幸せ"},
                {"id": "4", "text": "Fahrt nach Stuttgart und dann zum Hotel zu Fu."}]

        response = text_analytics.detect_language(docs)

    @GlobalTextAnalyticsAccountPreparer()
    def test_empty_credentials(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            text_analytics = TextAnalyticsClient(text_analytics_account, "")

    @GlobalTextAnalyticsAccountPreparer()
    def test_bad_type_for_credentials(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(TypeError):
            text_analytics = TextAnalyticsClient(text_analytics_account, [])

    @GlobalTextAnalyticsAccountPreparer()
    def test_none_credentials(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ValueError):
            text_analytics = TextAnalyticsClient(text_analytics_account, None)

    @GlobalTextAnalyticsAccountPreparer()
    def test_none_endpoint(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        with self.assertRaises(ValueError):
            text_analytics = TextAnalyticsClient(None, AzureKeyCredential(text_analytics_account_key))
