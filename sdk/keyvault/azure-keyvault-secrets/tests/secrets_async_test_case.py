# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import functools
import sys

from unittest import mock
from secrets_test_case import KeyVaultTestCase

def _get_completed_future(result=None):
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
            self.__aenter__ = mock.Mock(return_value=_get_completed_future())
            self.__aexit__ = mock.Mock(return_value=_get_completed_future())


class AsyncKeyVaultTestCase(KeyVaultTestCase):
    @staticmethod
    def await_prepared_test(test_fn):
        """Synchronous wrapper for async test methods. Used to avoid making changes
        upstream to AbstractPreparer (which doesn't await the functions it wraps)
        """

        @functools.wraps(test_fn)
        def run(test_class_instance, *args, **kwargs):
            vault_client = kwargs.get("vault_client")
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(test_fn(test_class_instance, vault_client))

        return run

    @staticmethod
    def get_completed_future(result=None):
        future = asyncio.Future()
        future.set_result(result)
        return future


    async def _poll_until_no_exception(self, fn, *resource_names, expected_exception, max_retries=20, retry_delay=3):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""

        for name in resource_names:
            for i in range(max_retries):
                try:
                    # TODO: better for caller to apply args to fn; could also gather
                    await fn(name)
                    break
                except expected_exception:
                    if i == max_retries - 1:
                        raise
                    if self.is_live:
                        await asyncio.sleep(retry_delay)

    async def _poll_until_exception(self, fn, *resource_names, expected_exception, max_retries=20, retry_delay=3):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""

        for name in resource_names:
            for _ in range(max_retries):
                try:
                    # TODO: better for caller to apply args to fn; could also gather
                    await fn(name)
                    if self.is_live:
                        await asyncio.sleep(retry_delay)
                except expected_exception:
                    return
        self.fail("expected exception {expected_exception} was not raised")
