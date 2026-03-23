# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for scenario tests.

These tests run **live** against a real Azure ML workspace and mirror
customer-production patterns from https://github.com/Azure/azureml-examples/tree/main/sdk/python

Required environment variables (same as existing e2e tests):
    ML_SUBSCRIPTION_ID
    ML_RESOURCE_GROUP
    ML_WORKSPACE_NAME
    ML_TENANT_ID        (optional – for SP auth)
    ML_CLIENT_ID        (optional – for SP auth)
    ML_CLIENT_SECRET    (optional – for SP auth)

Run:
    pytest tests/scenario_tests/ -v --co            # list tests
    pytest tests/scenario_tests/ -v -x              # run all, stop on first failure
    pytest tests/scenario_tests/test_scenario_workspace.py -v
"""

import os
import random
import string
import time

import pytest

from azure.ai.ml import MLClient
from azure.identity import AzureCliCredential, ClientSecretCredential, DefaultAzureCredential


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def credential():
    """Return a live credential. Tries SP first, falls back to CLI/Default."""
    tenant_id = os.environ.get("ML_TENANT_ID")
    sp_id = os.environ.get("ML_CLIENT_ID")
    sp_secret = os.environ.get("ML_CLIENT_SECRET")
    if sp_id and sp_secret and tenant_id:
        return ClientSecretCredential(tenant_id, sp_id, sp_secret)
    try:
        cred = AzureCliCredential()
        cred.get_token("https://management.azure.com/.default")
        return cred
    except Exception:
        return DefaultAzureCredential()


# ---------------------------------------------------------------------------
# Workspace coordinates
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def subscription_id():
    return os.environ["ML_SUBSCRIPTION_ID"]


@pytest.fixture(scope="session")
def resource_group():
    return os.environ["ML_RESOURCE_GROUP"]


@pytest.fixture(scope="session")
def workspace_name():
    return os.environ["ML_WORKSPACE_NAME"]


# ---------------------------------------------------------------------------
# MLClient  (session-scoped so we don't re-init every test)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def ml_client(credential, subscription_id, resource_group, workspace_name) -> MLClient:
    """Create an MLClient just like a customer would."""
    return MLClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name,
    )


# ---------------------------------------------------------------------------
# Random name helpers
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def unique_id():
    """Short random suffix for resource names to avoid collision."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


@pytest.fixture
def rand_name(unique_id):
    """Return a function that generates a prefixed unique name."""

    def _name(prefix: str = "scenario") -> str:
        return f"{prefix}-{unique_id}-{random.randint(1000, 9999)}"

    return _name


# ---------------------------------------------------------------------------
# Convenience fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def wait_for_job():
    """Return a helper that polls a job until it reaches a terminal state."""

    def _wait(ml_client: MLClient, job, timeout_seconds: int = 600):
        terminal_states = {"Completed", "Failed", "Canceled", "NotResponding"}
        start = time.time()
        while time.time() - start < timeout_seconds:
            refreshed = ml_client.jobs.get(job.name)
            if refreshed.status in terminal_states:
                return refreshed
            time.sleep(15)
        raise TimeoutError(f"Job {job.name} did not finish within {timeout_seconds}s (last status: {refreshed.status})")

    return _wait
