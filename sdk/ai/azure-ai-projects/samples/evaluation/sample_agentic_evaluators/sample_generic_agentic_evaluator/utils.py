# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import json
import time

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent
)


def run_evaluator(evaluator_name: str, evaluation_contents: list[SourceFileContentContent], data_source_config: dict, initialization_parameters: dict[str, str], data_mapping: dict[str, str]) -> None:
    endpoint = os.environ[
        "PROJECT_ENDPOINT"
    ]  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>

    with DefaultAzureCredential() as credential:
        with AIProjectClient(endpoint=endpoint, credential=credential, api_version="2025-11-15-preview") as project_client:
            print("Creating an OpenAI client from the AI Project client")

            client = project_client.get_openai_client()
            client._custom_query = {"api-version": "2025-11-15-preview"}

            testing_criteria = [
                {
                    "type": "azure_ai_evaluator",
                    "name": f"{evaluator_name}",
                    "evaluator_name": f"builtin.{evaluator_name}",
                    "initialization_parameters": initialization_parameters,
                    "data_mapping": data_mapping
                }
            ]

            print("Creating Eval Group")
            eval_object = client.evals.create(
                name=f"Test {evaluator_name} Evaluator with inline data",
                data_source_config=data_source_config,
                testing_criteria=testing_criteria,
            )
            print(f"Eval Group created")

            print("Get Eval Group by Id")
            eval_object_response = client.evals.retrieve(eval_object.id)
            print("Eval Run Response:")
            pprint(eval_object_response)

            print("Creating Eval Run with Inline Data")
            eval_run_object = client.evals.runs.create(
                eval_id=eval_object.id,
                name="inline_data_run",
                metadata={
                    "team": "eval-exp",
                    "scenario": "inline-data-v1"
                },
                data_source=CreateEvalJSONLRunDataSourceParam(
                    type="jsonl",
                    source=SourceFileContent(
                        type="file_content",
                        content=evaluation_contents
                    )
                )
            )

            print(f"Eval Run created")
            pprint(eval_run_object)

            print("Get Eval Run by Id")
            eval_run_response = client.evals.runs.retrieve(
                run_id=eval_run_object.id, eval_id=eval_object.id)
            print("Eval Run Response:")
            pprint(eval_run_response)

            print("\n\n----Eval Run Output Items----\n\n")

            while True:
                run = client.evals.runs.retrieve(
                    run_id=eval_run_response.id, eval_id=eval_object.id)
                if run.status == "completed" or run.status == "failed":
                    output_items = list(client.evals.runs.output_items.list(
                        run_id=run.id, eval_id=eval_object.id
                    ))
                    pprint(output_items)
                    print(f"Eval Run Status: {run.status}")
                    print(f"Eval Run Report URL: {run.report_url}")
                    break
                time.sleep(5)
                print("Waiting for eval run to complete...")

            # [END evaluations_sample]


def _to_json_primitive(obj):
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_to_json_primitive(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _to_json_primitive(v) for k, v in obj.items()}
    for method in ("to_dict", "as_dict", "dict", "serialize"):
        if hasattr(obj, method):
            try:
                return _to_json_primitive(getattr(obj, method)())
            except Exception:
                pass
    if hasattr(obj, "__dict__"):
        return _to_json_primitive({k: v for k, v in vars(obj).items() if not k.startswith("_")})
    return str(obj)


def pprint(str) -> None:
    print(json.dumps(_to_json_primitive(str), indent=2))
