# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import ApiVersion
from azure.ai.textanalytics.aio import TextAnalyticsClient
from testcase import TextAnalyticsTest, GlobalTextAnalyticsAccountPreparer


class TestRecognizeEntities(TextAnalyticsTest):
    @GlobalTextAnalyticsAccountPreparer()
    def test_default_api_version(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        credential = AzureKeyCredential(text_analytics_account_key)
        client = TextAnalyticsClient(text_analytics_account, credential)

        assert "v3.0" in client._client._client._base_url

    @GlobalTextAnalyticsAccountPreparer()
    def test_v3_0_api_version(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        credential = AzureKeyCredential(text_analytics_account_key)
        client = TextAnalyticsClient(text_analytics_account, credential, api_version=ApiVersion.V3_0)

        assert "v3.0" in client._client._client._base_url

    @GlobalTextAnalyticsAccountPreparer()
    def test_v3_1_preview_1_api_version(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        credential = AzureKeyCredential(text_analytics_account_key)
        client = TextAnalyticsClient(text_analytics_account, credential, api_version=ApiVersion.V3_1_preview_1)

        assert "v3.1-preview.1" in client._client._client._base_url