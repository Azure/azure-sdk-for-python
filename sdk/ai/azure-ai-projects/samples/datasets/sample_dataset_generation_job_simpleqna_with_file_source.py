# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates an evaluation dataset from a multi-source `simple_qna` job that
    combines an Azure OpenAI File with an inline Prompt. The sample:

      1. Uploads `simpleqna_seed_reference.txt` via the Azure OpenAI Files
         API (`purpose=user_data`) so it can be referenced by file id.
      2. Submits an `EvaluationDataGenerationJobInputs` job (scenario `evaluation`,
         generation type `simple_qna`) with two sources: the uploaded `File` and a
         `Prompt` that adds an instruction to generate expert-level,
         high-difficulty questions.
      3. Polls the job to completion, resolves the generated `DatasetVersion`,
         and shows that the caller-supplied output `description` and `tags` are
         propagated onto the new dataset.
      4. Cleans up the generated dataset and the Azure OpenAI input file.

    `simple_qna` REQUIRES `model_options` — the service uses the configured LLM
    to synthesize question / answer pairs from the combined sources.

    For `simple_qna` evaluation jobs the deployed model must support the
    Azure OpenAI Responses API. See the supported-model list:
    https://learn.microsoft.com/azure/foundry/openai/how-to/responses?tabs=python-key#model-support

USAGE:
    python sample_dataset_generation_job_simpleqna_with_file_source.py

    Before running the sample:

    pip install "azure-ai-projects>=2.8.0" azure-identity openai python-dotenv

    Keep `simpleqna_seed_reference.txt` in the same directory as this sample.

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of an Azure OpenAI model
       deployment used to synthesize the QnA samples. For `simple_qna` evaluation,
       choose a Responses-API capable model (see the link in the description).
    3) DATASET_NAME - Optional. Name to assign to the generated output dataset.
       Defaults to `simpleqna-file-source-sample`. The service caps the rendered
       output name at 50 characters, so keep custom values short — the sample
       appends a unique run id suffix.
    4) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between status
       polls for the data generation job. Defaults to 10.
