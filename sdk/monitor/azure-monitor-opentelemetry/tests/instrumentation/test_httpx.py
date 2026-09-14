# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest

from opentelemetry.instrumentation.httpx import (
    HTTPXClientInstrumentor,
    HTTPX2ClientInstrumentor,
)


class TestHttpxInstrumentation(unittest.TestCase):
    def test_instrument(self):
        self._instrument(HTTPXClientInstrumentor)
        self._instrument(HTTPX2ClientInstrumentor)

    def _instrument(self, instrumentor):
        try:
            instrumentor().instrument()
        except Exception as ex:  # pylint: disable=broad-except
            print(ex)
            self.fail(f"Unexpected exception raised when instrumenting {instrumentor.__name__}")
