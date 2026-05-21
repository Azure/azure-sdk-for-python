# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end scenario showing the full lifecycle of rubric evaluator
    generation jobs. The sample exercises:

      * `create_generation_job` with `operation_id` for idempotent re-submits.
      * `get_generation_job` to poll a single job to completion.
      * `list_generation_jobs` to enumerate recent jobs in the project.
      * `delete_generation_job` to remove a finished job record.
      * `delete_version` to remove the persisted evaluator that the job produced.

    `cancel_generation_job` is shown in a comment - cancelling requires catching
    a job mid-flight (jobs usually finish in under two minutes), so it is not
    exercised inline.

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
    2) FOUNDRY_MODEL_NAME - Required. The name of the LLM model deployment that
       the generation job will use (e.g. `gpt-4o`, `gpt-4.1`).
    3) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between status
       polls for the generation job. Defaults to 10.
"""

import os
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
            "prompt": (
                "You are evaluating a simple Q&A assistant that answers factual "
                "questions clearly and concisely."
            ),
        }
    ],
}

with (
    DefaultAzureCredential() as credential,
    # `allow_preview` and `api_version` are required for the evaluator
    # generation endpoints in this preview.
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
        allow_preview=True,
        api_version="2025-11-15-preview",
    ) as project_client,
):

    # ------------------------------------------------------------------
    # 1. Create the generation job.
    # ------------------------------------------------------------------
    # `operation_id` makes this call idempotent - re-running with the same id
    # returns the existing job instead of creating a duplicate. Useful for
    # retry-safe automation.
    print(f"Create generation job with operation_id `{operation_id}`.")
    job = project_client.beta.evaluators.create_generation_job(job=job_body, operation_id=operation_id)
    print(f"Created generation job `{job.id}` (status: `{cast(JobStatus, job.status).value}`).")

    # Re-issuing the same operation_id returns the SAME job rather than
    # starting a new one.
    replay = project_client.beta.evaluators.create_generation_job(job=job_body, operation_id=operation_id)
    assert replay.id == job.id, "operation_id should make create_generation_job idempotent"
    print(f"Idempotent replay returned the same id `{replay.id}`.")

    # ------------------------------------------------------------------
    # 2. Poll the job to completion.
    # ------------------------------------------------------------------
    print(f"Poll job `{job.id}` until it reaches a terminal state.", end="", flush=True)
    while job.status not in TERMINAL_STATUSES:
        time.sleep(poll_interval_seconds)
        job = project_client.beta.evaluators.get_generation_job(job.id)
        print(".", end="", flush=True)
    print()
    print(f"Final job status: `{cast(JobStatus, job.status).value}`.")

    if job.status != JobStatus.SUCCEEDED:
        message = job.error.message if job.error is not None else "<no error message>"
        raise RuntimeError(
            f"Generation job `{job.id}` ended with status `{cast(JobStatus, job.status).value}`: {message}"
        )

    evaluator = job.result
    print(f"Generated evaluator: name=`{evaluator.name}` version=`{evaluator.version}`.")

    # ------------------------------------------------------------------
    # 3. List recent generation jobs in this project.
    # ------------------------------------------------------------------
    # `PageOrder.DESC` returns the most recently created jobs first.
    print("List the 5 most recent generation jobs in this project:")
    recent = list(project_client.beta.evaluators.list_generation_jobs(limit=5, order=PageOrder.DESC))
    if not recent:
        print("  (no jobs returned)")
    for entry in recent:
        print(
            f"  - id=`{entry.id}` status=`{cast(JobStatus, entry.status).value}` "
            f"evaluator_name=`{entry.inputs.evaluator_name}`"
        )

    # ------------------------------------------------------------------
    # 4. Cancel (commented for reference).
    # ------------------------------------------------------------------
    # To cancel a job, call `cancel_generation_job` while it is still running.
    # The job above already completed, so the call is shown here only for
    # reference.
    #
    # cancelled = project_client.beta.evaluators.cancel_generation_job(some_running_job_id)
    # print(f"Cancelled: id=`{cancelled.id}` status=`{cast(JobStatus, cancelled.status).value}`.")

    # ------------------------------------------------------------------
    # 5. Clean up.
    # ------------------------------------------------------------------
    print(f"Delete evaluator `{evaluator.name}` version `{evaluator.version}`.")
    project_client.beta.evaluators.delete_version(name=evaluator.name, version=evaluator.version)

    # `delete_version` above cascades to remove the generation job record as
    # well; tolerate a 404 here.
    print(f"Delete generation job `{job.id}`.")
    try:
        project_client.beta.evaluators.delete_generation_job(job.id)
    except ResourceNotFoundError:
        print(f"  Job `{job.id}` was already removed by the delete_version cascade.")
