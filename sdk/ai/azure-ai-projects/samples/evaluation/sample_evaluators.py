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

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.

"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    EvaluatorVersion,
    EvaluatorCategory,
    EvaluatorDefinitionType,
)
from azure.core.paging import ItemPaged
from pprint import pprint

from dotenv import load_dotenv
load_dotenv()

endpoint = os.environ[
    "AZURE_AI_PROJECT_ENDPOINT"
]  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>

with DefaultAzureCredential() as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:
    
        prompt_evaluator = project_client.evaluators.create_version(
            name="my_custom_evaluator_prompt",
            evaluator_version= {
                "name": "my_custom_evaluator_prompt",
                "categories": [EvaluatorCategory.QUALITY],
                "display_name": "my_custom_evaluator_prompt",
                "description": "Custom evaluator to detect violent content",
                "definition": {
                    "type": EvaluatorDefinitionType.PROMPT,
                    "prompt_text": "Detect violent content in the text.",
                    "init_parameters": {
                        "required": [
                            "deployment_name"
                        ],
                        "type": "object",
                        "properties": {
                            "deployment_name": {
                            "type": "string"
                            },
                            "threshold": {
                            "type": "number"
                            },
                            "credential": {
                            "type": "object"
                            }
                        }
                    },
                    "metrics": {
                        "tool_selection": {
                            "type": "ordinal",
                            "desirable_direction": "increase",
                            "min_value": 0,
                            "max_value": 1
                        }
                    },
                    "data_schema": {
                        "required": [
                            "query",
                            "response",
                            "tool_definitions"
                        ],
                        "type": "object",
                        "properties": {
                            "query": {
                            "anyOf": [
                                {
                                "type": "string"
                                },
                                {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                }
                                }
                            ]
                            },
                            "response": {
                            "anyOf": [
                                {
                                "type": "string"
                                },
                                {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                }
                                }
                            ]
                            },
                            "tool_calls": {
                            "anyOf": [
                                {
                                "type": "object"
                                },
                                {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                }
                                }
                            ]
                            },
                            "tool_definitions": {
                            "anyOf": [
                                {
                                "type": "object"
                                },
                                {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                }
                                }
                            ]
                            }
                        },
                    },
                },
            }
        )
        
        # Get a single evaluator version
        print("Get a single evaluator version")
        evaluator = project_client.evaluators.get_version(
            name=prompt_evaluator.name,
            version="latest",
        )
        pprint(evaluator)
        
        code_evaluator = project_client.evaluators.create_version(
            name="my_custom_evaluator_code",
            evaluator_version= {
                "name": "my_custom_evaluator_code",
                "categories": [EvaluatorCategory.QUALITY],
                "display_name": "my_custom_evaluator_code",
                "description": "Custom evaluator to detect violent content",
                "definition": {
                    "type": EvaluatorDefinitionType.CODE,
                    "code_text": "def grade(sample, item) -> float:\n    \"\"\"\n    Evaluate response quality based on multiple criteria.\n    Note: All data is in the 'item' parameter, 'sample' is empty.\n    \"\"\"\n    # Extract data from item (not sample!)\n    response = item.get(\"response\", \"\").lower() if isinstance(item, dict) else \"\"\n    ground_truth = item.get(\"ground_truth\", \"\").lower() if isinstance(item, dict) else \"\"\n    query = item.get(\"query\", \"\").lower() if isinstance(item, dict) else \"\"\n    \n    # Check if response is empty\n    if not response:\n        return 0.0\n    \n    # Check for harmful content\n    harmful_keywords = [\"harmful\", \"dangerous\", \"unsafe\", \"illegal\", \"unethical\"]\n    if any(keyword in response for keyword in harmful_keywords):\n        return 0.0\n    \n    # Length check\n    if len(response) < 10:\n        return 0.1\n    elif len(response) < 50:\n        return 0.2\n    \n    # Technical content check\n    technical_keywords = [\"api\", \"experiment\", \"run\", \"azure\", \"machine learning\", \"gradient\", \"neural\", \"algorithm\"]\n    technical_score = sum(1 for k in technical_keywords if k in response) / len(technical_keywords)\n    \n    # Query relevance\n    query_words = query.split()[:3] if query else []\n    relevance_score = 0.7 if any(word in response for word in query_words) else 0.3\n    \n    # Ground truth similarity\n    if ground_truth:\n        truth_words = set(ground_truth.split())\n        response_words = set(response.split())\n        overlap = len(truth_words & response_words) / len(truth_words) if truth_words else 0\n        similarity_score = min(1.0, overlap)\n    else:\n        similarity_score = 0.5\n    \n    return min(1.0, (technical_score * 0.3) + (relevance_score * 0.3) + (similarity_score * 0.4))",
                    "init_parameters": {
                        "required": [
                            "deployment_name"
                        ],
                        "type": "object",
                        "properties": {
                            "deployment_name": {
                            "type": "string"
                            },
                            "threshold": {
                            "type": "number"
                            },
                            "credential": {
                            "type": "object"
                            }
                        }
                    },
                    "metrics": {
                        "tool_selection": {
                            "type": "ordinal",
                            "desirable_direction": "increase",
                            "min_value": 0,
                            "max_value": 1
                        }
                    },
                    "data_schema": {
                        "required": [
                            "query",
                            "response",
                            "tool_definitions"
                        ],
                        "type": "object",
                        "properties": {
                            "query": {
                            "anyOf": [
                                {
                                "type": "string"
                                },
                                {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                }
                                }
                            ]
                            },
                            "response": {
                            "anyOf": [
                                {
                                "type": "string"
                                },
                                {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                }
                                }
                            ]
                            },
                            "tool_calls": {
                            "anyOf": [
                                {
                                "type": "object"
                                },
                                {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                }
                                }
                            ]
                            },
                            "tool_definitions": {
                            "anyOf": [
                                {
                                "type": "object"
                                },
                                {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                }
                                }
                            ]
                            }
                        },
                    },
                },
            }
        )
        
        # Get a single evaluator version
        print("Get a single evaluator version")
        evaluator = project_client.evaluators.get_version(
            name=code_evaluator.name,
            version="latest",
        )
        pprint(evaluator)
        
        # evaluator = EvaluatorVersion(
        #     evaluator_type=EvaluatorType.CUSTOM,
        #     categories=[EvaluatorCategory.QUALITY],
        #     display_name="my_custom_evaluator",
        #     description="Custom evaluator to detect violent content",
        #     definition=PromptBasedEvaluatorDefinition(
        #         prompt_text="Detect violent content in the text.",
        #         init_parameters={},
        #         data_schema={},
        #         metrics={}
        #     )
        # )
        
        # new_evaluator = project_client.evaluators.create_version(
        #     name="my_custom_evaluator",
        #     evaluator_version=evaluator
        # )
        
        # Update an existing evaluator version

        updated_evaluator = project_client.evaluators.update_version(
            name=code_evaluator.name,
            version=code_evaluator.version,
            evaluator_version={
                "categories": [EvaluatorCategory.SAFETY],
                "display_name": "my_custom_evaluator_updated",
                "description": "Custom evaluator to detect violent content"
            }
        )
        project_client.evaluators.delete_version(
            name=code_evaluator.name,
            version=code_evaluator.version,
        )

        # Get a list of evaluator versions
        evaluators: ItemPaged[EvaluatorVersion] = project_client.evaluators.list_latest_versions(type="builtin")
        print("List of builtin evaluator versions")
        for evaluator in evaluators:
            pprint(evaluator)

        evaluators: ItemPaged[EvaluatorVersion] = project_client.evaluators.list_latest_versions(type="custom")
        print("List of custom evaluator versions")
        for evaluator in evaluators:
            pprint(evaluator)
        
        evaluators: ItemPaged[EvaluatorVersion] = project_client.evaluators.list_versions(name="custom.violence")
        print("List of custom evaluator versions")
        for evaluator in evaluators:
            pprint(evaluator)