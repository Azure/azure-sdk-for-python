# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Overrides the parent (recorded-test) conftest for the live test suite.

The live smoke test never goes through the test proxy (see test_smoke_live.py),
so it doesn't need the autouse ``start_proxy`` fixture from ../conftest.py.
This shadows that fixture so running ``pytest tests/live`` alone never tries
to download/start the proxy.
"""
import pytest


@pytest.fixture(scope="session", autouse=True)
def start_proxy():
    return
