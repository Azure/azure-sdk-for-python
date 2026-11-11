# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates the end-to-end workflow for
    running an evaluation using an endpoint-based evaluator with API Key authentication:

    1. Register an endpoint evaluator backed by an existing project connection
    2. Create an evaluation with the endpoint evaluator as testing criteria
    3. Run the evaluation with inline data
    4. Poll for results and display output

    Endpoint evaluators allow you to bring your own HTTP endpoint for evaluation. The service
    POSTs each evaluation row to your endpoint and expects a JSON response with a score and
    optional reasoning fields. Authentication is resolved server-side from a project
    connection.

    This sample uses endpoint contract schema version 0.0.2, which is recommended for new
    evaluators. With 0.0.2, the evaluator must define exactly one metric, of type "ordinal" or
    "continuous". For endpoints that still implement schema 0.0.1, see
    sample_endpoint_evaluator_schema_0_0_1.py.

    Your endpoint must accept POST requests with a JSON body like:
        {
          "schema_version": "0.0.2",
          "evaluator_name": "...",
          "evaluator_version": "...",
          "evaluation_target": {"type": "last_turn", "response_start_index": 1},
          "context": {"query": "...", "response": "...", "context": "..."},
          "messages": [
            {"role": "user", "content": [{"type": "text", "text": "..."}]},
            {"role": "assistant", "content": [{"type": "text", "text": "..."}]}
          ],
          "agent_definition": {"tool_definitions": []},
          "metadata": {"run_type": "dataset"}
        }
    The messages from response_start_index onward are the response to score. For
    conversation-level evaluators, evaluation_target is {"type": "conversation"}.

    And return a JSON response like:
        {
          "status": "completed",  // Valid values: "completed", "error", "skipped"
          "score": 4,             // Required when completed; within the metric's range
          "passed": true,         // Required when completed
          "reason": "Response is accurate and concise.",
          "properties": {"model_used": "gpt-4o"}
        }
    Omit "score" and "passed" when status is "error" or "skipped". Unknown fields are rejected.

USAGE:
    python sample_endpoint_evaluator_with_api_key.py

    Before running the sample:

    pip install "azure-ai-projects>=2.8.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) ENDPOINT_CONNECTION_NAME - Required. The name of the project connection to your scoring endpoint.

PREREQUISITES:
    - A project connection to your scoring endpoint that uses API key authentication. Its target
      is the endpoint URL, and it stores the endpoint's API key. The service sends the key in the
      ``api-key`` header.
    - A scoring endpoint that:
        * Accepts POST requests with a JSON body containing evaluation data
        * Authenticates requests using an API key
        * Returns a JSON response with a score and optional reasoning fields
"""

import os
import time

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    EndpointBasedEvaluatorDefinition,
    EndpointEvaluatorSchemaVersion,
    EvaluatorCategory,
    EvaluatorType,
    EvaluatorVersion,
    EvaluatorMetric,
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
connection_name = os.environ["ENDPOINT_CONNECTION_NAME"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):

    # ── Step 1: Register an endpoint-based evaluator ────────────────────
    # The evaluator references your project connection. The service
    # resolves the endpoint URL and API key credentials at evaluation time.
    print("[1/4] Registering endpoint-based evaluator with API Key auth...")

    evaluator = project_client.evaluators.create_version(
        name="my-endpoint-evaluator-apikey",
        evaluator_version=EvaluatorVersion(
            categories=[EvaluatorCategory.QUALITY],
            evaluator_type=EvaluatorType.CUSTOM,
            definition=EndpointBasedEvaluatorDefinition(
                connection_name=connection_name,
                schema_version=EndpointEvaluatorSchemaVersion.V0_0_2,
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
        # Endpoint evaluators are still in preview, so the service requires this opt-in header.
        headers={"Foundry-Features": "Evaluations=V1Preview"},
    )

    print(f"  Created evaluator: name={evaluator.name}, version={evaluator.version}")

    # ── Step 2: Create an evaluation ────────────────────────────────────
    print("[2/4] Creating evaluation...")

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

    # ── Step 3: Run the evaluation with inline data ─────────────────────
    print("[3/4] Running evaluation with inline data...")

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

    # ── Step 4: Poll for results ────────────────────────────────────────
    print("[4/4] Waiting for evaluation run to complete...")

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
    # The evaluator and evaluation are left in place so you can
    # inspect results in the Foundry portal. Uncomment the following to delete them:
    # project_client.evaluators.delete(name="my-endpoint-evaluator-apikey")
    # print("  Evaluator deleted: my-endpoint-evaluator-apikey")
    # client.evals.delete(eval_id=eval_object.id)
    # print(f"  Evaluation deleted: {eval_object.id}")
