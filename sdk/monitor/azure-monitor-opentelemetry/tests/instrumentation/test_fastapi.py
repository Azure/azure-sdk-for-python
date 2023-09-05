# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest

from opentelemetry.instrumentation.fastapi import (
    FastAPIInstrumentor,
)


class TestFastApiInstrumentation(unittest.TestCase):
    def test_instrument(self):
        excluded_urls = "client/.*/info,healthcheck"
        try:
            FastAPIInstrumentor().instrument(excluded_urls=excluded_urls)
        except Exception as ex:  # pylint: disable=broad-except
            print(ex)
            self.fail(
                f"Unexpected exception raised when instrumenting {FastAPIInstrumentor.__name__}"
            )
