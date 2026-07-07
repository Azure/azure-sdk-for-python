# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for activity protocol tests."""


def pytest_configure(config):
    config.addinivalue_line("markers", "tracing_e2e: end-to-end tracing tests against live Application Insights")
