# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates an evaluation dataset from a multi-source `simple_qna` job that
    combines a seed Dataset with an inline Prompt. The sample:

      1. Uploads a short Markdown reference document as a new versioned
         Dataset that will act as the seed (product / operations reference).
      2. Creates a `DataGenerationJob` (scenario=EVALUATION, type=simple_qna)
         with two sources: the seed `Dataset` and a `Prompt` that adds an
         instruction to generate expert-level, high-difficulty questions.
      3. Polls the job to completion, resolves the generated `DatasetVersion`,
         and shows that the caller-supplied output `description` and `tags` are
         propagated onto the new dataset.
      4. Cleans up the seed dataset and the data generation job.

    `simple_qna` REQUIRES `model_options` — the service uses the configured LLM
    to synthesize question / answer pairs from the combined sources.

USAGE:
    python sample_dataset_generation_job_simpleqna_with_dataset_source.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of an LLM model deployment used to
       synthesize the QnA samples (e.g. `gpt-4o`, `gpt-5`).
    3) DATASET_NAME - Optional. Name to assign to the generated output dataset.
       Defaults to `simpleqna-multisource-sample`. The service caps the rendered
       output name at 50 characters, so keep custom values short — the sample
       appends a unique run id suffix.
    4) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between status
       polls for the data generation job. Defaults to 10.
"""

import os
import tempfile
import time
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DataGenerationJob,
    DataGenerationJobInputs,
    DataGenerationJobOutputOptions,
    DataGenerationJobScenario,
    DataGenerationModelOptions,
    DatasetDataGenerationJobOutput,
    DatasetDataGenerationJobSource,
    DatasetVersion,
    JobStatus,
    PromptDataGenerationJobSource,
    SimpleQnADataGenerationJobOptions,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
dataset_name = os.environ.get("DATASET_NAME", "simpleqna-multisource-sample")
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Unique per-run resource names so repeated runs do not collide.
# The service rejects output names longer than 50 characters.
run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
seed_dataset_name = f"widgets-gizmos-seed-{run_id}"
output_dataset_name = f"{dataset_name}-{run_id}"
if len(output_dataset_name) > 50:
    raise ValueError(
        f"Output dataset name `{output_dataset_name}` exceeds the 50-character service limit. "
        f"Lower DATASET_NAME (currently `{dataset_name}`) so that `<DATASET_NAME>-<run id>` fits within 50 characters."
    )

# Reference document the sample uploads as the seed Dataset. Keep this >= 1 KB
# so the service has enough material to synthesize meaningful QnA pairs.
SEED_REFERENCE_DOCUMENT = """# Widgets and Gizmos Reference

## Products
- Widget: blue, manufactured at Factory 7 in Acme, carbon-fiber, rated to 80 C, sold in packs of 4, 250 g each.
- Gizmo: red, manufactured at Factory 12 in Bedrock, carbon-fiber, rated to 80 C, sold individually, 1.2 kg each.
- Sprocket: green, manufactured at Factory 3 in Acme, stainless steel, rated to 200 C, sold individually, 500 g each.

## Operations
- Factory operates weekdays 0700-1900 local time.
- Closed on public holidays, except for the annual maintenance run on December 27.
- ISO 9001 certified; audited annually by an independent third party.
- Quality control samples every 100th unit and runs full destructive testing on every 5000th unit.

## Customer support
- Warranty claims: email support@example.com with the serial number printed on the underside of the product.
- Returns: accepted within 30 days if unopened; opened items are eligible for repair only.
- Bulk orders (50+ units): contact sales@example.com for volume pricing and an extended 90-day return window.
- Replacement parts: orderable directly from the support portal using the original order number.

