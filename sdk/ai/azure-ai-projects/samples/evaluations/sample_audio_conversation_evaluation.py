# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Evaluate a recorded voice conversation with an audio-capable evaluator and
    judge. The recording is already registered as a project dataset asset.
    The service retrieves it from conversation_artifacts.audio; no local audio
    path is sent to the evaluator by the client.

    Requires service support for input_modality and a published audio evaluator.
    This sample scores completed recordings, not live audio streams.

USAGE:
    python sample_audio_conversation_evaluation.py

    pip install "azure-ai-projects>=2.8.0" python-dotenv

    Set these environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT - Project endpoint.
    2) FOUNDRY_MODEL_NAME - Audio-input judge deployment compatible with the evaluator.
    3) FOUNDRY_AUDIO_EVALUATOR_NAME - Published audio evaluator name.
       This sample uses an evaluator configured with deployment_name.
    4) FOUNDRY_AUDIO_ASSET_ID - Versioned project dataset asset containing the recording.
    5) FOUNDRY_AUDIO_ASSET_FILE_PATH - Recording's relative path within that asset.
    6) FOUNDRY_AUDIO_EVALUATOR_VERSION - Optional evaluator version; otherwise latest.
"""

import os
import time
from pprint import pprint

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import TestingCriterionAzureAIEvaluator
from openai.types.eval_create_params import DataSourceConfigCustom
from openai.types.evals import RunCreateResponse, RunRetrieveResponse
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
)


def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    recording: dict[str, object] = {
        "conversation_artifacts": {
            "audio": {
                "asset_id": os.environ["FOUNDRY_AUDIO_ASSET_ID"],
                "asset_file_path": os.environ["FOUNDRY_AUDIO_ASSET_FILE_PATH"],
            }
        }
    }
    criterion = TestingCriterionAzureAIEvaluator(
        type="azure_ai_evaluator",
        name="audio_conversation",
        evaluator_name=os.environ["FOUNDRY_AUDIO_EVALUATOR_NAME"],
        initialization_parameters={"deployment_name": os.environ["FOUNDRY_MODEL_NAME"]},
    )
    if version := os.environ.get("FOUNDRY_AUDIO_EVALUATOR_VERSION"):
        criterion["evaluator_version"] = version

    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
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
                }
            },
            "required": ["conversation_artifacts"],
        },
        include_sample_schema=False,
    )
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):
        evaluation = client.evals.create(
            name="Recorded audio conversation evaluation",
            data_source_config=data_source_config,
            testing_criteria=[criterion],
        )
        run: RunCreateResponse | RunRetrieveResponse | None = None
        terminal_states = ("completed", "failed", "cancelled", "canceled")
        try:
            run = client.evals.runs.create(
                eval_id=evaluation.id,
                data_source=CreateEvalJSONLRunDataSourceParam(
                    type="jsonl",
                    source={"type": "file_content", "content": [{"item": recording}]},
                ),
                extra_body={
                    "evaluation_level": "conversation",
                    "input_modality": "audio",
                },
            )
            print(f"Evaluation run created: {run.id}")
            deadline = time.monotonic() + 600
            while run.status not in terminal_states:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Evaluation run {run.id} did not finish within 600 seconds")
                time.sleep(5)
                run = client.evals.runs.retrieve(eval_id=evaluation.id, run_id=run.id)
            for item in client.evals.runs.output_items.list(eval_id=evaluation.id, run_id=run.id):
                pprint(item)
            if run.status != "completed":
                raise RuntimeError(f"Evaluation run {run.status}: {run.error}")
            if run.result_counts.errored:
                raise RuntimeError(f"{run.result_counts.errored} evaluation item(s) errored")
            print(f"Result counts: {run.result_counts}")
        finally:
            if run is not None and run.status not in terminal_states:
                client.evals.runs.cancel(eval_id=evaluation.id, run_id=run.id)
            client.evals.delete(eval_id=evaluation.id)


if __name__ == "__main__":
    main()
