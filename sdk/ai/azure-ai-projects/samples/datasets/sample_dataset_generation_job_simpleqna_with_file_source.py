# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates an evaluation dataset from a multi-source `simple_qna` job that
    combines an Azure OpenAI File with an inline Prompt. The sample:

      1. Uploads a short Markdown reference document via the Azure OpenAI Files
         API (`purpose=user_data`) so it can be referenced by file id.
      2. Creates a `DataGenerationJob` (scenario=EVALUATION, type=simple_qna)
         with two sources: the uploaded `File` and a `Prompt` that adds an
         instruction to generate expert-level, high-difficulty questions.
      3. Polls the job to completion, resolves the generated `DatasetVersion`,
         and shows that the caller-supplied output `description` and `tags` are
         propagated onto the new dataset.
      4. Cleans up the generated dataset, the Azure OpenAI input file, and the data generation job.

    `simple_qna` REQUIRES `model_options` — the service uses the configured LLM
    to synthesize question / answer pairs from the combined sources.

    For `simple_qna` evaluation jobs the deployed model must support the
    Azure OpenAI Responses API. See the supported-model list:
    https://learn.microsoft.com/azure/foundry/openai/how-to/responses?tabs=python-key#model-support

USAGE:
    python sample_dataset_generation_job_simpleqna_with_file_source.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity openai python-dotenv

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

import io
import os
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
    DatasetVersion,
    FileDataGenerationJobSource,
    JobStatus,
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

# Reference document the sample uploads as an Azure OpenAI file. The service
# requires the file to contain at least 1 KB of content to generate QnA from.
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
EXPECTED_OUTPUT_TAGS = {"sample": "dataset-generation-simpleqna-with-file-source", "difficulty": "expert"}

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # ------------------------------------------------------------------
    # 1. Upload the seed reference document as an Azure OpenAI file.
    # ------------------------------------------------------------------
    seed_filename = f"widgets-gizmos-seed-{run_id}.md"
    print(f"Upload the seed reference document as Azure OpenAI file `{seed_filename}`.")
    seed_file = openai_client.files.create(
        file=(seed_filename, io.BytesIO(SEED_REFERENCE_DOCUMENT.encode("utf-8"))),
        purpose="user_data",
    )
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
    print("Create a multi-source data generation job (File + Prompt).")
    job = DataGenerationJob(
        inputs=DataGenerationJobInputs(
            name=f"simpleqna-multisource-{run_id}",
            scenario=DataGenerationJobScenario.EVALUATION,
            sources=[
                FileDataGenerationJobSource(
                    description="Widgets & Gizmos product / operations reference (Azure OpenAI file).",
                    id=seed_file.id,
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
    print(f"Delete the generated dataset `{dataset.name}` v{dataset.version}.")
    project_client.datasets.delete(name=dataset.name or "", version=dataset.version or "")

    print(f"Delete the Azure OpenAI input file `{seed_file.id}`.")
    openai_client.files.delete(file_id=seed_file.id)

    print(f"Delete the data generation job `{job.id}`.")
    project_client.beta.datasets.delete_generation_job(job_id=job.id)
