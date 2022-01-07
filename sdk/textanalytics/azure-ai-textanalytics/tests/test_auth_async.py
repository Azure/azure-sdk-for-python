# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsPreparer
from testcase import TextAnalyticsTest


class TestAuth(TextAnalyticsTest):

    @pytest.mark.live_test_only
    @TextAnalyticsPreparer()
    async def test_active_directory_auth(self, textanalytics_test_endpoint):
        token = self.get_credential(TextAnalyticsClient, is_async=True)
        text_analytics = TextAnalyticsClient(textanalytics_test_endpoint, token)

        docs = [{"id": "1", "text": "I should take my cat to the veterinarian."},
                {"id": "2", "text": "Este es un document escrito en Español."},
                {"id": "3", "text": "猫は幸せ"},
                {"id": "4", "text": "Fahrt nach Stuttgart und dann zum Hotel zu Fu."}]

        response = await text_analytics.detect_language(docs)

    @TextAnalyticsPreparer()
    async def test_empty_credentials(self, textanalytics_test_endpoint, textanalytics_test_api_key):
        with pytest.raises(TypeError):
            text_analytics = TextAnalyticsClient(textanalytics_test_endpoint, "")

    @TextAnalyticsPreparer()
    def test_bad_type_for_credentials(self, textanalytics_test_endpoint, textanalytics_test_api_key):
        with pytest.raises(TypeError):
            text_analytics = TextAnalyticsClient(textanalytics_test_endpoint, [])

    @TextAnalyticsPreparer()
    def test_none_credentials(self, textanalytics_test_endpoint, textanalytics_test_api_key):
        with pytest.raises(ValueError):
            text_analytics = TextAnalyticsClient(textanalytics_test_endpoint, None)

    @TextAnalyticsPreparer()
    def test_none_endpoint(self, textanalytics_test_endpoint, textanalytics_test_api_key):
        with pytest.raises(ValueError):
            text_analytics = TextAnalyticsClient(None, AzureKeyCredential(textanalytics_test_api_key))
