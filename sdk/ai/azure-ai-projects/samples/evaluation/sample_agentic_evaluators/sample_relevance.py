# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list eval group and and eval runs
    for Relevance evaluator using inline dataset content.

USAGE:
    python sample_relevance.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) MODEL_DEPLOYMENT_NAME - Required. The name of the model deployment to use for evaluation.
"""

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

def main() -> None:
    endpoint = os.environ[
        "PROJECT_ENDPOINT"
    ]  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
    model_deployment_name = os.environ.get("MODEL_DEPLOYMENT_NAME", "")  # Sample : gpt-4o-mini

    with DefaultAzureCredential() as credential:
        with AIProjectClient(endpoint=endpoint, credential=credential, api_version="2025-11-15-preview") as project_client:
            print("Creating an OpenAI client from the AI Project client")
            
            client = project_client.get_openai_client()
            client._custom_query = {"api-version": "2025-11-15-preview"}
            
            data_source_config = {
                "type": "custom",
                "item_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string"
                        },
                        "response": {
                            "type": "string"
                        }
                    },
                    "required": ["query", "response"]
                },
                "include_sample_schema": True
            }
            
            testing_criteria = [
                {
                    "type": "azure_ai_evaluator",
                    "name": "relevance",
                    "evaluator_name": "builtin.relevance",
                    "initialization_parameters": {
                        "deployment_name": f"{model_deployment_name}"
                    },
                    "data_mapping": {
                        "query": "{{item.query}}",
                        "response": "{{item.response}}"
                    }
                }
            ]
            
            print("Creating Eval Group")
            eval_object = client.evals.create(
                name="Test Relevance Evaluator with inline data",
                data_source_config=data_source_config,
                testing_criteria=testing_criteria,
            )
            print(f"Eval Group created")

            print("Get Eval Group by Id")
            eval_object_response = client.evals.retrieve(eval_object.id)
            print("Eval Run Response:")
            pprint(eval_object_response)

            # Success example - relevant response
            success_query = "What is the capital of Japan?"
            success_response = "The capital of Japan is Tokyo."

            # Failure example - irrelevant response
            failure_query = "What is the capital of Japan?"
            failure_response = "Japan is known for its beautiful cherry blossoms and advanced technology. The country has a rich cultural heritage and is famous for sushi and anime."

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
                        content= [
                            # Success example - relevant response
                            SourceFileContentContent(
                                item= {
                                    "query": success_query,
                                    "response": success_response
                                }
                            ),
                            # Failure example - irrelevant response
                            SourceFileContentContent(
                                item= {
                                    "query": failure_query,
                                    "response": failure_response
                                }
                            )
                        ]
                    )
                )
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

if __name__ == "__main__":
    main()