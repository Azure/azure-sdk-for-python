# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest

from opentelemetry.instrumentation.flask import (
    FlaskInstrumentor,
)


class TestFlaskInstrumentation(unittest.TestCase):
    def test_instrument(self):
        excluded_urls = "client/.*/info,healthcheck"
        try:
            FlaskInstrumentor().instrument(excluded_urls=excluded_urls)
        except Exception as ex:  # pylint: disable=broad-except
            print(ex)
            self.fail(
                f"Unexpected exception raised when instrumenting {FlaskInstrumentor.__name__}"
            )
