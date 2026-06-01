# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates supervised fine-tuning data from an agent's recent
    conversation traces. The sample:

      1. Creates a `DataGenerationJob` (scenario=SUPERVISED_FINETUNING,
         type=traces) that reads spans from Application Insights for an
         existing agent within a time window and emits ready-to-use fine-tuning
         JSONL files split into training and validation partitions.
      2. Polls the job to completion and prints every generated file output.
      3. Cleans up the generated fine-tuning files and the data generation job.

    Setting `train_split` triggers a split of the generated samples into two
    Azure OpenAI files — a training partition and a validation partition.
    The Traces source consumes existing telemetry, so no `model_options` are
    required.

USAGE:
    python sample_dataset_generation_job_traces_for_finetuning.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_AGENT_NAME - Required. The name of an agent (Foundry Agent or
       OpenTelemetry-instrumented third-party agent) that has recent
       conversation traces in Application Insights.
    3) DATASET_NAME - Optional. Name to assign to the generated output files
       (used as the file name prefix). Defaults to `traces-finetuning-sample`.
       The service caps the rendered output name at 50 characters, so keep
       custom values short — the sample appends a unique run id suffix.
    4) FOUNDRY_TRACES_WINDOW_DAYS - Optional. How far back, in days, to look for
       agent traces. Defaults to 7.
    5) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between status
       polls for the data generation job. Defaults to 10.
"""

import os
import time
import uuid
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DataGenerationJob,
    DataGenerationJobInputs,
    DataGenerationJobOutputOptions,
    DataGenerationJobScenario,
    FileDataGenerationJobOutput,
    JobStatus,
    TracesDataGenerationJobOptions,
    TracesDataGenerationJobSource,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_AGENT_NAME"]
dataset_name = os.environ.get("DATASET_NAME", "traces-finetuning-sample")
traces_window_days = int(os.environ.get("FOUNDRY_TRACES_WINDOW_DAYS", "7"))
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

# Trace look-back window: now - `traces_window_days` ... now.
end_time = datetime.now(tz=timezone.utc)
start_time = end_time - timedelta(days=traces_window_days)

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # ------------------------------------------------------------------
    # 1. Submit a fine-tuning data generation job that reads agent traces.
    # ------------------------------------------------------------------
    print(
        f"Create a fine-tuning data generation job from traces for agent `{agent_name}` (window: {traces_window_days} day(s))."
    )
    job = DataGenerationJob(
        inputs=DataGenerationJobInputs(
            name=f"traces-finetuning-{run_id}",
            scenario=DataGenerationJobScenario.SUPERVISED_FINETUNING,
            sources=[
                TracesDataGenerationJobSource(
                    description="Application Insights conversation traces for the Foundry agent.",
                    agent_name=agent_name,
                    start_time=start_time,
                    end_time=end_time,
                ),
            ],
            options=TracesDataGenerationJobOptions(
                # Service requires max_samples to be between 15 and 1000.
                max_samples=15,
                # Split generated samples 80% training / 20% validation.
                train_split=0.8,
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
    # 2. Inspect the generated fine-tuning file outputs.
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
    # 3. Clean up.
    # ------------------------------------------------------------------
    for output in file_outputs:
        print(f"Delete the generated Azure OpenAI file `{output.id}`.")
        openai_client.files.delete(file_id=output.id)

    print(f"Delete the data generation job `{job.id}`.")
    project_client.beta.datasets.delete_generation_job(job_id=job.id)
