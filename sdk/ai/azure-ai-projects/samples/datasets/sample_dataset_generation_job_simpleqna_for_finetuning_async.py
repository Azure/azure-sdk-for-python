# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates supervised fine-tuning data from a plain-text reference document
    uploaded as an Azure OpenAI File. The sample:

      1. Uploads `simpleqna_seed_reference.txt` via the Azure OpenAI Files API
         (`purpose=user_data`) so it can be referenced by file id.
      2. Submits a `SupervisedFineTuningDataGenerationJobInputs` job (scenario
         `supervised_finetuning_preview`, generation type `simple_qna`) that
         synthesizes short-answer and long-answer question / answer pairs from
         the file content and emits them as training and validation JSONL files.
      3. Waits for job completion and prints every generated file output.
      4. Cleans up the generated fine-tuning files and the Azure OpenAI input file.

    `simple_qna` REQUIRES `model_options` — the service uses the configured LLM
    to synthesize the QnA pairs. Setting `train_split` triggers a split of
    the generated samples into two Azure OpenAI output files.

    Supervised fine-tuning data generation (scenario `supervised_finetuning_preview`),
    `question_types`, and Azure OpenAI file outputs are preview features. The client
    automatically sends the required `Foundry-Features: DataGenerationJobs=V1Preview`
    opt-in header on all data generation job operations.

USAGE:
    python sample_dataset_generation_job_simpleqna_for_finetuning_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.8.0" azure-identity openai python-dotenv aiohttp

    Keep `simpleqna_seed_reference.txt` in the same directory as this sample.

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of an Azure OpenAI model
       deployment used to synthesize the QnA samples. For `simple_qna` fine-tuning,
       the deployment must support the chat completions API (e.g. `gpt-4o`, `gpt-4.1`).
    3) DATASET_NAME - Optional. Name to assign to the generated output files
       (used as the file name prefix). Defaults to `simpleqna-finetuning-sample`.
       The service caps the rendered output name at 50 characters, so keep
       custom values short — the sample appends a unique run id suffix.
    4) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between status
       polls for the data generation job. Defaults to 10.
