# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list evaluation and and eval runs
    for Relevance evaluator using inline dataset content.

USAGE:
    python sample_relevance.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - Required. The name of the model deployment to use for evaluation.
"""

from dotenv import load_dotenv
import os
import json
import time
from pprint import pprint

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
from openai.types.eval_create_params import DataSourceConfigCustom


load_dotenv()


def main() -> None:
    endpoint = os.environ[
        "AZURE_AI_PROJECT_ENDPOINT"
    ]  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
    model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")  # Sample : gpt-4o-mini

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):

        data_source_config = DataSourceConfigCustom(
            {
                "type": "custom",
                "item_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                        "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                    },
                    "required": ["query", "response"],
                },
                "include_sample_schema": True,
            }
        )

        testing_criteria = [
            {
                "type": "azure_ai_evaluator",
                "name": "relevance",
                "evaluator_name": "builtin.relevance",
                "initialization_parameters": {"deployment_name": f"{model_deployment_name}"},
                "data_mapping": {"query": "{{item.query}}", "response": "{{item.response}}"},
            }
        ]

        print("Creating Evaluation")
        eval_object = client.evals.create(
            name="Test Relevance Evaluator with inline data",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,  # type: ignore
        )
        print(f"Evaluation created")

        print("Get Evaluation by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)

        # Success example - relevant response
        success_query = "What is the capital of Japan?"
        success_response = "The capital of Japan is Tokyo."

        # Failure example - irrelevant response
        failure_query = "What is the capital of Japan?"
        failure_response = "Japan is known for its beautiful cherry blossoms and advanced technology. The country has a rich cultural heritage and is famous for sushi and anime."

        # Conversation example
        query_conversation_query = [
            {
                "createdAt": "2025-03-26T17:30:00Z",
                "run_id": "run_SimpleTask789",
                "role": "user",
                "content": [{"type": "text", "text": "Please calculate 15% tip on a $80 dinner bill"}],
            }
        ]
        query_conversation_response = [
            {
                "createdAt": "2025-03-26T17:30:05Z",
                "run_id": "run_SimpleTask789",
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "The 15% tip on an $80 dinner bill is $12.00. Your total bill including tip would be $92.00.",
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
                        # Success example - relevant response
                        SourceFileContentContent(item={"query": success_query, "response": success_response}),
                        # Failure example - irrelevant response
                        SourceFileContentContent(item={"query": failure_query, "response": failure_response}),
                        # Conversation example
                        SourceFileContentContent(
                            item={"query": query_conversation_query, "response": query_conversation_response}
                        ),
                    ],
                ),
            ),
        )

        print(f"Eval Run created")
        pprint(eval_run_object)

        print("Get Eval Run by Id")
        eval_run_response = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
        print("Eval Run Response:")
        pprint(eval_run_response)

        print("\n\n----Eval Run Output Items----\n\n")

        while True:
            run = client.evals.runs.retrieve(run_id=eval_run_response.id, eval_id=eval_object.id)
            if run.status == "completed" or run.status == "failed":
                output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
                pprint(output_items)
                print(f"Eval Run Status: {run.status}")
                print(f"Eval Run Report URL: {run.report_url}")
                break
            time.sleep(5)
            print("Waiting for eval run to complete...")


if __name__ == "__main__":
    main()
