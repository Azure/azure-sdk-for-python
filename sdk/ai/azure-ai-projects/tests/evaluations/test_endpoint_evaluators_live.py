# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Integration tests for endpoint-based evaluators.

These tests run against a live service (INT environment) and validate the full
E2E workflow: connection creation → evaluator registration → evaluation run.

To run these tests:
    pytest tests/evaluations/test_endpoint_evaluators_live.py -s --run-live

Required environment variables:
    AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint
    AZURE_SUBSCRIPTION_ID - Azure subscription ID
    AZURE_RESOURCE_GROUP - Resource group containing the AI account
    ENDPOINT_URL - URL of the scoring endpoint
    ENDPOINT_API_KEY - API key for the scoring endpoint
    ENDPOINT_APP_ID - App Registration ID protecting the endpoint (for Entra ID tests)
"""

import os
import time
from urllib.parse import urlparse

import pytest
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    EndpointBasedEvaluatorDefinition,
    EvaluatorCategory,
    EvaluatorType,
    EvaluatorVersion,
)
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import ConnectionPropertiesV2BasicResource

from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
from openai.types.eval_create_params import DataSourceConfigCustom


# Skip all tests in this module unless running live
pytestmark = pytest.mark.skipif(
    os.environ.get("AZURE_TEST_RUN_LIVE") != "true",
    reason="Live tests only — set AZURE_TEST_RUN_LIVE=true",
)

SAMPLE_DATA = [
    SourceFileContentContent(
        item={
            "query": "What is machine learning?",
            "response": "Machine learning is a subset of AI that enables systems to learn from data.",
            "context": "AI and ML overview",
        }
    ),
    SourceFileContentContent(
        item={
            "query": "What is the capital of France?",
            "response": "The capital of France is Paris.",
            "context": "Geography question about European capitals",
        }
    ),
]

DATA_SOURCE_CONFIG = DataSourceConfigCustom(
    {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "response": {"type": "string"},
                "context": {"type": "string"},
            },
            "required": ["query", "response"],
        },
        "include_sample_schema": True,
    }
)


@pytest.fixture(scope="module")
def env():
    """Load and validate required environment variables."""
    required = ["AZURE_AI_PROJECT_ENDPOINT", "AZURE_SUBSCRIPTION_ID", "AZURE_RESOURCE_GROUP", "ENDPOINT_URL"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        pytest.skip(f"Missing environment variables: {', '.join(missing)}")

    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    return {
        "endpoint": endpoint,
        "subscription_id": os.environ["AZURE_SUBSCRIPTION_ID"],
        "resource_group": os.environ["AZURE_RESOURCE_GROUP"],
        "endpoint_url": os.environ["ENDPOINT_URL"],
        "endpoint_api_key": os.environ.get("ENDPOINT_API_KEY", ""),
        "endpoint_app_id": os.environ.get("ENDPOINT_APP_ID", ""),
        "account_name": urlparse(endpoint).hostname.split(".")[0],
    }


@pytest.fixture(scope="module")
def credential():
    """Provide a shared credential for the test module."""
    cred = DefaultAzureCredential()
    yield cred
    cred.close()


@pytest.fixture(scope="module")
def project_client(env, credential):
    """Provide a shared AIProjectClient."""
    client = AIProjectClient(endpoint=env["endpoint"], credential=credential)
    yield client
    client.close()


@pytest.fixture(scope="module")
def oai_client(project_client):
    """Provide a shared OpenAI client from the project."""
    client = project_client.get_openai_client()
    yield client
    client.close()


@pytest.fixture(scope="module")
def mgmt_client(env, credential):
    """Provide a shared CognitiveServicesManagementClient."""
    client = CognitiveServicesManagementClient(
        credential=credential,
        subscription_id=env["subscription_id"],
    )
    yield client
    client.close()


def _poll_run(oai_client, eval_id, run_id, timeout=120):
    """Poll an evaluation run until completion or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        run = oai_client.evals.runs.retrieve(run_id=run_id, eval_id=eval_id)
        if run.status in ("completed", "failed"):
            return run
        time.sleep(5)
    pytest.fail(f"Evaluation run {run_id} did not complete within {timeout}s")