"""

import asyncio
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    DataGenerationModelOptions,
    FileDataGenerationJobOutput,
    FileDataGenerationJobSource,
    SimpleQnADataGenerationJobOptions,
    SimpleQnAFineTuningQuestionType,
    SupervisedFineTuningDataGenerationJobInputs,
    SupervisedFineTuningDataGenerationJobOutputTarget,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
dataset_name = os.environ.get("DATASET_NAME", "simpleqna-finetuning-sample")
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Unique per-run output name so repeated runs do not collide.
# Output names are capped at 50 characters by the service.
run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
output_name = f"{dataset_name}-{run_id}"
if len(output_name) > 50:
    raise ValueError(
        f"Output name `{output_name}` exceeds the 50-character service limit. "
        f"Lower DATASET_NAME (currently `{dataset_name}`) so that `<DATASET_NAME>-<run id>` fits within 50 characters."
    )

SEED_REFERENCE_PATH = Path(__file__).with_name("simpleqna_seed_reference.txt")


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):

        seed_file_id: Optional[str] = None
        generated_file_ids: List[str] = []

        try:
            # ------------------------------------------------------------------
            # 1. Upload the seed reference document as an Azure OpenAI file.
            # ------------------------------------------------------------------
            seed_filename = SEED_REFERENCE_PATH.name
            print(f"Upload the seed reference document as Azure OpenAI file `{seed_filename}`.")
            with SEED_REFERENCE_PATH.open("rb") as seed_stream:
                seed_file = await openai_client.files.create(
                    file=(seed_filename, seed_stream, "text/plain"),
                    purpose="user_data",
                )
            seed_file_id = seed_file.id
            print(f"Uploaded Azure OpenAI file (id: {seed_file.id}).")

            # Wait for the file to finish processing — the data generation service
            # rejects references to files that are not yet in the `processed` state.
            print("Wait for the Azure OpenAI file to be processed.", end="", flush=True)
            while seed_file.status not in ("processed", "error"):
                await asyncio.sleep(2)
                seed_file = await openai_client.files.retrieve(file_id=seed_file.id)
                print(".", end="", flush=True)
            print()
            if seed_file.status != "processed":
                raise RuntimeError(
                    f"Azure OpenAI file `{seed_file.id}` failed to process: status=`{seed_file.status}`."
                )

            # ------------------------------------------------------------------
            # 2. Submit a fine-tuning data generation job that consumes the file.
            # ------------------------------------------------------------------

            job = SupervisedFineTuningDataGenerationJobInputs(
                name=f"simpleqna-finetuning-{run_id}",
                sources=[
                    FileDataGenerationJobSource(
                        description="Synthetic primary care conversation reference (Azure OpenAI file).",
                        id=seed_file.id,
                    ),
                ],
                generation_configuration=SimpleQnADataGenerationJobOptions(
                    # For fine-tuning jobs, the service requires max_samples to be between 15 and 1000.
                    max_samples=15,
                    # `simple_qna` REQUIRES model_options.
                    model_options=DataGenerationModelOptions(model=model_name),
                    # Split generated samples 80% training / 20% validation.
                    train_split=0.8,
                    # Ask for both short-answer and long-answer questions.
                    question_types=[
                        SimpleQnAFineTuningQuestionType.SHORT_ANSWER,
                        SimpleQnAFineTuningQuestionType.LONG_ANSWER,
                    ],
                ),
                output_configuration=SupervisedFineTuningDataGenerationJobOutputTarget(name=output_name),
            )

            print("Begin creating a dataset generation job.")
            poller = await project_client.datasets.begin_create_generation_job(
                job=job,
                polling_interval=poll_interval_seconds,
            )

            print("Waiting for the dataset generation job to complete.")
            job_result = await poller.result()
            print(f"Data generation result: {job_result}")

            # ------------------------------------------------------------------
            # 3. Inspect the generated fine-tuning file outputs.
            # ------------------------------------------------------------------
            # `train_split=0.8` produces two Azure OpenAI files: a training partition
            # and a validation partition. Both are emitted as FileDataGenerationJobOutput
            # entries in `job_result.outputs`.
            file_outputs = [
                output for output in (job_result.outputs or []) if isinstance(output, FileDataGenerationJobOutput)
            ]
            if not file_outputs:
                raise RuntimeError("The data generation job did not produce any file outputs.")

            print(f"Generated {len(file_outputs)} fine-tuning file(s):")
            for output in file_outputs:
                if not output.id:
                    raise RuntimeError("A file output was returned without an id.")
                generated_file_ids.append(output.id)
                # Resolve the Azure OpenAI file to surface its real filename and size.
                file_info = await openai_client.files.retrieve(file_id=output.id)
                print(f"  - filename=`{file_info.filename}` id=`{output.id}` bytes={file_info.bytes}")
            if job_result.generated_samples is not None:
                print(f"Generated samples: {job_result.generated_samples}")

        finally:
            # ------------------------------------------------------------------
            # 4. Clean up (best effort, so partial failures do not leak resources).
            # ------------------------------------------------------------------
            # Delete the generated files.
            for generated_file_id in generated_file_ids:
                print(f"Delete the generated Azure OpenAI file `{generated_file_id}`.")
                try:
                    await openai_client.files.delete(file_id=generated_file_id)
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    print(f"  (warning) could not delete Azure OpenAI file `{generated_file_id}`: {exc}")

            if seed_file_id:
                print(f"Delete the Azure OpenAI input file `{seed_file_id}`.")
                try:
                    await openai_client.files.delete(file_id=seed_file_id)
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    print(f"  (warning) could not delete Azure OpenAI file `{seed_file_id}`: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
