# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list eval group and and eval runs
    for Task Adherence evaluator using inline dataset content.

USAGE:
    python sample_task_adherence.py

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
                    "required": ["query", "response"],
                },
                "include_sample_schema": True,
            }
        )

        testing_criteria = [
            {
                "type": "azure_ai_evaluator",
                "name": "task_adherence",
                "evaluator_name": "builtin.task_adherence",
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
            name="Test Task Adherence Evaluator with inline data",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,  # type: ignore
        )
        print(f"Eval Group created")

        print("Get Eval Group by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)

        # Failure example - vague adherence to the task
        failure_query = "What are the best practices for maintaining a healthy rose garden during the summer?"
        failure_response = "Make sure to water your roses regularly and trim them occasionally."

        # Success example - full adherence to the task
        success_query = "What are the best practices for maintaining a healthy rose garden during the summer?"
        success_response = "For optimal summer care of your rose garden, start by watering deeply early in the morning to ensure the roots are well-hydrated without encouraging fungal growth. Apply a 2-3 inch layer of organic mulch around the base of the plants to conserve moisture and regulate soil temperature. Fertilize with a balanced rose fertilizer every 4–6 weeks to support healthy growth. Prune away any dead or diseased wood to promote good air circulation, and inspect regularly for pests such as aphids or spider mites, treating them promptly with an appropriate organic insecticidal soap. Finally, ensure that your roses receive at least 6 hours of direct sunlight daily for robust flowering."

        # Complex conversation example with tool calls
        complex_query = [
            {"role": "system", "content": "You are an expert in literature and can provide book recommendations."},
            {
                "createdAt": "2025-03-14T08:00:00Z",
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "I love historical fiction. Can you recommend a good book from that genre?",
                    }
                ],
            },
        ]

        complex_response = [
            {
                "createdAt": "2025-03-14T08:00:05Z",
                "role": "assistant",
                "content": [{"type": "text", "text": "Let me fetch a recommendation for historical fiction."}],
            },
            {
                "createdAt": "2025-03-14T08:00:10Z",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "tool_call_20250314_001",
                        "name": "get_book",
                        "arguments": {"genre": "historical fiction"},
                    }
                ],
            },
            {
                "createdAt": "2025-03-14T08:00:15Z",
                "role": "tool",
                "tool_call_id": "tool_call_20250314_001",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": '{ "book": { "title": "The Pillars of the Earth", "author": "Ken Follett", "summary": "A captivating tale set in medieval England that weaves historical events with personal drama." } }',
                    }
                ],
            },
            {
                "createdAt": "2025-03-14T08:00:20Z",
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "Based on our records, I recommend 'The Pillars of the Earth' by Ken Follett. This novel is an excellent example of historical fiction with a rich narrative and well-developed characters. Would you like more details or another suggestion?",
                    }
                ],
            },
        ]

        complex_tool_definitions = [
            {
                "name": "get_book",
                "description": "Retrieve a book recommendation for a specified genre.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "genre": {
                            "type": "string",
                            "description": "The genre for which a book recommendation is requested.",
                        }
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
                        # Failure example - vague adherence
                        SourceFileContentContent(
                            item={"query": failure_query, "response": failure_response, "tool_definitions": None}
                        ),
                        # Success example - full adherence
                        SourceFileContentContent(
                            item={"query": success_query, "response": success_response, "tool_definitions": None}
                        ),
                        # Complex conversation example with tool calls
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
