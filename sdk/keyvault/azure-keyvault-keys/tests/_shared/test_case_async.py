# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import functools

from azure_devtools.scenario_tests.patches import mock_in_unit_test
from devtools_testutils import AzureMgmtTestCase
from .helpers_async import get_completed_future


def skip_sleep(unit_test):
    async def immediate_return(_):
        return

    return mock_in_unit_test(unit_test, "asyncio.sleep", immediate_return)


class KeyVaultTestCase(AzureMgmtTestCase):
    def __init__(self, *args, match_body=True, **kwargs):
        super().__init__(*args, match_body=match_body, **kwargs)
        self.replay_patches.append(skip_sleep)

    def setUp(self):
        self.list_test_size = 7
        super(KeyVaultTestCase, self).setUp()

    @staticmethod
    def await_prepared_test(test_fn):
        """Synchronous wrapper for async test methods. Used to avoid making changes
        upstream to AbstractPreparer (which doesn't await the functions it wraps)
        """

        @functools.wraps(test_fn)
        def run(test_class_instance, *args, **kwargs):
            loop = asyncio.get_event_loop()
            client = kwargs.get("client")
            result = loop.run_until_complete(test_fn(test_class_instance, *args, **kwargs))
            if client:
                loop.run_until_complete(client.close())
            return result

        return run

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
