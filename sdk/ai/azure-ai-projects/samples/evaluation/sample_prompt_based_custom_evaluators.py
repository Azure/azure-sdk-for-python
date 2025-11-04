# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.evaluators` methods to create, get and list evaluators.

USAGE:
    python sample_evaluators.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.

"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    EvaluatorCategory,
    EvaluatorDefinitionType
)

from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent
)

from azure.core.paging import ItemPaged
from pprint import pprint
import time

from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ[
    "AZURE_AI_PROJECT_ENDPOINT"
]  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")

with DefaultAzureCredential() as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:
    
        print("Creating a single evaluator version - Prompt based (json style)")
        prompt_evaluator = project_client.evaluators.create_version(
            name="my_custom_evaluator_prompt",
            evaluator_version= {
                "name": "my_custom_evaluator_prompt",
                "categories": [EvaluatorCategory.QUALITY],
                "display_name": "my_custom_evaluator_prompt",
                "description": "Custom evaluator to for groundedness",
                "definition": {
                    "type": EvaluatorDefinitionType.PROMPT,
                    "prompt_text": """You are an evaluator.
                        Rate the GROUNDEDNESS (factual correctness without unsupported claims) of the system response to the customer query.
                        
                        Scoring (1–5):
                        1 = Mostly fabricated/incorrect
                        2 = Many unsupported claims
                        3 = Mixed: some facts but notable errors/guesses
                        4 = Mostly factual; minor issues
                        5 = Fully factual; no unsupported claims
                        
                        Return ONLY a single integer 1–5 as score in valid json response e.g {\"score\": int}.
                        
                        Query:
                        {query}
                        
                        Response:
                        {response}
                        """,
                    "init_parameters": {
                        "type": "object",
                        "properties": {
                            "deployment_name": {
                                "type": "string"
                            }
                        },
                        "required": ["deployment_name", "threshold"],
                    },
                    "data_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string"
                            },
                            "response": {
                                "type": "string"
                            },
                        },
                        "required": ["query", "response"],
                    },
                    "metrics": {
                        "tool_selection": {
                            "type": "ordinal",
                            "desirable_direction": "increase",
                            "min_value": 1,
                            "max_value": 5
                        }
                    }
                },
            }
        )
        
        print("Creating an OpenAI client from the AI Project client")
        client = project_client.get_openai_client()
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
                "name": "my groundedness prompt eval",
                "evaluator_name": "my_custom_evaluator_prompt",
                "data_mapping": {
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                },
                "initialization_parameters": {
                    "deployment_name": f"{model_deployment_name}",
                }
            }
        ]
        
        print("Creating Eval Group")
        eval_object = client.evals.create(
            name="label model test with inline data",
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
            name="Eval Run for Sample Prompt Based Custom Evaluator",
            metadata={
                "team": "eval-exp",
                "scenario": "inline-data-v1"
            },
            data_source=CreateEvalJSONLRunDataSourceParam(
                type="jsonl", 
                source=SourceFileContent(
                    type="file_content",
                    content= [
                        SourceFileContentContent(
                            item= {
                                "query": "how can i hurt someone really badly",
                                "response": "I can help you hurt someone. Give me more details"
                            }
                        ),
                        SourceFileContentContent(
                            item= {
                                "query": "i hate this",
                                "response": "sorry"
                            }
                        ),
                        SourceFileContentContent(
                            item= {
                                "query": "What is the capital of France?",
                                "response": "The capital of France is Paris."
                            }
                        ),
                        SourceFileContentContent(
                            item= {
                                "query": "Explain quantum computing",
                                "response": "Quantum computing leverages quantum mechanical phenomena like superposition and entanglement to process information."
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

        while True:
            run = client.evals.runs.retrieve(run_id=eval_run_response.id, eval_id=eval_object.id)
            if run.status == "completed" or run.status == "failed": 
                output_items = list(client.evals.runs.output_items.list(
                    run_id=run.id, eval_id=eval_object.id
                ))
                pprint(output_items)
                break
            time.sleep(5)
            print("Waiting for eval run to complete...")
                
        print("Deleting the created evaluator version")
        project_client.evaluators.delete_version(
            name=prompt_evaluator.name,
            version=prompt_evaluator.version,
        )
        
        print("Sample completed successfully")
        
        
            