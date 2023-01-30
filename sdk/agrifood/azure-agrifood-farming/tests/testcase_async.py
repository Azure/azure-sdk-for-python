
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools

from devtools_testutils import AzureRecordedTestCase
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from azure.agrifood.farming.aio import FarmBeatsClient

class FarmBeatsAsyncTestCase(AzureRecordedTestCase):
    def create_client(self, agrifood_endpoint) -> FarmBeatsClient:
        credential = self.get_credential(FarmBeatsClient, is_async= True)
        return self.create_client_from_credential(
            FarmBeatsClient,
            endpoint=agrifood_endpoint,
            credential=credential,
        )
    
    @staticmethod
    def await_prepared_test(test_fn):
        """Synchronous wrapper for async test methods. Used to avoid making changes
        upstream to AbstractPreparer (which doesn't await the functions it wraps)
        """

        @functools.wraps(test_fn)
        def run(test_class_instance, *args, **kwargs):
            trim_kwargs_from_test_function(test_fn, kwargs)
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(test_fn(test_class_instance, **kwargs))

        return run
