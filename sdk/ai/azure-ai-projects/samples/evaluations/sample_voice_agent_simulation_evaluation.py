# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Simulate a short voice conversation against an existing voice agent and
    grade the generated recording with the task-completion audio evaluator.
    The simulator model generates user turns; the audio judge grades the call.
    This is not a full-duplex tracing example.

USAGE:
    python sample_voice_agent_simulation_evaluation.py

    pip install "azure-ai-projects>=2.8.0" python-dotenv

    Set these environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT - Project endpoint.
    2) FOUNDRY_MODEL_NAME - Eligible audio-input judge deployment.
    3) FOUNDRY_AGENT_NAME - Existing voice agent to call.
    4) FOUNDRY_AGENT_VERSION - Version of that agent.
    5) FOUNDRY_SIMULATOR_MODEL_NAME - Chat model driving the simulated user.
    6) FOUNDRY_SIMULATOR_VOICE - Speech voice, for example en-US-AvaNeural.

    Requires deployed voice-simulation support. The existing agent is not changed
    or deleted. Simulation generates billable model/agent calls and output data.
"""

import os
import time
from pprint import pprint
from typing import Any, cast

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import TestingCriterionAzureAIEvaluator
from openai.types.eval_create_params import DataSourceConfigCustom
from openai.types.evals import RunCreateResponse, RunRetrieveResponse


def main() -> None:
    load_dotenv()
    data_source = {
        "type": "azure_ai_user_conversation_simulation",
        "source": {
            "type": "inline_user_conversation_simulation",
            "test_cases": [
                {
                    "test_case_id": "store_hours",
                    "test_case_description": (
                        "Ask when the store closes today. If asked for a location, "
                        "say Springfield, Illinois. Do not invent a closing time."
                    ),
                }
            ],
        },
        "target": {
            "type": "azure_ai_agent",
            "name": os.environ["FOUNDRY_AGENT_NAME"],
            "version": os.environ["FOUNDRY_AGENT_VERSION"],
        },
        "model_configuration": {
            "model": os.environ["FOUNDRY_SIMULATOR_MODEL_NAME"],
            "voice_model": {
                "type": "azure-standard",
                "name": os.environ["FOUNDRY_SIMULATOR_VOICE"],
            },
        },
        "default_simulation_configuration": {
            "max_num_turns": 3,
            "conversation_repetitions": 1,
            "enable_conversation_dataset_generation": True,
        },
    }
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], credential=credential
        ) as project_client,
        project_client.get_openai_client() as client,
    ):
        evaluation = client.evals.create(
            name="Voice agent simulation evaluation",
            data_source_config=DataSourceConfigCustom(
                type="custom",
                item_schema={
                    "type": "object",
                    "properties": {
                        "messages": {"type": "array"},
                        "conversation_artifacts": {"type": "object"},
                    },
                },
                include_sample_schema=False,
            ),
            testing_criteria=[
                TestingCriterionAzureAIEvaluator(
                    type="azure_ai_evaluator",
                    name="task_completion",
                    evaluator_name="builtin.task_completion_audio",
                    evaluator_version="1",
                    initialization_parameters={
                        "deployment_name": os.environ["FOUNDRY_MODEL_NAME"]
                    },
                )
            ],
        )
        run: RunCreateResponse | RunRetrieveResponse | None = None
        terminal_states = ("completed", "failed", "cancelled", "canceled")
        try:
            run = client.evals.runs.create(
                eval_id=evaluation.id,
                name="Voice agent simulation evaluation run",
                # The OpenAI SDK does not yet type the Foundry simulation source.
                data_source=cast(Any, data_source),
                extra_body={"evaluation_level": "conversation"},
            )
            print(f"Evaluation run created: {run.id}")
            deadline = time.monotonic() + 600
            while run.status not in terminal_states:
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        f"Evaluation run {run.id} did not finish within 600 seconds"
                    )
                time.sleep(5)
                run = client.evals.runs.retrieve(eval_id=evaluation.id, run_id=run.id)
            for item in client.evals.runs.output_items.list(
                eval_id=evaluation.id, run_id=run.id
            ):
                pprint(item)
            if run.status != "completed":
                raise RuntimeError(f"Evaluation run {run.status}: {run.error}")
            if run.result_counts.errored:
                raise RuntimeError(
                    f"{run.result_counts.errored} evaluation item(s) errored"
                )
            if not run.result_counts.total:
                raise RuntimeError("The evaluation produced no items")
            print(f"Result counts: {run.result_counts}")
        finally:
            try:
                if run is not None and run.status not in terminal_states:
                    client.evals.runs.cancel(eval_id=evaluation.id, run_id=run.id)
            finally:
                client.evals.delete(eval_id=evaluation.id)


if __name__ == "__main__":
    main()
