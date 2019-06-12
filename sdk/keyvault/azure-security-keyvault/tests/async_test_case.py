# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools

from azure.core.exceptions import ResourceNotFoundError

from test_case import KeyVaultTestCase


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

    async def _poll_until_resource_found(self, fn, secret_names, max_retries=20, retry_delay=6):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""

        if not self.is_live:
            return

        for i in range(max_retries):
            await asyncio.sleep(retry_delay)
            try:
                for name in secret_names:
                    # TODO: this enables polling get_secret but it'd be better if caller applied args to fn
                    await fn(name, version="")
                break
            except ResourceNotFoundError:
                if i == max_retries - 1:
                    raise
