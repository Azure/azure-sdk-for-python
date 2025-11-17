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
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.

"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    EvaluatorVersion,
    EvaluatorCategory,
    PromptBasedEvaluatorDefinition,
    CodeBasedEvaluatorDefinition,
    EvaluatorType,
    EvaluatorMetric,
    EvaluatorMetricDirection,
    EvaluatorMetricType,
)

from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    print("Creating Prompt based custom evaluator version (object style)")
    evaluator_version = EvaluatorVersion(
        evaluator_type=EvaluatorType.CUSTOM,
        categories=[EvaluatorCategory.QUALITY],
        display_name="my_custom_evaluator",
        description="Custom evaluator to detect violent content",
        definition=PromptBasedEvaluatorDefinition(
            prompt_text="""You are an evaluator.
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
            init_parameters={
                "type": "object",
                "properties": {"deployment_name": {"type": "string"}, "threshold": {"type": "number"}},
                "required": ["deployment_name", "threshold"],
            },
            data_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "response": {"type": "string"},
                },
                "required": ["query", "response"],
            },
            metrics={
                "score": EvaluatorMetric(
                    type=EvaluatorMetricType.ORDINAL,
                    desirable_direction=EvaluatorMetricDirection.INCREASE,
                    min_value=1,
                    max_value=5,
                )
            },
        ),
    )
    prompt_evaluator = project_client.evaluators.create_version(
        name="my_custom_evaluator_code_prompt_based",
        evaluator_version=evaluator_version,
    )
    pprint(prompt_evaluator)

    print("Creating Code based custom evaluator version (object style)")
    evaluator_version = EvaluatorVersion(
        evaluator_type=EvaluatorType.CUSTOM,
        categories=[EvaluatorCategory.QUALITY],
        display_name="my_custom_evaluator",
        description="Custom evaluator to detect violent content",
        definition=CodeBasedEvaluatorDefinition(
            code_text="def grade(sample, item):\n    return 1.0",
            init_parameters={
                "type": "object",
                "properties": {"deployment_name": {"type": "string"}},
                "required": ["deployment_name"],
            },
            data_schema={
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "response": {"type": "string"},
                },
                "required": ["query", "response"],
            },
            metrics={
                "tool_selection": EvaluatorMetric(
                    type=EvaluatorMetricType.ORDINAL,
                    desirable_direction=EvaluatorMetricDirection.INCREASE,
                    min_value=0,
                    max_value=5,
                )
            },
        ),
    )
    code_evaluator = project_client.evaluators.create_version(
        name="my_custom_evaluator_code_based", evaluator_version=evaluator_version
    )
    pprint(code_evaluator)

    print("Get code based evaluator version")
    code_evaluator_latest = project_client.evaluators.get_version(
        name=code_evaluator.name,
        version=code_evaluator.version,
    )
    pprint(code_evaluator_latest)

    print("Get prompt based evaluator version")
    prompt_evaluator_latest = project_client.evaluators.get_version(
        name=prompt_evaluator.name,
        version=prompt_evaluator.version,
    )
    pprint(prompt_evaluator_latest)

    print("Updating code based evaluator version")
    updated_evaluator = project_client.evaluators.update_version(
        name=code_evaluator.name,
        version=code_evaluator.version,
        evaluator_version={
            "categories": [EvaluatorCategory.SAFETY],
            "display_name": "my_custom_evaluator_updated",
            "description": "Custom evaluator description changed",
        },
    )
    pprint(updated_evaluator)

    print("Deleting code based evaluator version")
    project_client.evaluators.delete_version(
        name=code_evaluator_latest.name,
        version=code_evaluator_latest.version,
    )

    project_client.evaluators.delete_version(
        name=prompt_evaluator_latest.name,
        version=prompt_evaluator_latest.version,
    )

    print("Getting list of builtin evaluator versions")
    evaluators = project_client.evaluators.list_latest_versions(type="builtin")
    print("List of builtin evaluator versions")
    for evaluator in evaluators:
        pprint(evaluator)

    print("Getting list of custom evaluator versions")
    evaluators = project_client.evaluators.list_latest_versions(type="custom")
    print("List of custom evaluator versions")
    for evaluator in evaluators:
        pprint(evaluator)

    print("Sample completed successfully")
