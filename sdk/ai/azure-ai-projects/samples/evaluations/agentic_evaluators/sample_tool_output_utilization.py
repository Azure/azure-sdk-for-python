# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list eval group and and eval runs
    for Tool Output Utilization evaluator using inline dataset content.

USAGE:
    python sample_tool_output_utilization.py

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

    with DefaultAzureCredential() as credential:
        with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:
            print("Creating an OpenAI client from the AI Project client")

            client = project_client.get_openai_client()

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
                    "name": "tool_output_utilization",
                    "evaluator_name": "builtin.tool_output_utilization",
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
                name="Test Tool Output Utilization Evaluator with inline data",
                data_source_config=data_source_config,
                testing_criteria=testing_criteria,  # type: ignore
            )
            print(f"Eval Group created")

            print("Get Eval Group by Id")
            eval_object_response = client.evals.retrieve(eval_object.id)
            print("Eval Run Response:")
            pprint(eval_object_response)

            # Example 1: Good utilization - uses tool output effectively
            query1 = [
                {
                    "createdAt": "2025-03-26T17:27:30Z",
                    "run_id": "run_ToolOutput123",
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What's the weather like in Paris and should I bring an umbrella?"}
                    ],
                }
            ]
            response1 = [
                {
                    "createdAt": "2025-03-26T17:27:35Z",
                    "run_id": "run_ToolOutput123",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_call",
                            "tool_call_id": "call_WeatherParis456",
                            "name": "get_weather",
                            "arguments": {"location": "Paris"},
                        }
                    ],
                },
                {
                    "createdAt": "2025-03-26T17:27:37Z",
                    "run_id": "run_ToolOutput123",
                    "tool_call_id": "call_WeatherParis456",
                    "role": "tool",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_result": {
                                "weather": "Rainy, 16°C",
                                "humidity": "85%",
                                "precipitation": "Heavy rain expected",
                            },
                        }
                    ],
                },
                {
                    "createdAt": "2025-03-26T17:27:39Z",
                    "run_id": "run_ToolOutput123",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "The weather in Paris is currently rainy with a temperature of 16°C and high humidity at 85%. Heavy rain is expected, so yes, you should definitely bring an umbrella!",
                        }
                    ],
                },
            ]
            tool_definitions1 = [
                {
                    "name": "get_weather",
                    "description": "Get detailed weather information for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string", "description": "The city name"}},
                    },
                }
            ]

            # Example 2: Poor utilization - ignores tool output
            query2 = [
                {
                    "createdAt": "2025-03-26T17:28:00Z",
                    "run_id": "run_ToolOutputPoor789",
                    "role": "user",
                    "content": [{"type": "text", "text": "What's the current stock price of AAPL and should I buy?"}],
                }
            ]
            response2 = [
                {
                    "createdAt": "2025-03-26T17:28:05Z",
                    "run_id": "run_ToolOutputPoor789",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_call",
                            "tool_call_id": "call_StockPrice101",
                            "name": "get_stock_price",
                            "arguments": {"symbol": "AAPL"},
                        }
                    ],
                },
                {
                    "createdAt": "2025-03-26T17:28:07Z",
                    "run_id": "run_ToolOutputPoor789",
                    "tool_call_id": "call_StockPrice101",
                    "role": "tool",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_result": {
                                "price": "$190.50",
                                "change": "+2.5%",
                                "volume": "50M",
                                "market_cap": "$2.9T",
                            },
                        }
                    ],
                },
                {
                    "createdAt": "2025-03-26T17:28:09Z",
                    "run_id": "run_ToolOutputPoor789",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "I can't provide investment advice. Please consult with a financial advisor for investment decisions.",
                        }
                    ],
                },
            ]
            tool_definitions2 = [
                {
                    "name": "get_stock_price",
                    "description": "Get current stock price and market data",
                    "parameters": {
                        "type": "object",
                        "properties": {"symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL)"}},
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
                            # Example 1: Good tool output utilization
                            SourceFileContentContent(
                                item={"query": query1, "response": response1, "tool_definitions": tool_definitions1}
                            ),
                            # Example 2: Poor tool output utilization
                            SourceFileContentContent(
                                item={"query": query2, "response": response2, "tool_definitions": tool_definitions2}
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
