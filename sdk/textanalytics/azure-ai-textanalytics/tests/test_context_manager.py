# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from unittest import mock
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsTest, TextAnalyticsPreparer
from azure.ai.textanalytics import TextAnalyticsClient

class TestContextManager(TextAnalyticsTest):

    @TextAnalyticsPreparer()
    def test_close(self, **kwargs):
        textanalytics_test_endpoint = kwargs.pop("textanalytics_test_endpoint")
        textanalytics_test_api_key = kwargs.pop("textanalytics_test_api_key")
        transport = mock.MagicMock()
        client = TextAnalyticsClient(
            textanalytics_test_endpoint,
            AzureKeyCredential(textanalytics_test_api_key),
            transport=transport
        )
        client.close()
        assert transport.__enter__.call_count == 0
        assert transport.__exit__.call_count == 1

    @TextAnalyticsPreparer()
    def test_context_manager(self, **kwargs):
        textanalytics_test_endpoint = kwargs.pop("textanalytics_test_endpoint")
        textanalytics_test_api_key = kwargs.pop("textanalytics_test_api_key")
        transport = mock.MagicMock()
        client = TextAnalyticsClient(
            textanalytics_test_endpoint,
            AzureKeyCredential(textanalytics_test_api_key),
            transport=transport
        )

        with client:
            assert transport.__enter__.call_count == 1
        assert transport.__enter__.call_count == 1
        assert transport.__exit__.call_count == 1