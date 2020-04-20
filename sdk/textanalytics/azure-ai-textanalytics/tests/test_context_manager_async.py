# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock  # type: ignore
import asyncio
import sys

from asynctestcase import AsyncTextAnalyticsTest
from testcase import GlobalTextAnalyticsAccountPreparer
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

class TestContextManager(AsyncTextAnalyticsTest):
    @GlobalTextAnalyticsAccountPreparer()
    async def test_close(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        transport = AsyncMockTransport()
        client = TextAnalyticsClient(
            text_analytics_account,
            AzureKeyCredential(text_analytics_account_key),
            transport=transport
        )

        await client.close()
        assert transport.__aenter__.call_count == 0
        assert transport.__aexit__.call_count == 1

    @GlobalTextAnalyticsAccountPreparer()
    async def test_context_manager(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        transport = AsyncMockTransport()
        client = TextAnalyticsClient(
            text_analytics_account,
            AzureKeyCredential(text_analytics_account_key),
            transport=transport
        )

        async with client:
            assert transport.__aenter__.call_count == 1
        assert transport.__aenter__.call_count == 1
        assert transport.__aexit__.call_count == 1