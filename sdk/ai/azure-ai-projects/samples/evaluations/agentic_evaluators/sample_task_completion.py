# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list eval group and and eval runs
    for Task Completion evaluator using inline dataset content.

USAGE:
    python sample_task_completion.py

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


load_dotenv()


def main() -> None:
    endpoint = os.environ[
        "AZURE_AI_PROJECT_ENDPOINT"
    ]  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
    model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")  # Sample : gpt-4o-mini

    with (
        DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):

        data_source_config = {
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {
                    "query": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                    "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                    "tool_definitions": {
                        "anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]
                    },
                },
                "required": ["query", "response"],
            },
            "include_sample_schema": True,
        }

        testing_criteria = [
            {
                "type": "azure_ai_evaluator",
                "name": "task_completion",
                "evaluator_name": "builtin.task_completion",
                "initialization_parameters": {"deployment_name": f"{model_deployment_name}"},
                "data_mapping": {
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                    "tool_definitions": "{{item.tool_definitions}}",
                },
            }
        ]

        print("Creating Eval Group")
        eval_object = client.evals.create(
            name="Test Task Completion Evaluator with inline data",
            data_source_config=data_source_config,  # type: ignore
            testing_criteria=testing_criteria,  # type: ignore
        )
        print(f"Eval Group created")

        print("Get Eval Group by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)

        # Success example - task completed successfully
        success_query = "Book a flight from New York to Los Angeles for next Friday"
        success_response = "I've successfully booked your flight from New York (JFK) to Los Angeles (LAX) for Friday, March 29th. Your confirmation number is ABC123. The flight departs at 2:30 PM EST and arrives at 5:45 PM PST."

        # Failure example - task not completed
        failure_query = "Cancel my subscription and refund my payment"
        failure_response = "I understand you want to cancel your subscription. Here are some helpful articles about our cancellation policy and refund terms that you might find useful."

        # Complex example - conversation format with task completion
        complex_query = [
            {
                "createdAt": "2025-03-26T17:27:35Z",
                "run_id": "run_TaskCompletion123",
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "I need to transfer $500 from my checking account to my savings account",
                    }
                ],
            }
        ]
        complex_response = [
            {
                "createdAt": "2025-03-26T17:27:40Z",
                "run_id": "run_TaskCompletion123",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_TransferMoney456",
                        "name": "transfer_money",
                        "arguments": {"from_account": "checking", "to_account": "savings", "amount": 500},
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:27:42Z",
                "run_id": "run_TaskCompletion123",
                "tool_call_id": "call_TransferMoney456",
                "role": "tool",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": {
                            "status": "success",
                            "transaction_id": "TXN789",
                            "new_checking_balance": 2500.00,
                            "new_savings_balance": 8500.00,
                        },
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:27:45Z",
                "run_id": "run_TaskCompletion123",
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I've successfully transferred $500 from your checking account to your savings account. Transaction ID: TXN789. Your new checking balance is $2,500.00 and your savings balance is $8,500.00.",
                    }
                ],
            },
        ]

        complex_tool_definitions = [
            {
                "name": "transfer_money",
                "description": "Transfers money between user accounts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "from_account": {
                            "type": "string",
                            "description": "The source account type (checking, savings, etc.)",
                        },
                        "to_account": {
                            "type": "string",
                            "description": "The destination account type (checking, savings, etc.)",
                        },
                        "amount": {"type": "number", "description": "The amount to transfer"},
                    },
                },
            }
        ]

        # Another complex example - conversation format with query but no tool calls
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
                        # Success example - task completed
                        SourceFileContentContent(
                            item={"query": success_query, "response": success_response, "tool_definitions": None}
                        ),
                        # Failure example - task not completed
                        SourceFileContentContent(
                            item={"query": failure_query, "response": failure_response, "tool_definitions": None}
                        ),
                        # Complex example - conversation format with tool usage
                        SourceFileContentContent(
                            item={
                                "query": complex_query,
                                "response": complex_response,
                                "tool_definitions": complex_tool_definitions,
                            }
                        ),
                        # Another complex example - conversation format without tool calls
                        SourceFileContentContent(
                            item={
                                "query": query_conversation_query,
                                "response": query_conversation_response,
                                "tool_definitions": None,
                            }
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
