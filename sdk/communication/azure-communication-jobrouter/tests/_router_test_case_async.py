# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from abc import abstractmethod
from _shared.utils import get_http_logging_policy
from azure.communication.jobrouter.aio import RouterClient
from _router_test_case import RouterTestCaseBase


class AsyncRouterTestCase(RouterTestCaseBase):
    def setUp(self):
        super(AsyncRouterTestCase, self).setUp()

    @abstractmethod
    async def clean_up(self):
        pass

    def tearDown(self):
        super(AsyncRouterTestCase, self).tearDown()

    def create_client(self) -> RouterClient:
        return RouterClient.from_connection_string(
            conn_str = self.connection_str,
            http_logging_policy=get_http_logging_policy())

    async def _poll_until_no_exception(self, fn, expected_exception, *args, **kwargs):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""
        max_retries = kwargs.pop('max_retries', 20)
        retry_delay = kwargs.pop('retry_delay', 3)

        for i in range(max_retries):
            try:
                return await fn(*args, **kwargs)
            except expected_exception:
                if i == max_retries - 1:
                    raise
                if self.is_live:
                    await asyncio.sleep(retry_delay)

    async def _poll_until_exception(self, fn, expected_exception, max_retries=20, retry_delay=3):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""

        for _ in range(max_retries):
            try:
                await fn()
                if self.is_live:
                    await asyncio.sleep(retry_delay)
            except expected_exception:
                return

        self.fail(f"expected exception {expected_exception} was not raised")

