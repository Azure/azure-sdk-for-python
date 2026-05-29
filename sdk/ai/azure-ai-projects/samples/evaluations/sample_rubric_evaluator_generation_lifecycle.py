# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end scenario showing the lifecycle of rubric evaluator generation
    jobs. The sample exercises:

      * `create_generation_job` with `operation_id` for idempotent re-submits.
      * `get_generation_job` to poll a single job to completion.
      * `list_generation_jobs` to enumerate recent jobs in the project.
      * `delete_generation_job` to remove a finished job record.
      * `delete_version` to remove the persisted evaluator that the job produced.

    `cancel_generation_job` is not exercised here - cancelling requires catching
    a job mid-flight and jobs usually finish in under two minutes.

    Note: `delete_version` cascades to delete the generation job record as well,
    so `delete_generation_job` may return 404 - that is expected and tolerated
    below.

USAGE:
    python sample_rubric_evaluator_generation_lifecycle.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of the model the generation job
       will use (e.g. `gpt-4o`, `gpt-4.1`).
    3) POLL_INTERVAL_SECONDS - Optional. Seconds to sleep between status polls.
       Defaults to 10.
"""

import os
import itertools
import time
import uuid
from datetime import datetime, timezone
from typing import cast

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import JobStatus, PageOrder

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Unique per-run name so repeated runs do not collide.
ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
short = uuid.uuid4().hex[:6]
evaluator_name = f"lifecycle-demo-{ts}-{short}"
operation_id = f"rubric-lifecycle-{short}"

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

# Shared job body used both for the initial create and the idempotency replay.
job_body = {
    "model": model_name,
    "name": "Lifecycle demo",
    "evaluator_name": evaluator_name,
    "evaluator_display_name": "Lifecycle demo",
    "evaluator_description": "Minimal job used to demonstrate the LRO + list/delete lifecycle.",
    "sources": [
        {
            "type": "Prompt",
            "description": "Inline application overview.",
            "prompt": "You are evaluating a simple Q&A assistant that answers factual questions clearly and concisely.",
        }
    ],
}

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    # 1. Create the generation job. `operation_id` makes the call idempotent -
    # re-submitting with the same id returns the existing job.
    job = project_client.beta.evaluators.create_generation_job(job=job_body, operation_id=operation_id)
    print(f"Created generation job `{job.id}`.")

    replay = project_client.beta.evaluators.create_generation_job(job=job_body, operation_id=operation_id)
    assert replay.id == job.id  # idempotent replay returns the same job

    # 2. Poll the job to completion.
    print(f"Waiting for job `{job.id}` to complete...")
    while job.status not in TERMINAL_STATUSES:
        time.sleep(poll_interval_seconds)
        job = project_client.beta.evaluators.get_generation_job(job.id)
    print(f"Job finished with status `{cast(JobStatus, job.status).value}`.")

    if job.status != JobStatus.SUCCEEDED:
        message = job.error.message if job.error is not None else "<no error message>"
        raise RuntimeError(f"Generation job ended with status `{cast(JobStatus, job.status).value}`: {message}")

    evaluator = job.result
    assert evaluator is not None
    print(f"Generated evaluator `{evaluator.name}` version `{evaluator.version}`.")

    # 3. List the 5 most recent generation jobs in this project.
    #    `limit` controls the page size; use `itertools.islice` to cap the total.
    print("Recent generation jobs:")
    for entry in itertools.islice(
        project_client.beta.evaluators.list_generation_jobs(limit=5, order=PageOrder.DESC), 5
    ):
        entry_name = entry.inputs.evaluator_name if entry.inputs is not None else "<unknown>"
        print(f"  - id=`{entry.id}` status=`{cast(JobStatus, entry.status).value}` evaluator_name=`{entry_name}`")

    # 4. Cancel a running job (not exercised here; the job above already completed).
    # cancelled = project_client.beta.evaluators.cancel_generation_job(some_running_job_id)

    # 5. Clean up. `delete_version` cascades to the generation job record, so
    # the explicit delete below may return 404.
    print("Cleaning up.")
    project_client.beta.evaluators.delete_version(name=evaluator.name, version=evaluator.version)
    try:
        project_client.beta.evaluators.delete_generation_job(job.id)
    except ResourceNotFoundError:
        pass  # already removed by the delete_version cascade
