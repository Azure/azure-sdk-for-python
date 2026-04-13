# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest

from opentelemetry.instrumentation.httpx import (
    HTTPXClientInstrumentor,
)


class TestHttpxInstrumentation(unittest.TestCase):
    def test_instrument(self):
        try:
            HTTPXClientInstrumentor().instrument()
        except Exception as ex:  # pylint: disable=broad-except
            print(ex)
            self.fail(f"Unexpected exception raised when instrumenting {HTTPXClientInstrumentor.__name__}")
