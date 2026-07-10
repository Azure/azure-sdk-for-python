# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create and run a synthetic data evaluation
    against a Foundry agent using the synchronous AIProjectClient.

    Synthetic data evaluation generates test queries based on a prompt you provide,
    sends them to a Foundry agent, and evaluates the responses — no pre-existing
    test dataset required. The generated queries are stored as a dataset in your
    project for reuse.

    For evaluating a deployed model instead of an agent, see
    sample_synthetic_data_model_evaluation.py.

    This feature is currently in preview.

USAGE:
    python sample_synthetic_data_agent_evaluation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) FOUNDRY_MODEL_NAME - Required. The name of the model deployment to use for generating
       synthetic data and for AI-assisted evaluators.
    3) FOUNDRY_AGENT_NAME - Required. The name of the Foundry agent to evaluate.
"""

import os
import time
from pprint import pprint
from typing import Union

from dotenv import load_dotenv
from openai.types.evals.run_create_response import RunCreateResponse
from openai.types.evals.run_retrieve_response import RunRetrieveResponse

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AzureAIDataSourceConfig, TestingCriterionAzureAIEvaluator, PromptAgentDefinition

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ["FOUNDRY_AGENT_NAME"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):
    # Create (or update) an agent version to evaluate
    agent = project_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model_deployment_name,
            instructions="You are a helpful customer service agent. Be empathetic and solution-oriented.",
        ),
    )
    print(f"Agent created (name: {agent.name}, version: {agent.version})")

    # Use the azure_ai_source data source config with the synthetic_data_gen_preview scenario.
    # The schema is inferred from the service — no custom item_schema is needed.
    data_source_config = AzureAIDataSourceConfig(type="azure_ai_source", scenario="synthetic_data_gen_preview")

    # Define testing criteria using builtin evaluators.
    # {{item.query}} references the synthetically generated query.
    # {{sample.output_text}} references the agent's plain text response.
    testing_criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="coherence",
            evaluator_name="builtin.coherence",
            initialization_parameters={
                "deployment_name": model_deployment_name,
            },
            data_mapping={
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="violence",
            evaluator_name="builtin.violence",
            data_mapping={
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        ),
    ]

    print("Creating evaluation for synthetic data generation")
    eval_object = client.evals.create(
        name="Synthetic Data Evaluation",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    # Configure the synthetic data generation data source with an agent target.
    # The service generates queries based on the prompt, sends them to the agent,
    # and evaluates the responses.
    #
    # You can guide query generation in two ways:
    #   - "prompt": A text description of the queries to generate (used below).
    #   - "reference_files": A list of dataset asset IDs (uploaded via the datasets API)
    #     in the format of 'azureai://accounts/<account-name>/projects/<project-name>/data/<dataset-name>/versions/<version-no>'
    #     whose content the service uses as context for generating queries.
    # You can use either or both together.
    data_source = {
        "type": "azure_ai_synthetic_data_gen_preview",
        "item_generation_params": {
            "type": "synthetic_data_gen_preview",
            "samples_count": 5,
            "prompt": "Generate customer service questions about returning defective products",
            # "reference_files": ["<file-id-1>", "<file-id-2>"],
            "model_deployment_name": model_deployment_name,
            "output_dataset_name": "synthetic-eval-dataset",
        },
        "target": {
            "type": "azure_ai_agent",
            "name": agent.name,
            "version": agent.version,
        },
    }

    eval_run: Union[RunCreateResponse, RunRetrieveResponse] = client.evals.runs.create(
        eval_id=eval_object.id,
        name="synthetic-data-evaluation-run",
        data_source=data_source,  # type: ignore
    )
    print(f"Evaluation run created (id: {eval_run.id})")

    while eval_run.status not in ["completed", "failed"]:
        eval_run = client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_object.id)
        print(f"Waiting for eval run to complete... current status: {eval_run.status}")
        time.sleep(5)

    if eval_run.status == "completed":
        print("\n✓ Evaluation run completed successfully!")
        print(f"Result Counts: {eval_run.result_counts}")

        output_items = list(client.evals.runs.output_items.list(run_id=eval_run.id, eval_id=eval_object.id))
        print(f"\nOUTPUT ITEMS (Total: {len(output_items)})")
        print(f"{'-'*60}")
        pprint(output_items)
        print(f"{'-'*60}")

        print(f"\nEval Run Report URL: {eval_run.report_url}")

        # The synthetic data generation run stores the generated queries as a dataset.
        # Retrieve the output dataset ID from the run's data_source for reuse.
        output_dataset_id = getattr(eval_run.data_source, "item_generation_params", {}).get("output_dataset_id")
        if output_dataset_id:
            print(f"Output Dataset ID (for reuse): {output_dataset_id}")
    else:
        print("\n✗ Evaluation run failed.")

    client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")
