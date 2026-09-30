# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for azure-ai-agentserver-optimization tests."""

import pytest


ENV_VARS = [
    "OPTIMIZATION_CONFIG",
    "OPTIMIZATION_CANDIDATE_ID",
    "OPTIMIZATION_LOCAL_DIR",
    "OPTIMIZATION_RESOLVE_ENDPOINT",
    "MODEL_DEPLOYMENT_NAME",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Ensure optimization env vars are cleared before each test."""
    for var in ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    yield
