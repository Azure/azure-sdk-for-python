# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Overrides the parent (recorded-test) conftest for the unit test suite.

Unit tests don't make any network calls, so they don't need the test-proxy
server that the recorded tests in the parent ``tests/`` directory start. This
fixture shadows the autouse ``start_proxy`` fixture from ../conftest.py so
running ``pytest tests/unit`` alone never tries to download/start the proxy.
"""
import pytest


@pytest.fixture(scope="session", autouse=True)
def start_proxy():
    return
