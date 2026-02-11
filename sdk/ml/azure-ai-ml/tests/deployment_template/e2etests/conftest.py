# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Shared fixtures for deployment template E2E tests."""

from typing import Callable
import pytest
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment


@pytest.fixture(scope="session")
def test_environment(registry_client: MLClient) -> str:
    """Create or get a test environment in the registry for deployment templates.
    
    Returns:
        The environment ID string to use in deployment templates.
    """
    # Use a simple environment ID that references a basic docker image
    # This doesn't require the environment to exist in the registry
    return "azureml://registries/testFeed/environments/test-sklearn-env/versions/1"


@pytest.fixture
def deployment_template_name(randstr: Callable[[str], str]) -> str:
    """Generate a unique deployment template name for testing."""
    return randstr("dt-e2e-")


@pytest.fixture
def basic_deployment_template_yaml() -> str:
    """Path to basic deployment template YAML."""
    return "./tests/test_configs/deployment_template/basic_deployment_template.yaml"


@pytest.fixture
def minimal_deployment_template_yaml() -> str:
    """Path to minimal deployment template YAML."""
    return "./tests/test_configs/deployment_template/minimal_deployment_template.yaml"
