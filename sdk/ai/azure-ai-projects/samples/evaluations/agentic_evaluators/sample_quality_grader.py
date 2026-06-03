# pylint: disable=line-too-long,useless-suppression,missing-function-docstring
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list evaluation and eval runs
    for the Quality Grader evaluator using inline dataset content.

    The Quality Grader evaluator assesses the quality of an AI assistant's response at the
    turn level, evaluating dimensions such as relevance, abstention, and answer completeness.
    When context is provided, it additionally evaluates groundedness and context coverage.

USAGE:
    python sample_quality_grader.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) FOUNDRY_MODEL_NAME - Required. The name of the model deployment to use for evaluation.
"""

import os
import time
from pprint import pprint
from dotenv import load_dotenv
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
from openai.types.eval_create_params import DataSourceConfigCustom
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import TestingCriterionAzureAIEvaluator

load_dotenv()


def main() -> None:  # pylint: disable=too-many-locals
    endpoint = os.environ[
        "FOUNDRY_PROJECT_ENDPOINT"
    ]  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
    model_deployment_name = os.environ.get("FOUNDRY_MODEL_NAME", "")  # Sample : gpt-4o-mini

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):
        data_source_config = DataSourceConfigCustom(
            type="custom",
            item_schema={
                "type": "object",
                "properties": {
                    "query": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                    "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                    "context": {"type": "string"},
                },
                "required": ["query", "response"],
            },
            include_sample_schema=True,
        )

        testing_criteria = [
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="quality_grader",
                evaluator_name="builtin.quality_grader",
                initialization_parameters={"deployment_name": f"{model_deployment_name}"},
                data_mapping={
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                    "context": "{{item.context}}",
                },
            )
        ]

        print("Creating Evaluation")
        eval_object = client.evals.create(
            name="Test Quality Grader Evaluator with inline data",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,  # type: ignore
        )
        print("Evaluation created")

        print("Get Evaluation by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)

        # Success example - relevant and complete response without context
        success_query = "What are the benefits of regular exercise?"
        success_response = (
            "Regular exercise offers numerous benefits including improved cardiovascular health, "
            "better weight management, enhanced mood through endorphin release, stronger muscles and bones, "
            "and reduced risk of chronic diseases such as diabetes and heart disease."
        )

        # Success example with context - grounded and relevant response
        success_context = (
            "The Eiffel Tower is a wrought-iron lattice tower located on the Champ de Mars in Paris, France. "
            "It was constructed from 1887 to 1889 as the centerpiece of the 1889 World's Fair. "
            "The tower is 330 metres tall and was the tallest man-made structure in the world until 1930."
        )
        success_query_with_context = "Tell me about the Eiffel Tower."
        success_response_with_context = (
            "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris. "
            "It was built between 1887 and 1889 for the 1889 World's Fair and stands 330 metres tall. "
            "It held the record as the tallest man-made structure until 1930."
        )

        # Failure example - irrelevant response
        failure_query = "How do I reset my password?"
        failure_response = "The weather today is sunny with a high of 75 degrees Fahrenheit."

        # Failure example with context - ungrounded response
        failure_context = (
            "Our company's return policy allows returns within 30 days of purchase with a valid receipt. "
            "Items must be in their original packaging and unused condition."
        )
        failure_query_with_context = "What is the return policy?"
        failure_response_with_context = (
            "You can return items within 90 days of purchase without a receipt, "
            "even if the item has been used or opened."
        )

        # Conversation format example
        conversation_query = [
            {
                "createdAt": "2025-04-10T10:00:00Z",
                "run_id": "run_qualityGraderExample001",
                "role": "user",
                "content": [{"type": "text", "text": "What is the capital of Japan?"}],
            }
        ]
        conversation_response = [
            {
                "createdAt": "2025-04-10T10:00:05Z",
                "run_id": "run_qualityGraderExample001",
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "The capital of Japan is Tokyo. It is the most populous metropolitan area in the world.",
                    }
                ],
            }
        ]

        print("Creating Eval Run with Inline Data")
        eval_run_object = client.evals.runs.create(
            eval_id=eval_object.id,
            name="inline_data_run",
            metadata={"team": "eval-exp", "scenario": "inline-data-v1"},
            data_source=CreateEvalJSONLRunDataSourceParam(
                type="jsonl",
                source=SourceFileContent(
                    type="file_content",
                    content=[
                        # Success example - relevant response without context
                        SourceFileContentContent(
                            item={
                                "query": success_query,
                                "response": success_response,
                                "context": None,
                            }
                        ),
                        # Success example with context - grounded and relevant response
                        SourceFileContentContent(
                            item={
                                "query": success_query_with_context,
                                "response": success_response_with_context,
                                "context": success_context,
                            }
                        ),
                        # Failure example - irrelevant response
                        SourceFileContentContent(
                            item={
                                "query": failure_query,
                                "response": failure_response,
                                "context": None,
                            }
                        ),
                        # Failure example with context - ungrounded response
                        SourceFileContentContent(
                            item={
                                "query": failure_query_with_context,
                                "response": failure_response_with_context,
                                "context": failure_context,
                            }
                        ),
                        # Conversation format example
                        SourceFileContentContent(
                            item={
                                "query": conversation_query,
                                "response": conversation_response,
                                "context": None,
                            }
                        ),
                    ],
                ),
            ),
        )

        print("Eval Run created")
        pprint(eval_run_object)

        print("Get Eval Run by Id")
        eval_run_response = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
        print("Eval Run Response:")
        pprint(eval_run_response)

        print("\n\n----Eval Run Output Items----\n\n")

        while True:
            run = client.evals.runs.retrieve(run_id=eval_run_response.id, eval_id=eval_object.id)
            if run.status in ("completed", "failed"):
                output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
                pprint(output_items)
                print(f"Eval Run Status: {run.status}")
                print(f"Eval Run Report URL: {run.report_url}")
                break
            time.sleep(5)
            print("Waiting for eval run to complete...")


if __name__ == "__main__":
    main()
