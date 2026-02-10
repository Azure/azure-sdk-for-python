# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list evaluation and and eval runs
    for Groundedness evaluator using inline dataset content.

USAGE:
    python sample_groundedness.py

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
                        "context": {"type": "string"},
                        "query": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                        "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                        "tool_definitions": {
                            "anyOf": [
                                {"type": "string"},
                                {"type": "object"},
                                {"type": "array", "items": {"type": "object"}},
                            ]
                        },
                    },
                    "required": ["response"],
                },
                "include_sample_schema": True,
            }
        )

        testing_criteria = [
            {
                "type": "azure_ai_evaluator",
                "name": "groundedness",
                "evaluator_name": "builtin.groundedness",
                "initialization_parameters": {"deployment_name": f"{model_deployment_name}"},
                "data_mapping": {
                    "context": "{{item.context}}",
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                    "tool_definitions": "{{item.tool_definitions}}",
                },
            }
        ]

        print("Creating Evaluation")
        eval_object = client.evals.create(
            name="Test Groundedness Evaluator with inline data",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,  # type: ignore
        )
        print(f"Evaluation created")

        print("Get Evaluation by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)

        # Success example - response grounded in context
        success_context = (
            "France, a country in Western Europe, is known for its rich history and cultural heritage. "
            "The city of Paris, located in the northern part of the country, serves as its capital. "
            "Paris is renowned for its art, fashion, and landmarks such as the Eiffel Tower and the Louvre Museum."
        )
        success_response = "Paris is the capital of France."

        # Failure example - response not grounded in context
        failure_context = (
            "France, a country in Western Europe, is known for its rich history and cultural heritage. "
            "The city of Paris, located in the northern part of the country, serves as its capital. "
            "Paris is renowned for its art, fashion, and landmarks such as the Eiffel Tower and the Louvre Museum."
        )
        failure_response = "London is the capital of France and has a population of over 10 million people."

        # Simple example with query
        simple_query = "What is the population of Tokyo?"
        simple_context = "Tokyo, the capital of Japan, has a population of approximately 14 million people in the city proper and 38 million in the greater metropolitan area."
        simple_response = "According to the information provided, Tokyo has approximately 14 million people in the city proper and 38 million in the greater metropolitan area."

        # Complex example - conversation format with grounded response
        complex_context = "Weather service provides current weather information for any location."
        complex_response = [
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
                "content": [{"type": "tool_result", "tool_result": {"weather": "Rainy, 14°C"}}],
            },
            {
                "createdAt": "2025-03-26T17:27:42Z",
                "run_id": "run_zblZyGCNyx6aOYTadmaqM4QN",
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "The current weather in Seattle is rainy with a temperature of 14°C."}
                ],
            },
        ]

        complex_tool_definitions = [
            {
                "name": "fetch_weather",
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string", "description": "The location to fetch weather for."}},
                },
            }
        ]

        # Another complex example - conversation format with query but no tool calls
        query_conversation_context = "The company's employee handbook states that vacation days must be requested at least 2 weeks in advance and approved by your direct supervisor."
        query_conversation_query = [
            {
                "createdAt": "2025-03-26T17:30:00Z",
                "run_id": "run_ABC123DEF456",
                "role": "user",
                "content": [{"type": "text", "text": "What's the policy for requesting vacation days?"}],
            }
        ]
        query_conversation_response = [
            {
                "createdAt": "2025-03-26T17:30:05Z",
                "run_id": "run_ABC123DEF456",
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "According to the employee handbook, vacation days must be requested at least 2 weeks in advance and need approval from your direct supervisor.",
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
                        # Success example - grounded response
                        SourceFileContentContent(
                            item={
                                "context": success_context,
                                "response": success_response,
                                "query": None,
                                "tool_definitions": None,
                            }
                        ),
                        # Failure example - ungrounded response
                        SourceFileContentContent(
                            item={
                                "context": failure_context,
                                "response": failure_response,
                                "query": None,
                                "tool_definitions": None,
                            }
                        ),
                        # Simple example with query
                        SourceFileContentContent(
                            item={
                                "context": simple_context,
                                "query": simple_query,
                                "response": simple_response,
                                "tool_definitions": None,
                            }
                        ),
                        # Complex example - conversation format with grounded response
                        SourceFileContentContent(
                            item={
                                "context": complex_context,
                                "response": complex_response,
                                "query": None,
                                "tool_definitions": complex_tool_definitions,
                            }
                        ),
                        # Another complex example - conversation format with query but no tool calls
                        SourceFileContentContent(
                            item={
                                "context": query_conversation_context,
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
