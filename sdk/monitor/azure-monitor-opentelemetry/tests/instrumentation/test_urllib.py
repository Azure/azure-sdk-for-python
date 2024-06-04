# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest

from opentelemetry.instrumentation.urllib import (
    URLLibInstrumentor,
)


class TestUrllibInstrumentation(unittest.TestCase):
    def test_instrument(self):
        try:
            URLLibInstrumentor().instrument()
        except Exception as ex:  # pylint: disable=broad-except
            print(ex)
            self.fail(
                f"Unexpected exception raised when instrumenting {URLLibInstrumentor.__name__}"
            )
