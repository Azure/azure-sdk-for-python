# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates an evaluation dataset from an agent's recent conversation
    traces. The sample:

      1. Creates a `DataGenerationJob` (scenario=EVALUATION, type=traces) that
         reads spans from Application Insights for an existing agent within a
         time window and synthesizes question / answer pairs into a new
         versioned Dataset.
      2. Polls the job to completion and resolves the resulting `DatasetVersion`.
      3. Cleans up the generated dataset and the data generation job.

    The Traces source consumes existing telemetry, so no `model_options` are
    required — the service derives samples directly from the agent's traces.
    The agent must have at least one trace recorded within the configured
    look-back window or the job will succeed with zero generated samples.

USAGE:
    python sample_dataset_generation_job_traces_for_evaluation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_AGENT_NAME - Required. The name of an agent (Foundry Agent or
       OpenTelemetry-instrumented third-party agent) that has recent
       conversation traces in Application Insights.
    3) DATASET_NAME - Optional. Name to assign to the generated output dataset.
       Defaults to `traces-eval-sample`. The service caps the rendered output
       name at 50 characters, so keep custom values short — the sample appends
       a unique run id suffix.
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
    DatasetDataGenerationJobOutput,
    DatasetVersion,
    JobStatus,
    TracesDataGenerationJobOptions,
    TracesDataGenerationJobSource,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_AGENT_NAME"]
dataset_name = os.environ.get("DATASET_NAME", "traces-eval-sample")
traces_window_days = int(os.environ.get("FOUNDRY_TRACES_WINDOW_DAYS", "7"))
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Unique per-run output dataset name so repeated runs do not collide.
# Output names are capped at 50 characters by the service.
run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
output_dataset_name = f"{dataset_name}-{run_id}"
if len(output_dataset_name) > 50:
    raise ValueError(
        f"Output dataset name `{output_dataset_name}` exceeds the 50-character service limit. "
        f"Lower DATASET_NAME (currently `{dataset_name}`) so that `<DATASET_NAME>-<run id>` fits within 50 characters."
    )

# Trace look-back window: now - `traces_window_days` ... now.
end_time = datetime.now(tz=timezone.utc)
start_time = end_time - timedelta(days=traces_window_days)

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    # ------------------------------------------------------------------
    # 1. Submit a data generation job that reads agent traces.
    # ------------------------------------------------------------------
    print(f"Create a data generation job from traces for agent `{agent_name}` (window: {traces_window_days} day(s)).")
    job = DataGenerationJob(
        inputs=DataGenerationJobInputs(
            name=f"traces-eval-{run_id}",
            scenario=DataGenerationJobScenario.EVALUATION,
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
            ),
            output_options=DataGenerationJobOutputOptions(name=output_dataset_name),
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

    dataset: DatasetVersion = project_client.datasets.get(name=output_name, version=output_version)
    print(f"Generated dataset: name=`{dataset.name}` version=`{dataset.version}` id=`{dataset.id}`")
    if job.result is not None and job.result.generated_samples is not None:
        print(f"Generated samples: {job.result.generated_samples}")

    # ------------------------------------------------------------------
    # 2. Clean up.
    # ------------------------------------------------------------------
    print(f"Delete the generated dataset `{dataset.name}` v{dataset.version}.")
    project_client.datasets.delete(name=dataset.name or "", version=dataset.version or "")

    print(f"Delete the data generation job `{job.id}`.")
    project_client.beta.datasets.delete_generation_job(job_id=job.id)
