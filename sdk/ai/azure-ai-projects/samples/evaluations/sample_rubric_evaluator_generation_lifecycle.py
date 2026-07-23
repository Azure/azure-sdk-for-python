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
        returns `LROPoller[EvaluatorVersion]` — the SDK polls automatically and
        `.result()` blocks until the job reaches a terminal state.
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
    # 1. Start the generation job LRO. `operation_id` makes the call idempotent -
    # re-submitting with the same id returns a poller attached to the existing job.
    poller = project_client.beta.evaluators.begin_create_generation_job(
        job=job_body, operation_id=operation_id, polling_interval=poll_interval_seconds
    )
    print("Generation job started; LRO polling in progress.")

    # Idempotency: a second call with the same operation_id attaches to the same job.
    replay_poller = project_client.beta.evaluators.begin_create_generation_job(
        job=job_body, operation_id=operation_id, polling_interval=poll_interval_seconds
    )

    # 2. Block until the LRO finishes. The SDK polls automatically; `.result()` returns
    # the produced EvaluatorVersion once the job reaches a terminal state.
    print("Waiting for the generation job to complete (polling is handled by the SDK)...")
    evaluator: EvaluatorVersion = poller.result()
    print(f"Generated evaluator `{evaluator.name}` version `{evaluator.version}` "
          f"(job `{evaluator.generation_job_id}`).")

    # Verify the idempotency: the replay poller resolves to the same underlying job.
    replay_evaluator: EvaluatorVersion = replay_poller.result()
    assert replay_evaluator.generation_job_id == evaluator.generation_job_id

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
