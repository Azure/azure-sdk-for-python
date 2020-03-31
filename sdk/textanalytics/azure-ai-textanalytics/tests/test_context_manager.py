# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock  # type: ignore

from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsTest, GlobalTextAnalyticsAccountPreparer
from azure.ai.textanalytics import TextAnalyticsClient

class TestContextManager(TextAnalyticsTest):

    @GlobalTextAnalyticsAccountPreparer()
    def test_close(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        transport = mock.MagicMock()
        client = TextAnalyticsClient(
            text_analytics_account,
            AzureKeyCredential(text_analytics_account_key),
            transport=transport
        )
        client.close()
        assert transport.__enter__.call_count == 0
        assert transport.__exit__.call_count == 1

    @GlobalTextAnalyticsAccountPreparer()
    def test_context_manager(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        transport = mock.MagicMock()
        client = TextAnalyticsClient(
            text_analytics_account,
            AzureKeyCredential(text_analytics_account_key),
            transport=transport
        )

        with client:
            assert transport.__enter__.call_count == 1
        assert transport.__enter__.call_count == 1
        assert transport.__exit__.call_count == 1