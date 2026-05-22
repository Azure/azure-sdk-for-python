# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates supervised fine-tuning data from a Markdown reference document
    uploaded as an Azure OpenAI File. The sample:

      1. Uploads a short reference document via the Azure OpenAI Files API
         (`purpose=user_data`) so it can be referenced by file id.
      2. Creates a `DataGenerationJob` (scenario=SUPERVISED_FINETUNING,
         type=simple_qna) that synthesizes short-answer and long-answer
         question / answer pairs from the file content and emits them as
         training and validation JSONL files.
      3. Polls the job to completion and prints every generated file output.
      4. Cleans up the generated fine-tuning files, the Azure OpenAI input file, and the data generation job.

    `simple_qna` REQUIRES `model_options` — the service uses the configured LLM
    to synthesize the QnA pairs. Setting `train_split` triggers a split of
    the generated samples into two Azure OpenAI output files.

USAGE:
    python sample_dataset_generation_job_simpleqna_for_finetuning.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity openai python-dotenv

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
    FileDataGenerationJobOutput,
    FileDataGenerationJobSource,
    JobStatus,
    SimpleQnADataGenerationJobOptions,
    SimpleQnAFineTuningQuestionType,
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
    # 2. Submit a fine-tuning data generation job that consumes the file.
    # ------------------------------------------------------------------
    print("Create a fine-tuning data generation job from the Azure OpenAI file.")
    job = DataGenerationJob(
        inputs=DataGenerationJobInputs(
            name=f"simpleqna-finetuning-{run_id}",
            scenario=DataGenerationJobScenario.SUPERVISED_FINETUNING,
            sources=[
                FileDataGenerationJobSource(
                    description="Widgets & Gizmos product / operations reference (Azure OpenAI file).",
                    id=seed_file.id,
                ),
            ],
            options=SimpleQnADataGenerationJobOptions(
                # Service requires max_samples to be between 15 and 1000.
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
            output_options=DataGenerationJobOutputOptions(name=output_name),
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

    # ------------------------------------------------------------------
    # 3. Inspect the generated fine-tuning file outputs.
    # ------------------------------------------------------------------
    # `train_split=0.8` produces two Azure OpenAI files: a training partition
    # and a validation partition. Both are emitted as FileDataGenerationJobOutput
    # entries in `job.result.outputs`.
    file_outputs = [
        output
        for output in ((job.result.outputs if job.result is not None else None) or [])
        if isinstance(output, FileDataGenerationJobOutput)
    ]
    if not file_outputs:
        raise RuntimeError(f"Job `{job.id}` did not produce any file outputs.")

    print(f"Generated {len(file_outputs)} fine-tuning file(s):")
    for output in file_outputs:
        if not output.id:
            raise RuntimeError(f"Job `{job.id}` returned a file output without an id.")
        # Resolve the Azure OpenAI file to surface its real filename and size.
        file_info = openai_client.files.retrieve(file_id=output.id)
        print(f"  - filename=`{file_info.filename}` id=`{output.id}` bytes={file_info.bytes}")
    if job.result is not None and job.result.generated_samples is not None:
        print(f"Generated samples: {job.result.generated_samples}")

    # ------------------------------------------------------------------
    # 4. Clean up.
    # ------------------------------------------------------------------
    for output in file_outputs:
        print(f"Delete the generated Azure OpenAI file `{output.id}`.")
        openai_client.files.delete(file_id=output.id)

    print(f"Delete the Azure OpenAI input file `{seed_file.id}`.")
    openai_client.files.delete(file_id=seed_file.id)

    print(f"Delete the data generation job `{job.id}`.")
    project_client.beta.datasets.delete_generation_job(job_id=job.id)
