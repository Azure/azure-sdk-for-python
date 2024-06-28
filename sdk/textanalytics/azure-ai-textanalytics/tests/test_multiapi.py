# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiVersion
from testcase import TextAnalyticsTest, TextAnalyticsPreparer, get_textanalytics_client
from azure.ai.textanalytics._version import DEFAULT_API_VERSION


class TestMultiApi(TextAnalyticsTest):
    @TextAnalyticsPreparer()
    def test_default_api_version(self, **kwargs):
        client = get_textanalytics_client()
        assert DEFAULT_API_VERSION in client._api_version  # api_version is in query now, not in base_url

    @TextAnalyticsPreparer()
    def test_v3_0_api_version(self, **kwargs):
        client = get_textanalytics_client(api_version=TextAnalyticsApiVersion.V3_0)
        assert "v3.0" in client._client._client._base_url

    @TextAnalyticsPreparer()
    def test_v3_1_api_version(self, **kwargs):
        client = get_textanalytics_client(api_version=TextAnalyticsApiVersion.V3_1)
        assert "v3.1" in client._client._client._base_url
