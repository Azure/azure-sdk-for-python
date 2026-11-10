# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Asynchronously grade an existing recorded-conversation JSONL dataset with
    the four built-in audio evaluators. This does not invoke a target agent.
    See sample_audio_conversation_evaluation.py for the synchronous workflow.

USAGE:
    python sample_audio_conversation_evaluation_async.py

    pip install "azure-ai-projects>=2.8.0" python-dotenv aiohttp

    Set these environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT - Project endpoint.
    2) FOUNDRY_MODEL_NAME - Audio-input judge deployment compatible with the evaluator.
    3) FOUNDRY_DATASET_ID - Existing JSONL dataset ID, not the WAV asset ID.
       See README.md for the required row and recording-reference formats.
    Audio evaluators must be available and the judge must support audio input.
"""

import asyncio
import os
import time
from pprint import pprint

from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import TestingCriterionAzureAIEvaluator
from openai.types.eval_create_params import DataSourceConfigCustom
from openai.types.evals import RunCreateResponse, RunRetrieveResponse
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
)


async def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    dataset_id = os.environ["FOUNDRY_DATASET_ID"]
    testing_criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name=metric,
            evaluator_name=f"builtin.{metric}_audio",
            evaluator_version="1",
            initialization_parameters={
                "deployment_name": os.environ["FOUNDRY_MODEL_NAME"]
            },
        )
        for metric in (
            "task_completion",
            "groundedness",
            "customer_satisfaction",
            "coherence",
        )
    ]

    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
                "messages": {"type": "array"},
                "conversation_artifacts": {
                    "type": "object",
                    "properties": {
                        "audio": {
                            "type": "object",
                            "properties": {
                                "asset_id": {"type": "string"},
                                "asset_file_path": {"type": "string"},
                            },
                            "required": ["asset_id", "asset_file_path"],
                        }
                    },
                    "required": ["audio"],
                },
            },
            "required": ["conversation_artifacts"],
        },
        include_sample_schema=False,
    )
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):
        evaluation = await client.evals.create(
            name="Recorded audio conversation evaluation",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,
        )
        run: RunCreateResponse | RunRetrieveResponse | None = None
        terminal_states = ("completed", "failed", "cancelled", "canceled")
        try:
            run = await client.evals.runs.create(
                eval_id=evaluation.id,
                name="Recorded audio conversation evaluation run",
                data_source=CreateEvalJSONLRunDataSourceParam(
                    type="jsonl",
                    source={"type": "file_id", "id": dataset_id},
                ),
                extra_body={"evaluation_level": "conversation"},
            )
            print(f"Evaluation run created: {run.id}")
            deadline = time.monotonic() + 600
            while run.status not in terminal_states:
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        f"Evaluation run {run.id} did not finish within 600 seconds"
                    )
                await asyncio.sleep(5)
                run = await client.evals.runs.retrieve(
                    eval_id=evaluation.id, run_id=run.id
                )
            async for item in client.evals.runs.output_items.list(
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
                    await client.evals.runs.cancel(eval_id=evaluation.id, run_id=run.id)
            finally:
                await client.evals.delete(eval_id=evaluation.id)


if __name__ == "__main__":
    asyncio.run(main())
