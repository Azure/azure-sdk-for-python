# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Shared pytest fixtures for evaluator behavior tests.
"""

import os
import pytest
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


@pytest.fixture(scope="module")
def project_endpoint() -> str | None:
    """Get Azure AI Project endpoint from environment."""
    project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    print(f"Using project endpoint: {project_endpoint}")
    return project_endpoint


@pytest.fixture(scope="module")
def model_deployment_name() -> str:
    """Get model deployment name from environment."""
    model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
    print(f"Using model deployment name: {model_deployment_name}")
    return model_deployment_name


@pytest.fixture(scope="module")
def project_client(project_endpoint: str | None):
    """Create an AI Project client for testing."""
    credential = DefaultAzureCredential()
    with AIProjectClient(endpoint=project_endpoint, credential=credential) as client:
        yield client


@pytest.fixture(scope="module")
def openai_client(project_client: AIProjectClient):
    """Get OpenAI client from project client."""
    with project_client.get_openai_client() as client:
        yield client
