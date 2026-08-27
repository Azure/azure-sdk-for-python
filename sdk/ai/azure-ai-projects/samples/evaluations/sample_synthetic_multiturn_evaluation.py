# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end multi-turn evaluation with no hand-authored test data. This sample
    chains three services:

      1. Data generation produces a seed dataset with the `simulation_seed`
         recipe. Each generated row describes a scenario for a simulated user:
         `id`, `category`, `test_case_description`, and `desired_num_turns`.
      2. Conversation simulation replays those scenarios against a Foundry agent
         to produce full multi-turn conversations.
      3. Conversation-level evaluators score the generated conversations.

    The generated seed rows have the same shape that
    `sample_multiturn_conversation_simulation.py` uploads from
    `data_folder/sample_data_simulation_scenarios.jsonl`. Use that sample when
    you want to author scenarios yourself; use this sample to derive scenarios
    from an agent's instructions.

    For single-turn synthetic evaluation, see
    `sample_synthetic_data_agent_evaluation.py`.

    This feature is currently in preview.

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
from openai.types.eval_create_params import DataSourceConfigCustom

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentDataGenerationJobSource,
    DataGenerationJob,
    DataGenerationJobInputs,
    DataGenerationJobOutputOptions,
    DataGenerationJobScenario,
    DataGenerationModelOptions,
    DatasetDataGenerationJobOutput,
    PromptAgentDefinition,
    SimulationSeedDataGenerationJobOptions,
    TestingCriterionAzureAIEvaluator,
)

SEED_COUNT = 15
CONVERSATIONS_PER_SEED = 1
MAX_TURNS = 5


def main() -> None:
    """Generate simulation seeds, simulate conversations, and evaluate them."""
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

        # max_samples must be in [15, 1000]. The agent source lets the service
        # derive seed scenarios from the agent's instructions and metadata.
        print(f"\nGenerating {SEED_COUNT} seed scenarios (this takes a few minutes)...")
        poller = project_client.beta.datasets.begin_create_generation_job(
            job=DataGenerationJob(
                inputs=DataGenerationJobInputs(
                    name=f"{agent_name}-simulation-seeds",
                    scenario=DataGenerationJobScenario.EVALUATION,
                    sources=[
                        AgentDataGenerationJobSource(
                            description="Agent instructions and metadata used to generate simulation scenarios.",
                            agent_name=agent.name,
                            agent_version=agent.version,
                        ),
                    ],
                    options=SimulationSeedDataGenerationJobOptions(
                        max_samples=SEED_COUNT,
                        model_options=DataGenerationModelOptions(
                            model=model_deployment_name
                        ),
                    ),
                    output_options=DataGenerationJobOutputOptions(
                        name=f"{agent_name}-simulation-seeds"
                    ),
                ),
            ),
            polling_interval=10,
        )

        generation_result = poller.result()
        seeds = generation_result.outputs[0] if generation_result.outputs else None
        assert isinstance(
            seeds, DatasetDataGenerationJobOutput
        ), "Expected a dataset output from the generation job"
        assert seeds.id is not None, "Generation job returned a dataset without an id"

        print(f"Generated {generation_result.generated_samples} seed scenarios")
        print(f"Seed dataset: {seeds.name} v{seeds.version}")
        if generation_result.token_usage:
            print(f"Generation tokens: {generation_result.token_usage.total_tokens}")

        # Simulation emits conversations in the standard messages schema.
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

        testing_criteria = [
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="task_completion",
                evaluator_name="builtin.task_completion",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={"messages": "{{item.messages}}"},
            ),
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="customer_satisfaction",
                evaluator_name="builtin.customer_satisfaction",
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
            # The data mapping binds the generated seed columns directly to the
            # simulator inputs; no conversion or renaming is required.
            eval_run = client.evals.runs.create(
                eval_id=eval_object.id,
                name="synthetic-multiturn-run",
                data_source={
                    "type": "azure_ai_target_completions",
                    "source": {
                        "type": "file_id",
                        "id": seeds.id,
                    },
                    "target": {
                        "type": "azure_ai_agent",
                        "name": agent.name,
                        "version": agent.version,
                    },
                    "item_generation_params": {
                        "type": "conversation_gen_preview",
                        "model": model_deployment_name,
                        "num_conversations": CONVERSATIONS_PER_SEED,
                        "max_turns": MAX_TURNS,
                        "data_mapping": {
                            "id": "id",
                            "test_case_description": "test_case_description",
                            "desired_num_turns": "desired_num_turns",
                        },
                    },
                },  # type: ignore
                extra_body={"evaluation_level": "conversation"},
            )
            print(f"Simulation run created (id: {eval_run.id})")
            print("Simulation runs can take several minutes. Polling...")

            while True:
                run = client.evals.runs.retrieve(
                    run_id=eval_run.id, eval_id=eval_object.id
                )
                if run.status in ("completed", "failed", "canceled"):
                    break
                print(
                    f"Waiting for simulation to complete... current status: {run.status}"
                )
                time.sleep(10)

            if run.status != "completed":
                raise RuntimeError(f"Simulation run failed: {run.error}")

            print("\nSynthetic multi-turn evaluation completed successfully.")
            print(f"Result Counts: {run.result_counts}")
            if run.result_counts.errored:
                raise RuntimeError(
                    f"{run.result_counts.errored} evaluation item(s) errored"
                )

            expected_conversations = (
                generation_result.generated_samples * CONVERSATIONS_PER_SEED
            )
            print(
                f"Expected: {expected_conversations} conversations "
                f"({generation_result.generated_samples} generated scenarios x "
                f"{CONVERSATIONS_PER_SEED} per scenario)"
            )

            output_items = list(
                client.evals.runs.output_items.list(
                    run_id=run.id, eval_id=eval_object.id
                )
            )
            if (
                run.result_counts.total != expected_conversations
                or len(output_items) != expected_conversations
            ):
                raise RuntimeError(
                    f"Expected {expected_conversations} conversations, got "
                    f"{run.result_counts.total} results and {len(output_items)} output items"
                )

            print(f"\nOutput items: {len(output_items)}")
            if output_items:
                print("First output item:")
                pprint(output_items[0])

            print(f"\nEval Run Report URL: {run.report_url}")
            print(f"Reusable seed dataset: {seeds.name} v{seeds.version}")
        finally:
            client.evals.delete(eval_id=eval_object.id)
            print("Evaluation deleted")


if __name__ == "__main__":
    main()
