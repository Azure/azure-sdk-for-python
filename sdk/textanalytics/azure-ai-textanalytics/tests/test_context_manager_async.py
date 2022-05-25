# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from unittest import mock
import asyncio
import sys

from testcase import TextAnalyticsTest
from testcase import TextAnalyticsPreparer
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.aio import TextAnalyticsClient

def get_completed_future(result=None):
    future = asyncio.Future()
    future.set_result(result)
    return future

class AsyncMockTransport(mock.MagicMock):
    """Mock with do-nothing aenter/exit for mocking async transport.
    This is unnecessary on 3.8+, where MagicMocks implement aenter/exit.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if sys.version_info < (3, 8):
            self.__aenter__ = mock.Mock(return_value=get_completed_future())
            self.__aexit__ = mock.Mock(return_value=get_completed_future())

class TestContextManager(TextAnalyticsTest):
    @TextAnalyticsPreparer()
    async def test_close(self, **kwargs):
        textanalytics_test_endpoint = kwargs.pop("textanalytics_test_endpoint")
        textanalytics_test_api_key = kwargs.pop("textanalytics_test_api_key")
        transport = AsyncMockTransport()
        client = TextAnalyticsClient(
            textanalytics_test_endpoint,
            AzureKeyCredential(textanalytics_test_api_key),
            transport=transport
        )

        await client.close()
        assert transport.__aenter__.call_count == 0
        assert transport.__aexit__.call_count == 1

    @TextAnalyticsPreparer()
    async def test_context_manager(self, **kwargs):
        textanalytics_test_endpoint = kwargs.pop("textanalytics_test_endpoint")
        textanalytics_test_api_key = kwargs.pop("textanalytics_test_api_key")
        transport = AsyncMockTransport()
        client = TextAnalyticsClient(
            textanalytics_test_endpoint,
            AzureKeyCredential(textanalytics_test_api_key),
            transport=transport
        )

        async with client:
            assert transport.__aenter__.call_count == 1
        assert transport.__aenter__.call_count == 1
        assert transport.__aexit__.call_count == 1