"""

import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DataGenerationModelOptions,
    DatasetDataGenerationJobOutput,
    DatasetVersion,
    EvaluationDataGenerationJobInputs,
    EvaluationDataGenerationJobOutputTarget,
    FileDataGenerationJobSource,
    PromptDataGenerationJobSource,
    SimpleQnADataGenerationJobOptions,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
dataset_name = os.environ.get("DATASET_NAME", "simpleqna-file-source-sample")
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Unique per-run resource names so repeated runs do not collide.
# Output names are capped at 50 characters by the service.
run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
output_dataset_name = f"{dataset_name}-{run_id}"
if len(output_dataset_name) > 50:
    raise ValueError(
        f"Output dataset name `{output_dataset_name}` exceeds the 50-character service limit. "
        f"Lower DATASET_NAME (currently `{dataset_name}`) so that `<DATASET_NAME>-<run id>` fits within 50 characters."
    )

SEED_REFERENCE_PATH = Path(__file__).with_name("simpleqna_seed_reference.txt")

EXPECTED_OUTPUT_DESCRIPTION = "QnA pairs generated from synthetic primary care conversations."
EXPECTED_OUTPUT_TAGS = {
    "sample": "dataset-generation-simpleqna-with-file-source",
    "difficulty": "expert",
}

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    seed_file_id: Optional[str] = None
    dataset: Optional[DatasetVersion] = None

    try:
        # ------------------------------------------------------------------
        # 1. Upload the seed reference document as an Azure OpenAI file.
        # ------------------------------------------------------------------
        seed_filename = SEED_REFERENCE_PATH.name
        print(f"Upload the seed reference document as Azure OpenAI file `{seed_filename}`.")
        with SEED_REFERENCE_PATH.open("rb") as seed_stream:
            seed_file = openai_client.files.create(
                file=(seed_filename, seed_stream, "text/plain"),
                purpose="user_data",
            )
        seed_file_id = seed_file.id
        print(f"Uploaded Azure OpenAI file (id: {seed_file.id}).")

        # Wait for the file to finish processing — the data generation service
        # rejects references to files that are not yet in the `processed` state.
        print("Wait for the Azure OpenAI file to be processed.", end="", flush=True)
        while seed_file.status not in ("processed", "error"):
            time.sleep(2)
            seed_file = openai_client.files.retrieve(file_id=seed_file.id)
            print(".", end="", flush=True)
        print()
        if seed_file.status != "processed":
            raise RuntimeError(f"Azure OpenAI file `{seed_file.id}` failed to process: status=`{seed_file.status}`.")

        # ------------------------------------------------------------------
        # 2. Submit a multi-source SimpleQnA data generation job.
        # ------------------------------------------------------------------
        # Two sources are combined for a single job:
        #   - The File source contributes the source material (the reference
        #     document uploaded above).
        #   - The Prompt source contributes a steering instruction (difficulty).
        job = EvaluationDataGenerationJobInputs(
            name=f"simpleqna-multisource-{run_id}",
            sources=[
                FileDataGenerationJobSource(
                    description="Synthetic primary care conversation reference (Azure OpenAI file).",
                    id=seed_file.id,
                ),
                PromptDataGenerationJobSource(
                    description="Specifies the question difficulty for SimpleQnA generation.",
                    prompt="Generate expert-level questions of high difficulty.",
                ),
            ],
            generation_configuration=SimpleQnADataGenerationJobOptions(
                # For evaluation jobs, the service requires max_samples to be between 1 and 1000.
                max_samples=15,
                # `simple_qna` REQUIRES model_options.
                model_options=DataGenerationModelOptions(model=model_name),
            ),
            output_configuration=EvaluationDataGenerationJobOutputTarget(
                name=output_dataset_name,
                description=EXPECTED_OUTPUT_DESCRIPTION,
                tags=EXPECTED_OUTPUT_TAGS,
            ),
        )

        print("Begin creating a dataset generation job.")
        poller = project_client.datasets.begin_create_generation_job(
            job=job,
            polling_interval=poll_interval_seconds,
        )

        # Optional: While SDK is polling, periodically print the job status until the job is complete
        print("Periodically check job status:")
        while not poller.done():
            print(f"\tstatus=`{poller.status()}`")
            time.sleep(poll_interval_seconds)

        # Since done() is true, result() returns the final deserialized job result without
        # waiting further. It also propagates any LRO polling exception.
        job_result = poller.result()
        print(f"Final LRO status: `{poller.status()}`.")
        print(f"Data generation result: {job_result}")

        # Locate the Dataset output produced by the job.
        output_name: str = ""
        output_version: str = ""
        for output in job_result.outputs or []:
            if isinstance(output, DatasetDataGenerationJobOutput):
                output_name = output.name or ""
                output_version = output.version or ""
                break
        if not output_name or not output_version:
            raise RuntimeError("The data generation job did not produce a dataset output.")

        # ------------------------------------------------------------------
        # 3. Inspect the generated dataset and show metadata propagation.
        # ------------------------------------------------------------------
        # The caller-supplied output `description` and `tags` are persisted onto
        # the generated dataset. The service also automatically adds a
        # `data_generation_job_id` tag pointing back at this job.
        dataset = project_client.datasets.get(name=output_name, version=output_version)
        print(f"Generated dataset: name=`{dataset.name}` version=`{dataset.version}` id=`{dataset.id}`")
        print(f"  description: {dataset.description}")
        print(f"  tags:        {dataset.tags}")
        if job_result.generated_samples is not None:
            print(f"Generated samples: {job_result.generated_samples}")

    finally:
        # ------------------------------------------------------------------
        # 4. Clean up (best effort, so partial failures do not leak resources).
        # ------------------------------------------------------------------
        # Delete the generated dataset.
        if dataset is not None:
            print(f"Delete the generated dataset `{dataset.name}` v{dataset.version}.")
            try:
                project_client.datasets.delete(name=dataset.name or "", version=dataset.version or "")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"  (warning) could not delete dataset: {exc}")

        if seed_file_id:
            print(f"Delete the Azure OpenAI input file `{seed_file_id}`.")
            try:
                openai_client.files.delete(file_id=seed_file_id)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"  (warning) could not delete Azure OpenAI file `{seed_file_id}`: {exc}")
