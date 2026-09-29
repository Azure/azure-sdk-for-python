# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end multi-turn evaluation with no hand-authored test data. A single
    `azure_ai_synthetic_data_generation_with_simulation` data source has the
    service:

      1. Synthesize test-case scenarios from the agent's instructions.
      2. Simulate multi-turn conversations for those scenarios against a Foundry
         agent.
      3. Score the generated conversations with conversation-level evaluators.

    Generation and simulation happen in one eval run — no separate data
    generation job is required. Use `sample_multiturn_conversation_simulation.py`
    when you want to author the seed scenarios yourself; use this sample to
    derive scenarios from an agent's instructions.

    For single-turn synthetic evaluation, see
    `sample_synthetic_data_agent_evaluation.py`.

USAGE:
    python sample_synthetic_multiturn_evaluation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.5.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) FOUNDRY_MODEL_NAME - Required. The name of the model deployment used to generate seed
       scenarios, drive the simulated user, and run AI-assisted evaluators.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
"""

import os
import time
from pprint import pprint

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureAIDataSourceConfig,
    PromptAgentDefinition,
    TestingCriterionAzureAIEvaluator,
)

SEED_COUNT = 1
CONVERSATIONS_PER_SEED = 1
MAX_TURNS = 2
DESIRED_TURNS = 1


def main() -> None:
    """Generate synthetic scenarios, simulate conversations, and evaluate them."""
    load_dotenv()

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]
    agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):
        agent = project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions="You are a helpful customer service agent. Be empathetic and solution-oriented.",
            ),
        )
        print(f"Agent created (name: {agent.name}, version: {agent.version})")

        # Synthetic-data-generation-with-simulation groups declare an
        # "azure_ai_source" config with the "synthetic_data_gen" scenario. The
        # service generates the seed scenarios and simulated conversations at run
        # time, so no inline item schema is supplied.
        data_source_config = AzureAIDataSourceConfig(type="azure_ai_source", scenario="synthetic_data_gen")

        testing_criteria = [
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="tool_use_quality",
                evaluator_name="builtin.tool_use_quality",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={
                    "messages": "{{item.messages}}",
                    "tool_definitions": "{{item.tool_definitions}}",
                },
            ),
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="output_quality",
                evaluator_name="builtin.output_quality",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={
                    "messages": "{{item.messages}}",
                    "tool_definitions": "{{item.tool_definitions}}",
                },
            ),
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="deflection_rate",
                evaluator_name="builtin.deflection_rate",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={
                    "messages": "{{item.messages}}",
                    "tool_definitions": "{{item.tool_definitions}}",
                },
            ),
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="customer_satisfaction",
                evaluator_name="builtin.customer_satisfaction",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={"messages": "{{item.messages}}"},
            ),
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="task_completion",
                evaluator_name="builtin.task_completion",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={"messages": "{{item.messages}}"},
            ),
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="coherence",
                evaluator_name="builtin.coherence",
                initialization_parameters={"model": model_deployment_name},
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

        print("\nCreating evaluation group")
        eval_object = client.evals.create(
            name="Synthetic Multi-turn Evaluation",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,
        )
        print(f"Evaluation created (id: {eval_object.id})")

        try:
            # A single data source generates synthetic scenarios from the agent's
            # instructions and simulates multi-turn conversations for them.
            eval_run = client.evals.runs.create(
                eval_id=eval_object.id,
                name="synthetic-multiturn-run",
                data_source={
                    "type": "azure_ai_synthetic_data_generation_with_simulation",
                    "synthetic_data_generation_configuration": {
                        "test_case_count": SEED_COUNT,
                        "output_test_case_dataset_name": f"{agent_name}-synthetic-scenarios",
                        "generation_sources": [
                            {
                                "type": "agent",
                                "agent_name": agent.name,
                                "agent_version": agent.version,
                            },
                        ],
                    },
                    "model_configuration": {
                        "model": model_deployment_name,
                    },
                    "default_simulation_configuration": {
                        "max_num_turns": MAX_TURNS,
                        "conversation_repetitions": CONVERSATIONS_PER_SEED,
                        "desired_num_turns": DESIRED_TURNS,
                        "enable_conversation_dataset_generation": True,
                        "output_conversation_dataset_name": f"{agent_name}-synthetic-conversations",
                    },
                    "target": {
                        "type": "azure_ai_agent",
                        "name": agent.name,
                        "version": agent.version,
                    },
                },  # type: ignore
                extra_body={"evaluation_level": "conversation"},
            )
            print(f"Simulation run created (id: {eval_run.id})")
            print("Simulation runs can take several minutes. Polling...")

            while True:
                run = client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_object.id)
                if run.status in ("completed", "failed", "canceled"):
                    break
                print(f"Waiting for simulation to complete... current status: {run.status}")
                time.sleep(10)

            if run.status != "completed":
                raise RuntimeError(f"Simulation run failed: {run.error}")

            print("\nSynthetic multi-turn evaluation completed successfully.")
            print(f"Result Counts: {run.result_counts}")
            if run.result_counts.errored:
                raise RuntimeError(f"{run.result_counts.errored} evaluation item(s) errored")

            expected_conversations = SEED_COUNT * CONVERSATIONS_PER_SEED
            print(
                f"Expected up to: {expected_conversations} conversations "
                f"({SEED_COUNT} synthetic scenarios x {CONVERSATIONS_PER_SEED} per scenario)"
            )

            output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))

            print(f"\nOutput items: {len(output_items)}")
            if output_items:
                print("First output item:")
                pprint(output_items[0])

            print(f"\nEval Run Report URL: {run.report_url}")
        finally:
            client.evals.delete(eval_id=eval_object.id)
            print("Evaluation deleted")


if __name__ == "__main__":
    main()
