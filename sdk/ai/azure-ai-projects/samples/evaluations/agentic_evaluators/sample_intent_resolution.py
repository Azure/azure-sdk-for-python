# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list evaluation and and eval runs
    for Intent Resolution evaluator using inline dataset content.

USAGE:
    python sample_intent_resolution.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

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
                        "tool_definitions": {
                            "anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]
                        },
                    },
                    "required": ["query", "response"],
                },
                "include_sample_schema": True,
            }
        )

        testing_criteria = [
            {
                "type": "azure_ai_evaluator",
                "name": "intent_resolution",
                "evaluator_name": "builtin.intent_resolution",
                "initialization_parameters": {"deployment_name": f"{model_deployment_name}"},
                "data_mapping": {
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                    "tool_definitions": "{{item.tool_definitions}}",
                },
            }
        ]

        print("Creating Evaluation")
        eval_object = client.evals.create(
            name="Test Intent Resolution Evaluator with inline data",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,  # type: ignore
        )
        print(f"Evaluation created")

        print("Get Evaluation by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)

        # Success example - Intent is identified and understood and the response correctly resolves user intent
        success_query = "What are the opening hours of the Eiffel Tower?"
        success_response = "Opening hours of the Eiffel Tower are 9:00 AM to 11:00 PM."

        # Failure example - Even though intent is correctly identified, the response does not resolve the user intent
        failure_query = "What is the opening hours of the Eiffel Tower?"
        failure_response = (
            "Please check the official website for the up-to-date information on Eiffel Tower opening hours."
        )

        # Complex conversation example with tool calls
        complex_query = [
            {"role": "system", "content": "You are a friendly and helpful customer service agent."},
            {
                "createdAt": "2025-03-14T06:14:20Z",
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Hi, I need help with my order #123 status?",
                    }
                ],
            },
        ]

        complex_response = [
            {
                "createdAt": "2025-03-14T06:14:30Z",
                "run_id": "0",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "tool_call_001",
                        "name": "get_order",
                        "arguments": {"order_id": "123"},
                    }
                ],
            },
            {
                "createdAt": "2025-03-14T06:14:35Z",
                "run_id": "0",
                "tool_call_id": "tool_call_001",
                "role": "tool",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": '{ "order": { "id": "123", "status": "shipped", "delivery_date": "2025-03-15" } }',
                    }
                ],
            },
            {
                "createdAt": "2025-03-14T06:14:40Z",
                "run_id": "0",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "tool_call_002",
                        "name": "get_tracking",
                        "arguments": {"order_id": "123"},
                    }
                ],
            },
            {
                "createdAt": "2025-03-14T06:14:45Z",
                "run_id": "0",
                "tool_call_id": "tool_call_002",
                "role": "tool",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": '{ "tracking_number": "ABC123", "carrier": "UPS" }',
                    }
                ],
            },
            {
                "createdAt": "2025-03-14T06:14:50Z",
                "run_id": "0",
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "Your order #123 has been shipped and is expected to be delivered on March 15, 2025. The tracking number is ABC123 with UPS.",
                    }
                ],
            },
        ]

        # Tool definitions for the complex example
        tool_definitions = [
            {
                "name": "get_order",
                "description": "Get the details of a specific order.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string", "description": "The order ID to get the details for."}
                    },
                },
            },
            {
                "name": "get_tracking",
                "description": "Get tracking information for an order.",
                "parameters": {
                    "type": "object",
                    "properties": {"order_id": {"type": "string", "description": "The order ID to get tracking for."}},
                },
            },
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
                        # Example 1: Success case - simple string query and response
                        SourceFileContentContent(item={"query": success_query, "response": success_response}),
                        # Example 2: Failure case - simple string query and response
                        SourceFileContentContent(item={"query": failure_query, "response": failure_response}),
                        # Example 3: Complex conversation with tool calls and tool definitions
                        SourceFileContentContent(
                            item={
                                "query": complex_query,
                                "response": complex_response,
                                "tool_definitions": tool_definitions,
                            }
                        ),
                        # Example 4: Complex conversation without tool definitions
                        SourceFileContentContent(item={"query": complex_query, "response": complex_response}),
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
