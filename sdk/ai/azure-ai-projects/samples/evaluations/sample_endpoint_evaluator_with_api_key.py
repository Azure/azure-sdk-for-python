# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates the end-to-end workflow for
    running an evaluation using an endpoint-based evaluator with API Key authentication:

    1. Create a workspace connection with API Key credentials
    2. Register an endpoint evaluator backed by the connection
    3. Create an evaluation with the endpoint evaluator as testing criteria
    4. Run the evaluation with inline data
    5. Poll for results and display output

    Endpoint evaluators allow you to bring your own HTTP endpoint for evaluation. The service
    POSTs each evaluation row to your endpoint and expects a JSON response with label/score
    and optional reasoning fields. Authentication is resolved server-side from a workspace
    connection.

    Your endpoint must accept POST requests with a JSON body like:
        {
          "schema_version": "0.0.1",
          "evaluator_name": "...",
          "evaluator_version": "...",
          "evaluation_level": "turn",
          "data": {
            "item": {"query": "...", "context": "..."},
            "sample": {"response": "..."}
          }
        }
    And return a JSON response like:
        {
          "schema_version": "0.0.1",
          "score": 0.85,
          "reason": "Response is accurate and concise.",
          "status": "Completed",  // Valid values: "Completed", "Error", "Skipped"
          "properties": {"model_used": "gpt-4o", "custom_flag": true},
          "threshold": null,
          "passed": true
        }

USAGE:
    python sample_endpoint_evaluator_with_api_key.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" azure-mgmt-cognitiveservices python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) AZURE_SUBSCRIPTION_ID - Required. The Azure subscription ID containing your project.
    3) AZURE_RESOURCE_GROUP - Required. The resource group containing your Azure AI account.
    4) ENDPOINT_URL - Required. The URL of your scoring endpoint
       (e.g., https://my-scoring-endpoint.azurewebsites.net/api/evaluate).
    5) ENDPOINT_API_KEY - Required. The API key for authenticating with your scoring endpoint.

PREREQUISITES:
    - A scoring endpoint that:
        * Accepts POST requests with a JSON body containing evaluation data
        * Authenticates requests using an API key (via the ``api-key`` header)
        * Returns a JSON response with label/score and optional reasoning fields
"""

import os
import time
from urllib.parse import urlparse

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    EndpointBasedEvaluatorDefinition,
    EvaluatorCategory,
    EvaluatorType,
    EvaluatorVersion,
    EvaluatorMetric,
)
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import (
    ConnectionPropertiesV2BasicResource,
    ApiKeyAuthConnectionProperties,
    ConnectionApiKey,
)

from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
from openai.types.eval_create_params import DataSourceConfigCustom

from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group = os.environ["AZURE_RESOURCE_GROUP"]
endpoint_url = os.environ["ENDPOINT_URL"]
endpoint_api_key = os.environ["ENDPOINT_API_KEY"]

# Derive account name from the project endpoint URL
# e.g., https://accountname.services.ai.azure.com/api/projects/default -> "accountname"
hostname = urlparse(endpoint).hostname
if not hostname:
    raise ValueError(f"Could not parse hostname from endpoint: {endpoint}")
account_name = hostname.split(".")[0]
connection_name = "my-endpoint-apikey-connection"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):

    # ── Step 1: Create a workspace connection with API Key auth ─────────
    # The connection stores the endpoint URL and API key credentials. At evaluation
    # time, the service resolves the connection and sends the API key in the request
    # header to your endpoint.
    # Note: create is idempotent — it creates or updates the connection if it already exists.
    print("[1/5] Creating workspace connection with API Key auth...")

    mgmt_client = CognitiveServicesManagementClient(
        credential=credential,
        subscription_id=subscription_id,
    )
    connection = ConnectionPropertiesV2BasicResource(
        properties=ApiKeyAuthConnectionProperties(
            category="ApiKey",
            target=endpoint_url,
            credentials=ConnectionApiKey(key=endpoint_api_key),
        ),
    )
    mgmt_client.account_connections.create(
        resource_group_name=resource_group,
        account_name=account_name,
        connection_name=connection_name,
        connection=connection,
    )
    print(f"  Connection created: {connection_name}")

    # ── Step 2: Register an endpoint-based evaluator ────────────────────
    # The evaluator references the workspace connection created above. The service
    # resolves the endpoint URL and API key credentials at evaluation time.
    print("[2/5] Registering endpoint-based evaluator with API Key auth...")

    evaluator = project_client.beta.evaluators.create_version(
        name="my-endpoint-evaluator-apikey",
        evaluator_version=EvaluatorVersion(
            categories=[EvaluatorCategory.QUALITY],
            evaluator_type=EvaluatorType.CUSTOM,
            definition=EndpointBasedEvaluatorDefinition(
                connection_name=connection_name,
                metrics={
                    "score": EvaluatorMetric(
                        type="ordinal",
                        min_value=1,
                        max_value=5,
                    )
                },
            ),
            display_name="Endpoint Evaluator (API Key)",
            description="Custom scoring endpoint authenticated with an API key",
        ),
    )

    print(f"  Created evaluator: name={evaluator.name}, version={evaluator.version}")

    # ── Step 3: Create an evaluation ────────────────────────────────────
    print("[3/5] Creating evaluation...")

    data_source_config = DataSourceConfigCustom(
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

    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "endpoint_eval_apikey",
            "evaluator_name": "my-endpoint-evaluator-apikey",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
                "context": "{{item.context}}",
            },
        }
    ]

    eval_object = client.evals.create(
        name="endpoint-evaluator-apikey-test",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,  # type: ignore
    )

    print(f"  Evaluation created: id={eval_object.id}")

    # ── Step 4: Run the evaluation with inline data ─────────────────────
    print("[4/5] Running evaluation with inline data...")

    eval_run = client.evals.runs.create(
        eval_id=eval_object.id,
        name="endpoint-apikey-run",
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileContent(
                type="file_content",
                content=[
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
                    SourceFileContentContent(
                        item={
                            "query": "Explain quantum computing",
                            "response": "Quantum computing leverages quantum mechanical phenomena like superposition and entanglement to process information.",
                            "context": "Complex scientific concept explanation",
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "query": "What are some tips for staying healthy?",
                            "response": "To stay healthy, focus on regular exercise, a balanced diet, adequate sleep, and stress management.",
                            "context": "Health and wellness advice",
                        }
                    ),
                ],
            ),
        ),
    )

    print(f"  Eval run created: id={eval_run.id}")

    # ── Step 5: Poll for results ────────────────────────────────────────
    print("[5/5] Waiting for evaluation run to complete...")

    while True:
        run = client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_object.id)
        if run.status in ("completed", "failed"):
            print(f"  Run status: {run.status}")
            output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
            pprint(output_items)
            print(f"  Report URL: {run.report_url}")
            break
        time.sleep(5)
        print(f"  Status: {run.status} — polling again...")

    # ── Cleanup ────────────────────────────────────────────────────────
    # The connection, evaluator, and evaluation are left in place so you can
    # inspect results in the Foundry portal. Uncomment the following to delete them:
    # mgmt_client.account_connections.delete(
    #     resource_group_name=resource_group,
    #     account_name=account_name,
    #     connection_name=connection_name,
    # )
    # print(f"  Connection deleted: {connection_name}")
    # project_client.beta.evaluators.delete(name="my-endpoint-evaluator-apikey")
    # print("  Evaluator deleted: my-endpoint-evaluator-apikey")
    # client.evals.delete(eval_id=eval_object.id)
    # print(f"  Evaluation deleted: {eval_object.id}")