class TestEndpointEvaluatorApiKey:
    """Integration tests for endpoint evaluators with API Key authentication."""

    def test_api_key_e2e_success(self, env, project_client, oai_client, mgmt_client):
        """Register endpoint evaluator with API key connection, run evaluation successfully."""
        if not env["endpoint_api_key"]:
            pytest.skip("ENDPOINT_API_KEY not set")

        connection_name = "test-apikey-conn-live"
        evaluator_name = "test-endpoint-eval-apikey-live"

        # Step 1: Create connection
        connection = ConnectionPropertiesV2BasicResource(
            properties={
                "category": "ApiKey",
                "target": env["endpoint_url"],
                "authType": "ApiKey",
                "credentials": {"key": env["endpoint_api_key"]},
            },
        )
        mgmt_client.account_connections.create(
            resource_group_name=env["resource_group"],
            account_name=env["account_name"],
            connection_name=connection_name,
            connection=connection,
        )

        # Step 2: Register evaluator
        evaluator = project_client.beta.evaluators.create_version(
            name=evaluator_name,
            evaluator_version=EvaluatorVersion(
                categories=[EvaluatorCategory.QUALITY],
                evaluator_type=EvaluatorType.CUSTOM,
                definition=EndpointBasedEvaluatorDefinition(connection_name=connection_name),
                display_name="Test Endpoint Evaluator (API Key)",
                description="Integration test evaluator",
            ),
        )
        assert evaluator.name == evaluator_name

        # Step 3: Create evaluation
        testing_criteria = [
            {
                "type": "azure_ai_evaluator",
                "name": "endpoint_eval_apikey",
                "evaluator_name": evaluator_name,
                "data_mapping": {
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                    "context": "{{item.context}}",
                },
            }
        ]
        eval_object = oai_client.evals.create(
            name="test-endpoint-apikey-live",
            data_source_config=DATA_SOURCE_CONFIG,
            testing_criteria=testing_criteria,
        )
        assert eval_object.id is not None

        # Step 4: Run evaluation
        eval_run = oai_client.evals.runs.create(
            eval_id=eval_object.id,
            name="test-apikey-run",
            data_source=CreateEvalJSONLRunDataSourceParam(
                type="jsonl",
                source=SourceFileContent(type="file_content", content=SAMPLE_DATA),
            ),
        )

        # Step 5: Poll and validate
        run = _poll_run(oai_client, eval_object.id, eval_run.id)
        assert run.status == "completed"

        output_items = list(oai_client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
        assert len(output_items) == 2
        for item in output_items:
            assert item.status == "completed"
            assert len(item.results) > 0

    def test_api_key_invalid_key_returns_error(self, env, project_client, oai_client, mgmt_client):
        """Run endpoint evaluator with invalid API key, expect error status on items."""
        connection_name = "test-apikey-invalid-conn-live"
        evaluator_name = "test-endpoint-eval-apikey-invalid-live"

        # Create connection with invalid key
        connection = ConnectionPropertiesV2BasicResource(
            properties={
                "category": "ApiKey",
                "target": env["endpoint_url"],
                "authType": "ApiKey",
                "credentials": {"key": "invalid-key-that-should-fail"},
            },
        )
        mgmt_client.account_connections.create(
            resource_group_name=env["resource_group"],
            account_name=env["account_name"],
            connection_name=connection_name,
            connection=connection,
        )

        # Register evaluator
        evaluator = project_client.beta.evaluators.create_version(
            name=evaluator_name,
            evaluator_version=EvaluatorVersion(
                categories=[EvaluatorCategory.QUALITY],
                evaluator_type=EvaluatorType.CUSTOM,
                definition=EndpointBasedEvaluatorDefinition(connection_name=connection_name),
                display_name="Test Endpoint Evaluator (Invalid Key)",
                description="Integration test - invalid key",
            ),
        )

        # Create eval + run
        testing_criteria = [
            {
                "type": "azure_ai_evaluator",
                "name": "endpoint_eval_invalid",
                "evaluator_name": evaluator_name,
                "data_mapping": {"query": "{{item.query}}", "response": "{{item.response}}"},
            }
        ]
        eval_object = oai_client.evals.create(
            name="test-endpoint-apikey-invalid-live",
            data_source_config=DATA_SOURCE_CONFIG,
            testing_criteria=testing_criteria,
        )
        eval_run = oai_client.evals.runs.create(
            eval_id=eval_object.id,
            name="test-invalid-key-run",
            data_source=CreateEvalJSONLRunDataSourceParam(
                type="jsonl",
                source=SourceFileContent(type="file_content", content=SAMPLE_DATA),
            ),
        )

        # Poll — run should complete but items should have error status
        run = _poll_run(oai_client, eval_object.id, eval_run.id)
        assert run.status == "completed"

        output_items = list(oai_client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
        assert len(output_items) == 2
        for item in output_items:
            # Items should be in error state since the endpoint rejected the invalid key
            assert item.status == "error" or (item.results and len(item.results) == 0)


class TestEndpointEvaluatorEntraId:
    """Integration tests for endpoint evaluators with Entra ID authentication."""

    def test_entra_id_e2e_success(self, env, project_client, oai_client, mgmt_client):
        """Register endpoint evaluator with Entra ID connection, run evaluation successfully."""
        if not env["endpoint_app_id"]:
            pytest.skip("ENDPOINT_APP_ID not set")

        connection_name = "test-entra-conn-live"
        evaluator_name = "test-endpoint-eval-entra-live"

        # Step 1: Create AAD connection
        connection = ConnectionPropertiesV2BasicResource(
            properties={
                "category": "CustomKeys",
                "target": env["endpoint_url"],
                "authType": "AAD",
                "metadata": {"ResourceId": f"api://{env['endpoint_app_id']}"},
            },
        )
        mgmt_client.account_connections.create(
            resource_group_name=env["resource_group"],
            account_name=env["account_name"],
            connection_name=connection_name,
            connection=connection,
        )

        # Step 2: Register evaluator
        evaluator = project_client.beta.evaluators.create_version(
            name=evaluator_name,
            evaluator_version=EvaluatorVersion(
                categories=[EvaluatorCategory.QUALITY],
                evaluator_type=EvaluatorType.CUSTOM,
                definition=EndpointBasedEvaluatorDefinition(connection_name=connection_name),
                display_name="Test Endpoint Evaluator (Entra ID)",
                description="Integration test evaluator with Entra ID",
            ),
        )
        assert evaluator.name == evaluator_name

        # Step 3: Create evaluation
        testing_criteria = [
            {
                "type": "azure_ai_evaluator",
                "name": "endpoint_eval_entra",
                "evaluator_name": evaluator_name,
                "data_mapping": {
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                    "context": "{{item.context}}",
                },
            }
        ]
        eval_object = oai_client.evals.create(
            name="test-endpoint-entra-live",
            data_source_config=DATA_SOURCE_CONFIG,
            testing_criteria=testing_criteria,
        )
        assert eval_object.id is not None

        # Step 4: Run evaluation
        eval_run = oai_client.evals.runs.create(
            eval_id=eval_object.id,
            name="test-entra-run",
            data_source=CreateEvalJSONLRunDataSourceParam(
                type="jsonl",
                source=SourceFileContent(type="file_content", content=SAMPLE_DATA),
            ),
        )

        # Step 5: Poll and validate
        run = _poll_run(oai_client, eval_object.id, eval_run.id)
        assert run.status == "completed"

        output_items = list(oai_client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
        assert len(output_items) == 2
        for item in output_items:
            assert item.status == "completed"
            assert len(item.results) > 0
            # Verify we got actual scoring results
            result = item.results[0]
            assert result.status == "completed"
            assert result.reason is not None
