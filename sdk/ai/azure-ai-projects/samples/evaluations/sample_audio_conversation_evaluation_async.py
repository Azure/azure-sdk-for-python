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

    pip install "azure-ai-projects>=2.11.0" python-dotenv aiohttp

    Set these environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT - Project endpoint.
    2) FOUNDRY_MODEL_NAME - Audio-input judge deployment compatible with the evaluator.
    3) FOUNDRY_DATASET_ID - Optional existing JSONL dataset ID, not the WAV asset ID.
       If omitted, upload the bundled WAV and a one-row JSONL dataset using the
       project's default storage connection, then delete the created dataset versions.
       Existing datasets are not changed or deleted.
    Audio evaluators must be available and the judge must support audio input.
"""

import asyncio
import json
import os
from contextlib import AsyncExitStack
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
import time
from pprint import pprint
from uuid import uuid4

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
    dataset_id = os.environ.get("FOUNDRY_DATASET_ID")
    testing_criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name=metric,
            evaluator_name=f"builtin.{metric}_audio",
            evaluator_version="1",
            initialization_parameters={"deployment_name": os.environ["FOUNDRY_MODEL_NAME"]},
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
        AsyncExitStack() as cleanup,
    ):
        if not dataset_id:
            with TemporaryDirectory() as directory:
                folder = Path(directory) / "recordings"
                folder.mkdir()
                copyfile(
                    Path(__file__).parent / "data_folder" / "sample_evaluations_score_model_grader_with_audio.wav",
                    folder / "conversation.wav",
                )
                recording_name = f"sample-audio-{uuid4().hex}"
                recording = await project_client.datasets.upload_folder(
                    name=recording_name, version="1", folder=str(folder)
                )
                cleanup.push_async_callback(project_client.datasets.delete, name=recording_name, version="1")
                if not recording.id:
                    raise ValueError("Recording upload returned no dataset ID")
                row = {
                    "conversation_artifacts": {
                        "audio": {
                            "asset_id": recording.id.replace("/data/", "/datasets/"),
                            "asset_file_path": "conversation.wav",
                        }
                    }
                }
                jsonl = Path(directory) / "conversation.jsonl"
                jsonl.write_text(json.dumps(row) + "\n", encoding="utf-8")
                dataset_name = f"sample-audio-conversations-{uuid4().hex}"
                dataset = await project_client.datasets.upload_file(
                    name=dataset_name, version="1", file_path=str(jsonl)
                )
                cleanup.push_async_callback(project_client.datasets.delete, name=dataset_name, version="1")
                if not dataset.id:
                    raise ValueError("JSONL upload returned no dataset ID")
                dataset_id = dataset.id
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
                    raise TimeoutError(f"Evaluation run {run.id} did not finish within 600 seconds")
                await asyncio.sleep(5)
                run = await client.evals.runs.retrieve(eval_id=evaluation.id, run_id=run.id)
            async for item in client.evals.runs.output_items.list(eval_id=evaluation.id, run_id=run.id):
                pprint(item)
            if run.status != "completed":
                raise RuntimeError(f"Evaluation run {run.status}: {run.error}")
            if run.result_counts.errored:
                raise RuntimeError(f"{run.result_counts.errored} evaluation item(s) errored")
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
