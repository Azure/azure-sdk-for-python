# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list eval group and and eval runs
    for Tool Selection evaluator using inline dataset content.

USAGE:
    python sample_tool_selection.py

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
                    "tool_calls": {"anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]},
                    "tool_definitions": {
                        "anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]
                    },
                },
                "required": ["query", "response", "tool_definitions"],
            },
            "include_sample_schema": True,
        }

        testing_criteria = [
            {
                "type": "azure_ai_evaluator",
                "name": "tool_selection",
                "evaluator_name": "builtin.tool_selection",
                "initialization_parameters": {"deployment_name": f"{model_deployment_name}"},
                "data_mapping": {
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                    "tool_calls": "{{item.tool_calls}}",
                    "tool_definitions": "{{item.tool_definitions}}",
                },
            }
        ]

        print("Creating Eval Group")
        eval_object = client.evals.create(
            name="Test Tool Selection Evaluator with inline data",
            data_source_config=data_source_config,  # type: ignore
            testing_criteria=testing_criteria,  # type: ignore
        )
        print(f"Eval Group created")

        print("Get Eval Group by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)

        # Example: Conversation format
        query = "Can you send me an email with weather information for Seattle?"
        response = [
            {
                "createdAt": "2025-03-26T17:27:35Z",
                "run_id": "run_zblZyGCNyx6aOYTadmaqM4QN",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_CUdbkBfvVBla2YP3p24uhElJ",
                        "name": "fetch_weather",
                        "arguments": {"location": "Seattle"},
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:27:37Z",
                "run_id": "run_zblZyGCNyx6aOYTadmaqM4QN",
                "tool_call_id": "call_CUdbkBfvVBla2YP3p24uhElJ",
                "role": "tool",
                "content": [{"type": "tool_result", "tool_result": {"weather": "Rainy, 14\u00b0C"}}],
            },
            {
                "createdAt": "2025-03-26T17:27:38Z",
                "run_id": "run_zblZyGCNyx6aOYTadmaqM4QN",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_iq9RuPxqzykebvACgX8pqRW2",
                        "name": "send_email",
                        "arguments": {
                            "recipient": "your_email@example.com",
                            "subject": "Weather Information for Seattle",
                            "body": "The current weather in Seattle is rainy with a temperature of 14\u00b0C.",
                        },
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:27:41Z",
                "run_id": "run_zblZyGCNyx6aOYTadmaqM4QN",
                "tool_call_id": "call_iq9RuPxqzykebvACgX8pqRW2",
                "role": "tool",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": {"message": "Email successfully sent to your_email@example.com."},
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:27:42Z",
                "run_id": "run_zblZyGCNyx6aOYTadmaqM4QN",
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I have successfully sent you an email with the weather information for Seattle. The current weather is rainy with a temperature of 14\u00b0C.",
                    }
                ],
            },
        ]

        tool_definitions = [
            {
                "name": "fetch_weather",
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to fetch weather for."}
                    },
                },
            },
            {
                "name": "send_email",
                "description": "Sends an email with the specified subject and body to the recipient.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string", "description": "Email address of the recipient."},
                        "subject": {"type": "string", "description": "Subject of the email."},
                        "body": {"type": "string", "description": "Body content of the email."},
                    },
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
                        SourceFileContentContent(
                            item={
                                "query": query,
                                "response": response,
                                "tool_calls": None,
                                "tool_definitions": tool_definitions,
                            }
                        )
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
