﻿# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools
from queuetestcase import QueueTestCase

LOGGING_FORMAT = '%(asctime)s %(name)-20s %(levelname)-5s %(message)s'

class AsyncQueueTestCase(QueueTestCase):
    @staticmethod
    def await_prepared_test(test_fn):
        """Synchronous wrapper for async test methods. Used to avoid making changes
        upstream to AbstractPreparer (which doesn't await the functions it wraps)
        """

        @functools.wraps(test_fn)
        def run(test_class_instance, *args, **kwargs):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(test_fn(test_class_instance, **kwargs))

        return run
