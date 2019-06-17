# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import functools
import unittest
from .const import ENV_LIVE_TEST
from .utilities import trim_kwargs_from_test_function


def live_only():
    return unittest.skipUnless(
        os.environ.get(ENV_LIVE_TEST, False),
        'This is a live only test. A live test will bypass all vcrpy components.')


def record_only():
    return unittest.skipUnless(
        not os.environ.get(ENV_LIVE_TEST, False),
        'This test is excluded from being run live. To force a recording, please remove the recording file.')


class AllowLargeResponse(object):  # pylint: disable=too-few-public-methods

    def __init__(self, size_kb=1024):
        self.size_kb = size_kb

    def __call__(self, fn):
        def _preparer_wrapper(test_class_instance, **kwargs):
            from azure_devtools.scenario_tests import LargeResponseBodyProcessor
            large_resp_body = next((r for r in test_class_instance.recording_processors
                                    if isinstance(r, LargeResponseBodyProcessor)), None)
            if large_resp_body:
                large_resp_body._max_response_body = self.size_kb  # pylint: disable=protected-access

            trim_kwargs_from_test_function(fn, kwargs)

            fn(test_class_instance, **kwargs)

        setattr(_preparer_wrapper, '__is_preparer', True)
        functools.update_wrapper(_preparer_wrapper, fn)
        return _preparer_wrapper
