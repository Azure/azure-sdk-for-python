# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
import sys
import unittest

# Skip for Python v3.13 until https://github.com/psycopg/psycopg2/pull/1729 is resolved
# Skip for Python v3.8 on windows due to https://github.com/psycopg/psycopg/issues/936
if (os.name != "nt" or sys.version_info > (3, 8)) and sys.implementation.name != "pypy":
    from opentelemetry.instrumentation.psycopg2 import (
        Psycopg2Instrumentor,
    )


class TestPsycopg2Instrumentation(unittest.TestCase):

    @pytest.mark.skipif(
        (os.name == "nt" and sys.version_info < (3, 9)) or sys.implementation.name == "pypy",
        reason="Psycopg2 not supported for pypy, Windows Py3.8",
    )
    def test_instrument(self):
        try:
            Psycopg2Instrumentor().instrument()
        except Exception as ex:  # pylint: disable=broad-except
            print(ex)
            self.fail(f"Unexpected exception raised when instrumenting {Psycopg2Instrumentor.__name__}")
