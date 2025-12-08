# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to create and run an evaluation for an Azure AI agent response
    using the synchronous AIProjectClient.

    The OpenAI compatible Evals calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

USAGE:
    python sample_agent_response_evaluation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_AGENT_NAME - The name of the AI agent to use for evaluation.
    3) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import time
from typing import Union
from pprint import pprint
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from openai.types.evals.run_create_response import RunCreateResponse
from openai.types.evals.run_retrieve_response import RunRetrieveResponse

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    agent = project_client.agents.create_version(
        agent_name=os.environ["AZURE_AI_AGENT_NAME"],
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant that answers general questions",
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    conversation = openai_client.conversations.create(
        items=[{"type": "message", "role": "user", "content": "What is the size of France in square miles?"}],
    )
    print(f"Created conversation with initial user message (id: {conversation.id})")

    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        input="",
    )
    print(f"Response output: {response.output_text} (id: {response.id})")

    data_source_config = {"type": "azure_ai_source", "scenario": "responses"}
    testing_criteria = [
        {"type": "azure_ai_evaluator", "name": "violence_detection", "evaluator_name": "builtin.violence"}
    ]
    eval_object = openai_client.evals.create(
        name="Agent Response Evaluation",
        data_source_config=data_source_config,  # type: ignore
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    data_source = {
        "type": "azure_ai_responses",
        "item_generation_params": {
            "type": "response_retrieval",
            "data_mapping": {"response_id": "{{item.resp_id}}"},
            "source": {"type": "file_content", "content": [{"item": {"resp_id": response.id}}]},
        },
    }

    response_eval_run: Union[RunCreateResponse, RunRetrieveResponse] = openai_client.evals.runs.create(
        eval_id=eval_object.id, name=f"Evaluation Run for Agent {agent.name}", data_source=data_source  # type: ignore
    )
    print(f"Evaluation run created (id: {response_eval_run.id})")

    while response_eval_run.status not in ["completed", "failed"]:
        response_eval_run = openai_client.evals.runs.retrieve(run_id=response_eval_run.id, eval_id=eval_object.id)
        print(f"Waiting for eval run to complete... current status: {response_eval_run.status}")
        time.sleep(5)

    if response_eval_run.status == "completed":
        print("\n✓ Evaluation run completed successfully!")
        print(f"Result Counts: {response_eval_run.result_counts}")

        output_items = list(
            openai_client.evals.runs.output_items.list(run_id=response_eval_run.id, eval_id=eval_object.id)
        )
        print(f"\nOUTPUT ITEMS (Total: {len(output_items)})")
        print(f"Eval Run Report URL: {response_eval_run.report_url}")

        print(f"{'-'*60}")
        pprint(output_items)
        print(f"{'-'*60}")
    else:
        print("\n✗ Evaluation run failed.")

    openai_client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")

    project_client.agents.delete(agent_name=agent.name)
    print("Agent deleted")
