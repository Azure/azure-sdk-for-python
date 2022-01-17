
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import asyncio
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from .testcase import CommunicationTestCase


class AsyncCommunicationTestCase(CommunicationTestCase):

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


def get_completed_future(result=None):
    future = asyncio.Future()
    future.set_result(result)
    return future
