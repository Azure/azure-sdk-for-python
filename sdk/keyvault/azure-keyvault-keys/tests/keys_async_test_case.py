# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import functools

from keys_test_case import KeyVaultTestCase


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
