# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list evaluation and and eval runs
    for Task Navigation Efficiency evaluator using inline dataset content.

USAGE:
    python sample_task_navigation_efficiency.py

    Before running the sample:

    pip install "azure-ai-projects>=2.8.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
"""

import os
import time
from pprint import pprint

from dotenv import load_dotenv

from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
from openai.types.eval_create_params import DataSourceConfigCustom
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import TestingCriterionAzureAIEvaluator

load_dotenv()


def main() -> None:
    endpoint = os.environ.get(
        "FOUNDRY_PROJECT_ENDPOINT", ""
    )  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):

        print("Creating an OpenAI client from the AI Project client")

        data_source_config = DataSourceConfigCustom(
            type="custom",
            item_schema={
                "type": "object",
                "properties": {"actions": {"type": "array"}, "expected_actions": {"type": "array"}},
                "required": ["actions", "expected_actions"],
            },
            include_sample_schema=True,
        )

        testing_criteria = [
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="task_navigation_efficiency",
                evaluator_name="builtin.task_navigation_efficiency",
                initialization_parameters={
                    "matching_mode": "exact_match"  #  Can be "exact_match", "in_order_match", or "any_order_match"
                },
                data_mapping={"actions": "{{item.actions}}", "expected_actions": "{{item.expected_actions}}"},
            )
        ]

        print("Creating Evaluation")
        eval_object = client.evals.create(
            name="Test Task Navigation Efficiency Evaluator with inline data",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,  # type: ignore
        )
        print("Evaluation created")

        print("Get Evaluation by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)

        # single-turn example
        # Simple inline actions and expected actions without parameters
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
                "content": [{"type": "tool_call", "tool_call_id": "call_2", "name": "call_tool_A", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_3", "name": "call_tool_B", "arguments": {}}],
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
        actions = [
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

        expected_actions = ["search", "format_result"]

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
                            item={"actions": simple_response, "expected_actions": simple_ground_truth}
                        ),
                        SourceFileContentContent(item={"actions": actions, "expected_actions": expected_actions}),
                    ],
                ),
            ),
        )

        print("Eval Run created")
        pprint(eval_run_object)

        print("Get Eval Run by Id")
        eval_run_response = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
        print("Eval Run Response:")
        pprint(eval_run_response)

        print("\n\n----Eval Run Output Items----\n\n")

        while True:
            run = client.evals.runs.retrieve(run_id=eval_run_response.id, eval_id=eval_object.id)
            if run.status in ("completed", "failed", "canceled", "cancelled"):
                output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
                pprint(output_items)
                print(f"Eval Run Status: {run.status}")
                print(f"Eval Run Report URL: {run.report_url}")
                break
            time.sleep(5)
            print("Waiting for eval run to complete...")

        client.evals.delete(eval_id=eval_object.id)
        if run.status != "completed" or run.result_counts.errored:
            raise RuntimeError(f"Evaluation {run.status}, {run.result_counts.errored} errored item(s): {run.error}")

        # messages input example (turn-level evaluation)
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "Find the weather in NYC and format it as JSON."}]},
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_search_weather",
                        "name": "search",
                        "arguments": {"query": "weather", "location": "NYC"},
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_search_weather",
                "content": [{"type": "tool_result", "tool_result": {"weather": "Sunny, 20°C"}}],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_format_weather",
                        "name": "format_result",
                        "arguments": {"format": "json"},
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_format_weather",
                "content": [{"type": "tool_result", "tool_result": {"json": '{"weather": "Sunny, 20°C"}'}}],
            },
            {"role": "assistant", "content": [{"type": "text", "text": '{"weather": "Sunny, 20°C"}'}]},
        ]
        messages_eval = client.evals.create(
            name="Test Task Navigation Efficiency Evaluator with messages",
            data_source_config=DataSourceConfigCustom(
                type="custom",
                item_schema={
                    "type": "object",
                    "properties": {
                        "messages": {"type": "array", "items": {"type": "object"}},
                        # Turn-level runs require actions explicitly in addition to the conversation.
                        "actions": {"type": "array", "items": {"type": "object"}},
                        "expected_actions": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["messages", "actions", "expected_actions"],
                },
                include_sample_schema=False,
            ),
            testing_criteria=[
                TestingCriterionAzureAIEvaluator(
                    type="azure_ai_evaluator",
                    name="task_navigation_efficiency_messages",
                    evaluator_name="builtin.task_navigation_efficiency",
                    initialization_parameters={"matching_mode": "exact_match"},
                    data_mapping={
                        "messages": "{{item.messages}}",
                        "actions": "{{item.actions}}",
                        "expected_actions": "{{item.expected_actions}}",
                    },
                )
            ],  # type: ignore
        )
        try:
            messages_run = client.evals.runs.create(
                eval_id=messages_eval.id,
                name="messages_inline_run",
                extra_body={"evaluation_level": "turn"},
                data_source=CreateEvalJSONLRunDataSourceParam(
                    type="jsonl",
                    source=SourceFileContent(
                        type="file_content",
                        content=[
                            SourceFileContentContent(
                                item={
                                    "messages": messages,
                                    "actions": actions,
                                    "expected_actions": expected_actions,
                                }
                            )
                        ],
                    ),
                ),
            )
            while messages_run.status not in ("completed", "failed", "canceled", "cancelled"):
                time.sleep(5)
                messages_run = client.evals.runs.retrieve(run_id=messages_run.id, eval_id=messages_eval.id)
            print(f"Messages eval run status: {messages_run.status}")
            print(f"Messages eval run report: {messages_run.report_url}")
            pprint(list(client.evals.runs.output_items.list(run_id=messages_run.id, eval_id=messages_eval.id)))
            if messages_run.status != "completed" or messages_run.result_counts.errored:
                raise RuntimeError(
                    f"Messages evaluation {messages_run.status}, "
                    f"{messages_run.result_counts.errored} errored item(s): {messages_run.error}"
                )
        finally:
            client.evals.delete(eval_id=messages_eval.id)


if __name__ == "__main__":
    main()
