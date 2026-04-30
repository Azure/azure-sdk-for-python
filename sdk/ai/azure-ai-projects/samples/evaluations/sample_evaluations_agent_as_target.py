# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to run Azure AI Evaluations against
    a hosted agent using the azure_ai_target_completions data source. The evaluation service
    invokes the agent live for each test query, collects responses, and runs built-in quality
    and safety evaluators against them.

    This is different from trace evaluations (sample_evaluations_builtin_with_traces.py) which
    evaluate historical agent traces. This sample evaluates agents live.

USAGE:
    python sample_evaluations_agent_as_target.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) FOUNDRY_MODEL_NAME - Required. The Azure OpenAI deployment name to use as the judge model for
       built-in evaluators.
    3) AGENT_NAME - Required. The hosted agent name to evaluate.
    4) AGENT_VERSION - Optional. The agent version to evaluate. Defaults to "1".
"""

import os
import time
from datetime import datetime
from pprint import pprint

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import TestingCriterionAzureAIEvaluator
from azure.identity import DefaultAzureCredential

load_dotenv()


endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ["AGENT_NAME"]
agent_version = os.environ.get("AGENT_VERSION", "1")

# Sample test queries. Replace with queries appropriate for your agent.
INPUT_QUERIES = [
    {
        "item": {
            "query": "Hello, what can you help me with?",
        }
    },
    {
        "item": {
            "query": "Can you give me a brief summary of your capabilities?",
        }
    },
]


def _build_evaluator_config(
    name: str,
    evaluator_name: str,
    response_mapping: str,
) -> TestingCriterionAzureAIEvaluator:
    """Create a standard Azure AI evaluator configuration block.

    :param name: Display name for this testing criterion.
    :type name: str
    :param evaluator_name: Built-in evaluator identifier.
    :type evaluator_name: str
    :param response_mapping: Response mapping expression used by the evaluator.
    :type response_mapping: str
    :return: Evaluator configuration used in the evaluation group.
    :rtype: ~azure.ai.projects.models.TestingCriterionAzureAIEvaluator
    """
    return TestingCriterionAzureAIEvaluator(
        type="azure_ai_evaluator",
        name=name,
        evaluator_name=evaluator_name,
        data_mapping={
            "query": "{{item.query}}",
            "response": response_mapping,
            "tool_definitions": "{{sample.tool_definitions}}",
        },
        initialization_parameters={
            "deployment_name": model_deployment_name,
        },
    )


def main() -> None:
    testing_criteria = [
        _build_evaluator_config(
            name="intent_resolution",
            evaluator_name="builtin.intent_resolution",
            response_mapping="{{sample.output_text}}",
        ),
        _build_evaluator_config(
            name="task_adherence",
            evaluator_name="builtin.task_adherence",
            response_mapping="{{sample.output_items}}",
        ),
    ]

    data_source_config = {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "context": {"type": "string"},
                "ground_truth": {"type": "string"},
            },
            "required": ["query"],
        },
        "include_sample_schema": True,
    }

    input_messages = {
        "type": "template",
        "template": [
            {
                "type": "message",
                "role": "user",
                "content": {
                    "type": "input_text",
                    "text": "{{item.query}}",
                },
            }
        ],
    }

    print(f"Agent: {agent_name} v{agent_version}")
    print(f"Evaluators: {len(testing_criteria)}")
    print(f"Queries: {len(INPUT_QUERIES)}")

    with DefaultAzureCredential() as credential:
        with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:
            client = project_client.get_openai_client()

            print("\nCreating evaluation")
            eval_name = f"Hosted Agent Eval - {agent_name} - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            eval_object = client.evals.create(
                name=eval_name,
                data_source_config=data_source_config,  # type: ignore
                testing_criteria=testing_criteria,  # type: ignore
            )
            print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

            print("\nGet Evaluation by Id")
            eval_object_response = client.evals.retrieve(eval_object.id)
            print("Evaluation Response:")
            pprint(eval_object_response)

            print("\nCreating Eval Run")
            data_source = {
                "type": "azure_ai_target_completions",
                "source": {
                    "type": "file_content",
                    "content": INPUT_QUERIES,
                },
                "input_messages": input_messages,
                "target": {
                    "type": "azure_ai_agent",
                    "name": agent_name,
                    "version": agent_version,
                },
            }
            run_name = f"Run - {agent_name} - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            eval_run_object = client.evals.runs.create(
                eval_id=eval_object.id,
                name=run_name,
                data_source=data_source,  # type: ignore
            )
            print("Eval Run created")
            pprint(eval_run_object)

            print("\nMonitoring Eval Run status...")
            while True:
                run = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
                print(f"Status: {run.status}")

                if run.status in {"completed", "failed", "canceled"}:
                    print("\nEval Run finished!")
                    print("Final Eval Run Response:")
                    pprint(run)
                    break

                time.sleep(5)
                print("Waiting for eval run to complete...")

            client.evals.delete(eval_id=eval_object.id)
            print("Evaluation deleted")


if __name__ == "__main__":
    main()
