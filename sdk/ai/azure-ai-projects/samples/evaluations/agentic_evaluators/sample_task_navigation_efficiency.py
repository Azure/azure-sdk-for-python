# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list eval group and and eval runs
    for Task Navigation Efficiency evaluator using inline dataset content.

USAGE:
    python sample_task_navigation_efficiency.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
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
    endpoint = os.environ.get(
        "AZURE_AI_PROJECT_ENDPOINT", ""
    )  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>

    with DefaultAzureCredential() as credential:

        with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

            print("Creating an OpenAI client from the AI Project client")

            client = project_client.get_openai_client()

            data_source_config = {
                "type": "custom",
                "item_schema": {
                    "type": "object",
                    "properties": {"response": {"type": "array"}, "ground_truth": {"type": "array"}},
                    "required": ["response", "ground_truth"],
                },
                "include_sample_schema": True,
            }

            testing_criteria = [
                {
                    "type": "azure_ai_evaluator",
                    "name": "task_navigation_efficiency",
                    "evaluator_name": "builtin.task_navigation_efficiency",
                    "initialization_parameters": {
                        "matching_mode": "exact_match"  #  Can be "exact_match", "in_order_match", or "any_order_match"
                    },
                    "data_mapping": {"response": "{{item.response}}", "ground_truth": "{{item.ground_truth}}"},
                }
            ]

            print("Creating Eval Group")
            eval_object = client.evals.create(
                name="Test Task Navigation Efficiency Evaluator with inline data",
                data_source_config=data_source_config, # type: ignore
                testing_criteria=testing_criteria, # type: ignore
            )
            print(f"Eval Group created")

            print("Get Eval Group by Id")
            eval_object_response = client.evals.retrieve(eval_object.id)
            print("Eval Run Response:")
            pprint(eval_object_response)

            # simple inline data with response and ground truth without parameters
            simple_response = [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_call",
                            "tool_call_id": "call_1",
                            "name": "identify_tools_to_call",
                            "arguments": {},
                        }
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {"type": "tool_call", "tool_call_id": "call_2", "name": "call_tool_A", "arguments": {}}
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {"type": "tool_call", "tool_call_id": "call_3", "name": "call_tool_B", "arguments": {}}
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {"type": "tool_call", "tool_call_id": "call_4", "name": "response_synthesis", "arguments": {}}
                    ],
                },
            ]

            simple_ground_truth = ["identify_tools_to_call", "call_tool_A", "call_tool_B", "response_synthesis"]

            # Another example with parameters in tool calls
            response = [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_call",
                            "tool_call_id": "call_1",
                            "name": "search",
                            "arguments": {"query": "weather", "location": "NYC"},
                        }
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_call",
                            "tool_call_id": "call_2",
                            "name": "format_result",
                            "arguments": {"format": "json"},
                        }
                    ],
                },
            ]

            ground_truth = (
                ["search", "format_result"],
                {"search": {"query": "weather", "location": "NYC"}, "format_result": {"format": "json"}},
            )

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
                                item={"response": simple_response, "ground_truth": simple_ground_truth}
                            ),
                            SourceFileContentContent(item={"response": response, "ground_truth": ground_truth}),
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
