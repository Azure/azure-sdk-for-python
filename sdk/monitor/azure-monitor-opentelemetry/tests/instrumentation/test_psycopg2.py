# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest

from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.psycopg2 import (
    Psycopg2Instrumentor,
)


class TestPsycopg2Instrumentation(unittest.TestCase):
    def test_instrument(self):
        try:
            Psycopg2Instrumentor().instrument()
        except Exception as ex:  # pylint: disable=broad-except
            print(ex)
            self.fail(
                f"Unexpected exception raised when instrumenting {Psycopg2Instrumentor.__name__}"
            )
