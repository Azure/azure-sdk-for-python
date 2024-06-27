# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from unittest import mock
from testcase import TextAnalyticsTest, TextAnalyticsPreparer, get_textanalytics_client
from azure.ai.textanalytics import TextAnalyticsClient

class TestContextManager(TextAnalyticsTest):

    @TextAnalyticsPreparer()
    def test_close(self, **kwargs):
        transport = mock.MagicMock()
        client = get_textanalytics_client(transport=transport)
        client.close()
        assert transport.__enter__.call_count == 0
        assert transport.__exit__.call_count == 1

    @TextAnalyticsPreparer()
    def test_context_manager(self, **kwargs):
        transport = mock.MagicMock()
        client = get_textanalytics_client(transport=transport)

        with client:
            assert transport.__enter__.call_count == 1
        assert transport.__enter__.call_count == 1
        assert transport.__exit__.call_count == 1