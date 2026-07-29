# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end scenario showing the lifecycle of rubric evaluator generation
    jobs. The sample exercises:

      * `begin_create_generation_job` with `operation_id` for idempotent re-submits;
                returns `LROPoller[EvaluatorVersion]`, whose status is reported until
                the job reaches a terminal state.
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

    pip install "azure-ai-projects>=2.4.0" azure-identity python-dotenv

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
from azure.ai.projects.models import (
    EvaluatorGenerationInputs,
    EvaluatorGenerationJob,
    EvaluatorVersion,
    JobStatus,
    PageOrder,
    PromptEvaluatorGenerationJobSource,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

# Unique per-run name so repeated runs do not collide.
ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
short = uuid.uuid4().hex[:6]
evaluator_name = f"lifecycle-demo-{ts}-{short}"
operation_id = f"rubric-lifecycle-{short}"

# Shared job used both for the initial create and the idempotency replay.
job_body = EvaluatorGenerationJob(
    inputs=EvaluatorGenerationInputs(
        model=model_name,
        evaluator_name=evaluator_name,
        evaluator_display_name="Lifecycle demo",
        evaluator_description="Minimal job used to demonstrate the LRO + list/delete lifecycle.",
        sources=[
            PromptEvaluatorGenerationJobSource(
                description="Inline application overview.",
                prompt="You are evaluating a simple Q&A assistant that answers factual questions clearly and concisely.",
            ),
        ],
    ),
)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    # 1. Create the generation job. `operation_id` makes the call idempotent -
    # re-submitting with the same id returns the existing job.
    created_jobs: list[EvaluatorGenerationJob] = []

    def capture_created_job(response):
        created_jobs.append(EvaluatorGenerationJob(response.http_response.json()))

    # Alternatively, append `.result()` to block while the SDK handles polling.
    project_client.beta.evaluators.begin_create_generation_job(
        job=job_body,
        operation_id=operation_id,
        polling=False,
        raw_response_hook=capture_created_job,
    )
    if not created_jobs:
        raise RuntimeError("The create operation did not return a generation job.")
    job = created_jobs[0]
    print(f"Created job: id={job.id}, status={job.status}")

    # Idempotency: a second call with the same operation_id returns the same job.
    replay_job = project_client.beta.evaluators.get_generation_job(job.id)
    assert replay_job.id == job.id

    # 2. Poll until the job reaches a terminal state.
    print(f"Polling job `{job.id}` to completion...", end="", flush=True)
    while job.status not in TERMINAL_STATUSES:
        time.sleep(poll_interval_seconds)
        job = project_client.beta.evaluators.get_generation_job(job.id)
        print(".", end="", flush=True)
    print()
    print(f"Final job status: `{job.status}`.")

    if job.status != JobStatus.SUCCEEDED:
        message = job.error.message if job.error else "<no error message>"
        raise RuntimeError(f"Generation job `{job.id}` ended with status `{job.status}`: {message}")
    if job.result is None:
        raise RuntimeError(f"Generation job `{job.id}` completed without a result.")
    evaluator: EvaluatorVersion = job.result
    print(
        f"Generated evaluator `{evaluator.name}` version `{evaluator.version}` "
        f"(job `{evaluator.generation_job_id}`)."
    )

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
        if evaluator.generation_job_id is not None:
            project_client.beta.evaluators.delete_generation_job(evaluator.generation_job_id)
    except ResourceNotFoundError:
        pass  # already removed by the delete_version cascade
