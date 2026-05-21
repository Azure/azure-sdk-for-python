# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to run a conversation
    simulation evaluation against a Foundry agent. The service generates multi-turn
    conversations by simulating a user interacting with your agent based on seed
    scenarios, then evaluates the generated conversations with conversation-level
    metrics.

    This is Scenario 4 of multi-turn evaluations: you provide seed scenarios
    (each describing a test case), and the service generates full conversations
    by replaying simulated user turns against your agent. The generated
    conversations are then scored by conversation-level evaluators.

    Key concepts:
      - data_source type is "azure_ai_target_completions" with
        item_generation_params.type = "conversation_gen_preview"
      - num_conversations is per seed scenario (e.g., 2 conversations × 3 scenarios = 6 total)
      - max_turns controls the maximum exchanges per conversation
      - The seed scenarios source is at the data_source root level

USAGE:
    python sample_multiturn_conversation_simulation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint.
    2) FOUNDRY_MODEL_NAME - Required. The model deployment name for the simulator
       and AI-assisted evaluators.
    3) FOUNDRY_AGENT_NAME - Required. The name of the Foundry agent to simulate against.
"""

import os
import time
from pprint import pprint
from dotenv import load_dotenv
from openai.types.eval_create_params import DataSourceConfigCustom
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import TestingCriterionAzureAIEvaluator, PromptAgentDefinition

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "")

# Path to the simulation scenarios data file
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "data_folder"))
scenarios_file = os.path.join(data_folder, "sample_data_simulation_scenarios.jsonl")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):
    # Create (or update) an agent to simulate against
    agent = project_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model_deployment_name,
            instructions="You are a helpful customer service agent. Be empathetic and solution-oriented.",
        ),
    )
    print(f"Agent created (name: {agent.name}, version: {agent.version})")

    # Simulation uses the same "custom" eval group type as dataset evaluation (S1),
    # since the generated conversations follow the same messages schema.
    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
                "messages": {"type": "array"},
            },
            "required": ["messages"],
        },
        include_sample_schema=False,
    )

    # Conversation-level evaluators
    testing_criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="customer_satisfaction",
            evaluator_name="builtin.customer_satisfaction",
            initialization_parameters={"deployment_name": model_deployment_name},
            data_mapping={"messages": "{{item.messages}}"},
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="task_completion",
            evaluator_name="builtin.task_completion",
            initialization_parameters={"deployment_name": model_deployment_name},
            data_mapping={"messages": "{{item.messages}}"},
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="conversation_coherence",
            evaluator_name="builtin.coherence",
            initialization_parameters={"deployment_name": model_deployment_name},
            data_mapping={"messages": "{{item.messages}}"},
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="groundedness",
            evaluator_name="builtin.groundedness",
            initialization_parameters={"model": model_deployment_name},
            data_mapping={"messages": "{{item.messages}}"},
        ),
    ]

    print("Creating simulation evaluation group")
    eval_object = client.evals.create(
        name="Multi-turn Conversation Simulation",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created (id: {eval_object.id})")

    # Upload the simulation scenarios dataset
    try:
        dataset = project_client.datasets.upload_file(
            name="simulation-scenarios",
            version="1",
            file_path=scenarios_file,
        )
        assert dataset.id is not None, "Dataset upload returned no ID"
        scenarios_id: str = dataset.id
        print(f"Scenarios dataset uploaded (id: {scenarios_id})")
    except Exception:
        # Dataset already exists — use the existing URI
        scenarios_id = f"azureai://accounts/{endpoint.split('/')[2].split('.')[0]}/projects/{endpoint.rstrip('/').split('/')[-1]}/data/simulation-scenarios/versions/1"
        print(f"Using existing scenarios dataset (id: {scenarios_id})")

    # Create a simulation run
    # - source: the seed scenarios dataset (each row is a test case)
    # - target: the agent to simulate against
    # - item_generation_params: controls conversation generation
    #   - num_conversations: conversations to generate per seed scenario
    #   - max_turns: maximum exchanges per conversation
    #   - data_mapping: maps JSONL field names to simulation parameters
    eval_run = client.evals.runs.create(
        eval_id=eval_object.id,
        name="conversation-simulation-run",
        data_source={
            "type": "azure_ai_target_completions",
            "source": {
                "type": "file_id",
                "id": scenarios_id,
            },
            "target": {
                "type": "azure_ai_agent",
                "name": agent.name,
                "version": agent.version,
            },
            "item_generation_params": {
                "type": "conversation_gen_preview",
                "model": model_deployment_name,
                "num_conversations": 2,
                "max_turns": 5,
                "sampling_params": {
                    "temperature": 0.7,
                    "top_p": 1.0,
                    "max_completion_tokens": 800,
                },
                "data_mapping": {
                    "test_case_description": "test_case_description",
                    "id": "id",
                    "desired_num_turns": "desired_num_turns",
                },
            },
        },  # type: ignore
        extra_body={"evaluation_level": "conversation"},
    )
    print(f"Simulation run created (id: {eval_run.id})")
    print("Simulation runs are slow (3-8 min). Polling...")

    while True:
        run = client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_object.id)
        if run.status in ("completed", "failed"):
            break
        print(f"Waiting for simulation to complete... current status: {run.status}")
        time.sleep(10)

    if run.status == "completed":
        print("\n✓ Simulation run completed successfully!")
        print(f"Result Counts: {run.result_counts}")
        # With 3 seed scenarios and num_conversations=2, expect 6 total conversations
        print(f"Expected: {3 * 2} conversations (3 scenarios × 2 per scenario)")

        output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
        print(f"\nOUTPUT ITEMS (Total: {len(output_items)})")
        print(f"{'-'*60}")
        pprint(output_items)
        print(f"{'-'*60}")

        print(f"\nEval Run Report URL: {run.report_url}")
    else:
        print(f"\n✗ Simulation run failed: {run.error}")

    client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")
