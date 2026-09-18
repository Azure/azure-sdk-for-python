"""Pytest configuration for the Fabric mapper test suite."""

import pytest


def pytest_collection_modifyitems(items):
    """Include local unit tests in the Cosmos pipeline's selected test set."""
    for item in items:
        if "integration" not in item.keywords and "e2e" not in item.keywords:
            item.add_marker(pytest.mark.cosmosEmulator)
