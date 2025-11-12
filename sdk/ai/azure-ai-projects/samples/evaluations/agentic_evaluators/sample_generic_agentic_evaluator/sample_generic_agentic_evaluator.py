# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list eval group and and eval runs
    for Any agentic evaluator using inline dataset content.

USAGE:
    python sample_generic_agentic_evaluator.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - Required. The name of the model deployment to use for evaluation.
"""

from dotenv import load_dotenv
import os
from samples.evaluation.sample_agentic_evaluators.sample_generic_agentic_evaluator.agent_utils import run_evaluator
from schema_mappings import evaluator_to_data_source_config, evaluator_to_data_mapping
from openai.types.evals.create_eval_jsonl_run_data_source_param import SourceFileContentContent


load_dotenv()


def _get_evaluator_initialization_parameters(evaluator_name: str) -> dict[str, str]:
    if evaluator_name == "task_navigation_efficiency":
        return {"matching_mode": "exact_match"}  #  Can be "exact_match", "in_order_match", or "any_order_match"
    else:
        model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")  # Sample : gpt-4o-mini
        return {"deployment_name": model_deployment_name}


def _get_evaluation_contents() -> list[SourceFileContentContent]:
    # Sample inline data
    # Change this to add more examples for evaluation
    # Use the appropriate schema based on the evaluator being used
    success_query = "What is the capital of France?"
    success_response = "The capital of France is Paris."

    evaluation_contents = [SourceFileContentContent(item={"query": success_query, "response": success_response})]

    return evaluation_contents


def main() -> None:
    evaluator_name = "coherence"  # Change to any agentic evaluator name like "relevance", "response_completeness", "task_navigation_efficiency"
    data_source_config = evaluator_to_data_source_config[evaluator_name]
    initialization_parameters = _get_evaluator_initialization_parameters(evaluator_name)
    data_mapping = evaluator_to_data_mapping[evaluator_name]
    evaluation_contents = _get_evaluation_contents()

    run_evaluator(evaluator_name, evaluation_contents, data_source_config, initialization_parameters, data_mapping)


if __name__ == "__main__":
    main()
