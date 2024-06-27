# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from unittest import mock
import asyncio
import sys

from testcase import TextAnalyticsTest
from testcase import TextAnalyticsPreparer, get_async_textanalytics_client
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

class TestContextManager(TextAnalyticsTest):
    @TextAnalyticsPreparer()
    async def test_close(self, **kwargs):
        transport = AsyncMockTransport()
        client = get_async_textanalytics_client(transport=transport)

        await client.close()
        assert transport.__aenter__.call_count == 0
        assert transport.__aexit__.call_count == 1

    @TextAnalyticsPreparer()
    async def test_context_manager(self, **kwargs):
        transport = AsyncMockTransport()
        client = get_async_textanalytics_client(transport=transport)

        async with client:
            assert transport.__aenter__.call_count == 1
        assert transport.__aenter__.call_count == 1
        assert transport.__aexit__.call_count == 1