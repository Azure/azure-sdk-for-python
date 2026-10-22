# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools

from devtools_testutils import AzureRecordedTestCase, trim_kwargs_from_test_function
from azure.agrifood.farming.aio import FarmBeatsClient

class FarmBeatsAsyncTestCase(AzureRecordedTestCase):
    def create_client(self, agrifood_endpoint) -> FarmBeatsClient:
        self.credential = self.get_credential(FarmBeatsClient, is_async= True)
        self.client = self.create_client_from_credential(
            FarmBeatsClient,
            endpoint=agrifood_endpoint,
            credential=self.credential,
        )
        return self.client
    
    async def close_client(self):
        await self.credential.close()
        await self.client.close()
    
    @staticmethod
    def await_prepared_test(test_fn):
        """Synchronous wrapper for async test methods. Used to avoid making changes
        upstream to AbstractPreparer (which doesn't await the functions it wraps)
        """

        @functools.wraps(test_fn)
        def run(test_class_instance, *args, **kwargs):
            trim_kwargs_from_test_function(test_fn, kwargs)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run(test_fn(test_class_instance, **kwargs))

        return run
