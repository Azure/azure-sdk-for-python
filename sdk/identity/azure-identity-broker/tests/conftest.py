# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest


def pytest_addoption(parser):
    parser.addoption("--manual", action="store_true", default=False, help="include manual tests in test run")


def pytest_configure(config):
    config.addinivalue_line("markers", "manual: mark test as requiring manual interaction")


def pytest_collection_modifyitems(config, items):
    run_manual_tests = config.getoption("--manual")
    skip_manual = pytest.mark.skip(reason="run pytest with '--manual' to run manual tests")
    for test in items:
        if not run_manual_tests and "manual" in test.keywords:
            test.add_marker(skip_manual)
