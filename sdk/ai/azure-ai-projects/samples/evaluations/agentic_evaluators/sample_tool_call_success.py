# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list evaluation and and eval runs
    for Tool Success evaluator using inline dataset content.

USAGE:
    python sample_tool_call_success.py

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
from openai.types.eval_create_params import DataSourceConfigCustom
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
                        "tool_definitions": {
                            "anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]
                        },
                        "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                    },
                    "required": ["response"],
                },
                "include_sample_schema": True,
            }
        )

        testing_criteria = [
            {
                "type": "azure_ai_evaluator",
                "name": "tool_call_success",
                "evaluator_name": "builtin.tool_call_success",
                "initialization_parameters": {"deployment_name": f"{model_deployment_name}"},
                "data_mapping": {"tool_definitions": "{{item.tool_definitions}}", "response": "{{item.response}}"},
            }
        ]

        print("Creating Evaluation")
        eval_object = client.evals.create(
            name="Test Tool Call Success Evaluator with inline data",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,  # type: ignore
        )
        print(f"Evaluation created")

        print("Get Evaluation by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)

        # Example 1: Successful tool execution
        response1 = [
            {
                "createdAt": "2025-03-26T17:27:35Z",
                "run_id": "run_ToolSuccess123",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_FileUpload456",
                        "name": "upload_file",
                        "arguments": {"file_path": "/documents/report.pdf", "destination": "cloud_storage"},
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:27:37Z",
                "run_id": "run_ToolSuccess123",
                "tool_call_id": "call_FileUpload456",
                "role": "tool",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": {
                            "status": "success",
                            "file_id": "file_12345",
                            "upload_url": "https://storage.example.com/file_12345",
                            "message": "File uploaded successfully",
                        },
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:27:39Z",
                "run_id": "run_ToolSuccess123",
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I've successfully uploaded your report.pdf to cloud storage. The file ID is file_12345 and it's available at the provided URL.",
                    }
                ],
            },
        ]
        tool_definitions1 = [
            {
                "name": "upload_file",
                "description": "Upload a file to cloud storage",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the file to upload"},
                        "destination": {"type": "string", "description": "Destination storage location"},
                    },
                },
            }
        ]

        # Example 2: Failed tool execution
        response2 = [
            {
                "createdAt": "2025-03-26T17:28:10Z",
                "run_id": "run_ToolFail789",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_DatabaseQuery101",
                        "name": "query_database",
                        "arguments": {"table": "users", "query": "SELECT * FROM users WHERE age > 25"},
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:28:12Z",
                "run_id": "run_ToolFail789",
                "tool_call_id": "call_DatabaseQuery101",
                "role": "tool",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": {
                            "status": "error",
                            "error_code": "DB_CONNECTION_FAILED",
                            "message": "Unable to connect to database. Connection timeout after 30 seconds.",
                        },
                    }
                ],
            },
            {
                "createdAt": "2025-03-26T17:28:14Z",
                "run_id": "run_ToolFail789",
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I encountered an error while trying to query the database. The connection timed out after 30 seconds. Please try again later or contact your database administrator.",
                    }
                ],
            },
        ]
        tool_definitions2 = [
            {
                "name": "query_database",
                "description": "Execute SQL queries on the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Database table name"},
                        "query": {"type": "string", "description": "SQL query to execute"},
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
                        # Example 1: Successful tool execution
                        SourceFileContentContent(item={"tool_definitions": tool_definitions1, "response": response1}),
                        # Example 2: Failed tool execution
                        SourceFileContentContent(item={"tool_definitions": tool_definitions2, "response": response2}),
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
