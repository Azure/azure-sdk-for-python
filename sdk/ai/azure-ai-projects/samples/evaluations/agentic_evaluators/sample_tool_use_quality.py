# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Evaluate single-turn and multi-turn tool use using builtin.tool_use_quality.
    Single-turn data uses query and response; multi-turn data keeps all messages
    in one row. Both include tool_definitions. The composite evaluator scores
    tool call accuracy, success, input accuracy, output utilization, and selection.

USAGE:
    python sample_tool_use_quality.py

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT - The Foundry project endpoint.
    2) FOUNDRY_MODEL_NAME - The model deployment used by the evaluator.
"""

import os
import time
from pprint import pprint

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import TestingCriterionAzureAIEvaluator
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from openai.types.eval_create_params import DataSourceConfigCustom
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)

load_dotenv()


def main() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]

    tool_definitions = [
        {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        }
    ]

    # single-turn example
    query = [
        {"role": "user", "content": [{"type": "text", "text": "What's the weather in Seattle?"}]},
    ]
    response = [
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_call",
                    "tool_call_id": "call_weather_1",
                    "name": "get_weather",
                    "arguments": {"city": "Seattle"},
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "call_weather_1",
            "content": [{"type": "tool_result", "tool_result": {"temperature_c": 14, "condition": "Rainy"}}],
        },
        {"role": "assistant", "content": [{"type": "text", "text": "It is rainy and 14 C in Seattle."}]},
    ]

    # multi-turn example
    messages = [
        {"role": "user", "content": [{"type": "text", "text": "What's the weather in Seattle?"}]},
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_call",
                    "tool_call_id": "call_weather_2",
                    "name": "get_weather",
                    "arguments": {"city": "Seattle"},
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "call_weather_2",
            "content": [{"type": "tool_result", "tool_result": {"temperature_c": 14, "condition": "Rainy"}}],
        },
        {"role": "assistant", "content": [{"type": "text", "text": "It is rainy and 14 C in Seattle."}]},
        {"role": "user", "content": [{"type": "text", "text": "And what about Portland?"}]},
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_call",
                    "tool_call_id": "call_weather_3",
                    "name": "get_weather",
                    "arguments": {"city": "Portland"},
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "call_weather_3",
            "content": [{"type": "tool_result", "tool_result": {"temperature_c": 18, "condition": "Sunny"}}],
        },
        {"role": "assistant", "content": [{"type": "text", "text": "It is sunny and 18 C in Portland."}]},
    ]

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):
        for evaluation_level, item in (
            (
                "turn",
                {"query": query, "response": response, "tool_definitions": tool_definitions},
            ),
            ("conversation", {"messages": messages, "tool_definitions": tool_definitions}),
        ):
            if evaluation_level == "turn":
                properties = {
                    "query": {"type": "array", "items": {"type": "object"}},
                    "response": {"type": "array", "items": {"type": "object"}},
                }
                data_mapping = {
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                    "tool_definitions": "{{item.tool_definitions}}",
                }
            else:
                properties = {"messages": {"type": "array", "items": {"type": "object"}}}
                data_mapping = {
                    "messages": "{{item.messages}}",
                    "tool_definitions": "{{item.tool_definitions}}",
                }
            properties["tool_definitions"] = {"type": "array", "items": {"type": "object"}}

            evaluation = client.evals.create(
                name=f"Tool Use Quality - {evaluation_level}",
                data_source_config=DataSourceConfigCustom(
                    type="custom",
                    item_schema={
                        "type": "object",
                        "properties": properties,
                        "required": list(properties),
                    },
                    include_sample_schema=evaluation_level == "turn",
                ),
                testing_criteria=[
                    TestingCriterionAzureAIEvaluator(
                        type="azure_ai_evaluator",
                        name="tool_use_quality",
                        evaluator_name="builtin.tool_use_quality",
                        initialization_parameters={
                            "deployment_name": model_deployment_name,
                            "evaluation_level": evaluation_level,
                        },
                        data_mapping=data_mapping,
                    )
                ],
            )
            try:
                run = client.evals.runs.create(
                    eval_id=evaluation.id,
                    name=f"{evaluation_level}_inline_run",
                    extra_body={"evaluation_level": evaluation_level},
                    data_source=CreateEvalJSONLRunDataSourceParam(
                        type="jsonl",
                        source=SourceFileContent(
                            type="file_content",
                            content=[SourceFileContentContent(item=item)],
                        ),
                    ),
                )
                while run.status not in ("completed", "failed", "canceled", "cancelled"):
                    time.sleep(5)
                    run = client.evals.runs.retrieve(run_id=run.id, eval_id=evaluation.id)
                print(f"{evaluation_level} tool use quality results:")
                pprint(list(client.evals.runs.output_items.list(run_id=run.id, eval_id=evaluation.id)))
                if run.status != "completed" or run.result_counts.errored:
                    raise RuntimeError(
                        f"{evaluation_level} tool use quality evaluation {run.status}, "
                        f"{run.result_counts.errored} errored item(s): {run.error}"
                    )
            finally:
                client.evals.delete(eval_id=evaluation.id)


if __name__ == "__main__":
    main()