## Pricing and SLAs
- Widget pack: USD 24.99 per 4-pack; free shipping on orders over USD 75.
- Gizmo unit: USD 49.99; free shipping on orders over USD 75.
- Sprocket unit: USD 14.99; ships from regional warehouses in 1-2 business days.
- Standard support response: within one business day. Priority support response: within four hours.
"""

EXPECTED_OUTPUT_DESCRIPTION = "Expert-level QnA pairs generated from the Widgets & Gizmos reference."
EXPECTED_OUTPUT_TAGS = {"sample": "dataset-generation-simpleqna-with-dataset-source", "difficulty": "expert"}

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    # ------------------------------------------------------------------
    # 1. Upload the seed reference document as a versioned Dataset.
    # ------------------------------------------------------------------
    print(f"Upload the seed reference document as dataset `{seed_dataset_name}` v1.")
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write(SEED_REFERENCE_DOCUMENT)
        seed_local_path = tmp.name
    try:
        seed_dataset = project_client.datasets.upload_file(
            name=seed_dataset_name,
            version="1",
            file_path=seed_local_path,
        )
    finally:
        os.remove(seed_local_path)
    print(f"Uploaded seed dataset (id: {seed_dataset.id}).")

    # ------------------------------------------------------------------
    # 2. Submit a multi-source SimpleQnA data generation job.
    # ------------------------------------------------------------------
    # Two sources are combined for a single job:
    #   - The Dataset source contributes the source material (the reference
    #     document uploaded above).
    #   - The Prompt source contributes a steering instruction (difficulty).
    print("Create a multi-source data generation job (Dataset + Prompt).")
    job = DataGenerationJob(
        inputs=DataGenerationJobInputs(
            name=f"simpleqna-multisource-{run_id}",
            scenario=DataGenerationJobScenario.EVALUATION,
            sources=[
                DatasetDataGenerationJobSource(
                    description="Widgets & Gizmos product / operations reference.",
                    name=seed_dataset.name or "",
                    version=seed_dataset.version or "",
                ),
                PromptDataGenerationJobSource(
                    description="Specifies the question difficulty for SimpleQnA generation.",
                    prompt="Generate expert-level questions of high difficulty.",
                ),
            ],
            options=SimpleQnADataGenerationJobOptions(
                # Service requires max_samples to be between 15 and 1000.
                max_samples=15,
                # `simple_qna` REQUIRES model_options.
                model_options=DataGenerationModelOptions(model=model_name),
            ),
            output_options=DataGenerationJobOutputOptions(
                name=output_dataset_name,
                description=EXPECTED_OUTPUT_DESCRIPTION,
                tags=EXPECTED_OUTPUT_TAGS,
            ),
        ),
    )
    job = project_client.beta.datasets.create_generation_job(job=job)
    print(f"Created data generation job `{job.id}` (status: `{job.status}`).")

    print(f"Poll job `{job.id}` until it reaches a terminal state.", end="", flush=True)
    while True:
        job = project_client.beta.datasets.get_generation_job(job_id=job.id)
        if job.status in TERMINAL_STATUSES:
            break
        time.sleep(poll_interval_seconds)
        print(".", end="", flush=True)
    print()
    print(f"Final job status: `{job.status}`.")

    if job.status != JobStatus.SUCCEEDED:
        message = job.error.message if job.error is not None else "<no error message>"
        raise RuntimeError(f"Job `{job.id}` ended with status `{job.status}`: {message}")

    # Locate the Dataset output produced by the job.
    output_name: str = ""
    output_version: str = ""
    for output in (job.result.outputs if job.result is not None else None) or []:
        if isinstance(output, DatasetDataGenerationJobOutput):
            output_name = output.name or ""
            output_version = output.version or ""
            break
    if not output_name or not output_version:
        raise RuntimeError(f"Job `{job.id}` did not produce a dataset output.")

    # ------------------------------------------------------------------
    # 3. Inspect the generated dataset and show metadata propagation.
    # ------------------------------------------------------------------
    # The caller-supplied output `description` and `tags` are persisted onto
    # the generated dataset. The service also automatically adds a
    # `data_generation_job_id` tag pointing back at this job.
    dataset: DatasetVersion = project_client.datasets.get(name=output_name, version=output_version)
    print(f"Generated dataset: name=`{dataset.name}` version=`{dataset.version}` id=`{dataset.id}`")
    print(f"  description: {dataset.description}")
    print(f"  tags:        {dataset.tags}")
    if job.result is not None and job.result.generated_samples is not None:
        print(f"Generated samples: {job.result.generated_samples}")

    # ------------------------------------------------------------------
    # 4. Clean up.
    # ------------------------------------------------------------------
    print(f"Delete the seed dataset `{seed_dataset.name}` v{seed_dataset.version}.")
    project_client.datasets.delete(name=seed_dataset.name or "", version=seed_dataset.version or "")

    print(f"Delete the data generation job `{job.id}`.")
    project_client.beta.datasets.delete_generation_job(job_id=job.id)
