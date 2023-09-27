# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest

from opentelemetry.instrumentation.urllib3 import (
    URLLib3Instrumentor,
)


class TestUrllib3Instrumentation(unittest.TestCase):
    def test_instrument(self):
        try:
            URLLib3Instrumentor().instrument()
        except Exception as ex:  # pylint: disable=broad-except
            print(ex)
            self.fail(
                f"Unexpected exception raised when instrumenting {URLLib3Instrumentor.__name__}"
            )
