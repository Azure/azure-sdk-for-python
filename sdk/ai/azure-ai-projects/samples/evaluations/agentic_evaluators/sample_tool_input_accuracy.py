# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list evaluation and and eval runs
    for Tool Input Accuracy evaluator using inline dataset content.

USAGE:
    python sample_tool_input_accuracy.py

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
        print("Creating an OpenAI client from the AI Project client")

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
                    "required": ["query", "response", "tool_definitions"],
                },
                "include_sample_schema": True,
            }
        )

        testing_criteria = [
            {
                "type": "azure_ai_evaluator",
                "name": "tool_input_accuracy",
                "evaluator_name": "builtin.tool_input_accuracy",
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
            name="Test Tool Input Accuracy Evaluator with inline data",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,  # type: ignore
        )
        print(f"Evaluation created")

        print("Get Evaluation by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)

        # Success example - accurate tool inputs (string query, complex response)
        success_query = "Get the weather for Boston"
        success_response = [
            {
                "createdAt": "2025-03-26T17:27:35Z",
                "run_id": "run_ToolInputAccuracy123",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_WeatherBoston456",
                        "name": "get_weather",
                        "arguments": {"location": "Boston"},
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:27:37Z",
                "run_id": "run_ToolInputAccuracy123",
                "tool_call_id": "call_WeatherBoston456",
                "role": "tool",
                "content": [{"type": "tool_result", "tool_result": {"weather": "Sunny, 22°C"}}],
            },
            {
                "createdAt": "2025-03-26T17:27:39Z",
                "run_id": "run_ToolInputAccuracy123",
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "The current weather in Boston is sunny with a temperature of 22°C."}
                ],
            },
        ]
        success_tool_definitions = [
            {
                "name": "get_weather",
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string", "description": "The city name"}},
                },
            }
        ]

        # Failure example - inaccurate tool inputs (string query, complex response)
        failure_query = "Send an email to john@example.com with the meeting details"
        failure_response = [
            {
                "createdAt": "2025-03-26T17:28:10Z",
                "run_id": "run_ToolInputFail789",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_EmailFail101",
                        "name": "send_email",
                        "arguments": {"recipient": "john@example.com"},
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:28:12Z",
                "run_id": "run_ToolInputFail789",
                "tool_call_id": "call_EmailFail101",
                "role": "tool",
                "content": [
                    {"type": "tool_result", "tool_result": {"error": "Missing required fields: subject and body"}}
                ],
            },
            {
                "createdAt": "2025-03-26T17:28:14Z",
                "run_id": "run_ToolInputFail789",
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I encountered an error sending the email. Please provide the subject and message content.",
                    }
                ],
            },
        ]
        failure_tool_definitions = [
            {
                "name": "send_email",
                "description": "Send an email to specified recipient",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject line"},
                        "body": {"type": "string", "description": "Email message body"},
                    },
                },
            }
        ]

        # Complex example - accurate tool inputs (complex query, complex response)
        complex_query = [
            {
                "createdAt": "2025-03-26T17:29:00Z",
                "run_id": "run_ComplexToolInput321",
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Book a meeting room for Friday from 2 PM to 4 PM for the project review",
                    }
                ],
            }
        ]
        complex_response = [
            {
                "createdAt": "2025-03-26T17:29:05Z",
                "run_id": "run_ComplexToolInput321",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_BookRoom654",
                        "name": "book_meeting_room",
                        "arguments": {
                            "date": "2025-03-29",
                            "start_time": "14:00",
                            "end_time": "16:00",
                            "purpose": "project review",
                        },
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:29:07Z",
                "run_id": "run_ComplexToolInput321",
                "tool_call_id": "call_BookRoom654",
                "role": "tool",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": {"room_id": "Conference Room B", "confirmation": "Room booked successfully"},
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:29:09Z",
                "run_id": "run_ComplexToolInput321",
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I've successfully booked Conference Room B for Friday, March 29th from 2:00 PM to 4:00 PM for your project review.",
                    }
                ],
            },
        ]
        complex_tool_definitions = [
            {
                "name": "book_meeting_room",
                "description": "Book a meeting room for specified date and time",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                        "start_time": {"type": "string", "description": "Start time in HH:MM format"},
                        "end_time": {"type": "string", "description": "End time in HH:MM format"},
                        "purpose": {"type": "string", "description": "Meeting purpose"},
                    },
                },
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
                        # Success example - accurate tool inputs
                        SourceFileContentContent(
                            item={
                                "query": success_query,
                                "response": success_response,
                                "tool_definitions": success_tool_definitions,
                            }
                        ),
                        # Failure example - inaccurate tool inputs
                        SourceFileContentContent(
                            item={
                                "query": failure_query,
                                "response": failure_response,
                                "tool_definitions": failure_tool_definitions,
                            }
                        ),
                        # Complex example - conversation format with accurate tool inputs
                        SourceFileContentContent(
                            item={
                                "query": complex_query,
                                "response": complex_response,
                                "tool_definitions": complex_tool_definitions,
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
