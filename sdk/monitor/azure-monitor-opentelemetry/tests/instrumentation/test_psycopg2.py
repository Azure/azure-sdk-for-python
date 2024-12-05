# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import sys
import unittest

# Skip for Python v3.13 until https://github.com/psycopg/psycopg2/pull/1729 is resolved
if sys.implementation.name != "pypy" and sys.version_info < (3, 13):
    from opentelemetry.instrumentation.psycopg2 import (
        Psycopg2Instrumentor,
    )


class TestPsycopg2Instrumentation(unittest.TestCase):

    @pytest.mark.skipif(sys.implementation.name == "pypy" or sys.version_info >= (3, 13), reason="Psycopg2 not supported for pypy3.9 and Py3.13")
    def test_instrument(self):
        try:
            Psycopg2Instrumentor().instrument()
        except Exception as ex:  # pylint: disable=broad-except
            print(ex)
            self.fail(
                f"Unexpected exception raised when instrumenting {Psycopg2Instrumentor.__name__}"
            )
