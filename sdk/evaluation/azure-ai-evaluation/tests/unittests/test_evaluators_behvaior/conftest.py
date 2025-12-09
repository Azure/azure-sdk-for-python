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
def project_endpoint():
    """Get Azure AI Project endpoint from environment."""
    return os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "https://np-wus2-resource.services.ai.azure.com/api/projects/np-wus2")


@pytest.fixture(scope="module")
def model_deployment_name():
    """Get model deployment name from environment."""
    return os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")


@pytest.fixture(scope="module")
def project_client(project_endpoint):
    """Create an AI Project client for testing."""
    credential = DefaultAzureCredential()
    with AIProjectClient(endpoint=project_endpoint, credential=credential) as client:
        yield client


@pytest.fixture(scope="module")
def openai_client(project_client):
    """Get OpenAI client from project client."""
    with project_client.get_openai_client() as client:
        yield client
