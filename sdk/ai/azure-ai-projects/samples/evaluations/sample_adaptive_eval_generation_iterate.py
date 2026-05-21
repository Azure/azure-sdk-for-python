# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end scenario showing the human-in-the-loop iteration workflow for
    adaptive evaluators. This is the typical pattern when the first generated
    rubric is a good starting point but a domain expert wants to tune the
    weighting or add custom dimensions. The sample:

      1. Generates v1 of an evaluator from a single `Prompt` source.
      2. Inspects the dimensions the service produced.
      3. Edits the dimensions locally - boosts the highest-weight editable
         dimension to 10, drops the lowest-weight editable dimension, and
         adds a new custom dimension. The non-editable `general_quality`
         ALWAYS-ON dimension is preserved verbatim.
      4. Saves the edited definition as v2 with `create_version`.
      5. Calls `list_versions` to enumerate v1 and v2.
      6. Cleans up by deleting both versions.

USAGE:
    python sample_adaptive_eval_generation_iterate.py

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

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import EvaluatorDefinitionType, JobStatus

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Unique per-run name so repeated runs do not collide.
ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
short = uuid.uuid4().hex[:6]
evaluator_name = f"reservation-quality-iterate-{ts}-{short}"

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

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
    # 1. Generate v1 of the evaluator from a single `Prompt` source.
    # ------------------------------------------------------------------
    print(f"Create generation job for evaluator `{evaluator_name}` (v1).")
    job = project_client.beta.evaluators.create_generation_job(
        job={
            "model": model_name,
            "name": "Reservation Quality (iterate)",
            "evaluator_name": evaluator_name,
            "evaluator_display_name": "Reservation Quality (iterate)",
            "evaluator_description": "Starting point for human-in-the-loop iteration.",
            "sources": [
                {
                    "type": "Prompt",
                    "description": "Inline application overview.",
                    "prompt": (
                        "You are evaluating a restaurant reservation assistant that creates, "
                        "modifies, and cancels reservations. It uses tools for restaurant "
                        "lookup, availability checking, and notifications. It must confirm "
                        "user intent before committing changes."
                    ),
                }
            ],
        },
        operation_id=f"adaptive-iterate-{short}",
    )
    print(f"Created generation job `{job.id}` (status: `{cast(JobStatus, job.status).value}`).")

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

    v1 = job.result
    print(f"v1 created: version=`{v1.version}`.")
    print(f"v1 dimensions ({len(v1.definition.dimensions)}):")
    for dim in v1.definition.dimensions:
        marker = " [ALWAYS-ON]" if dim.always_applicable else ""
        print(f"  - {dim.id} (weight={dim.weight}){marker}")

    # ------------------------------------------------------------------
    # 2. Edit dimensions locally.
    # ------------------------------------------------------------------
    # Domain-expert edits:
    #   * Always preserve the ALWAYS-ON `general_quality` residual dimension
    #     exactly as-is (id, weight, description, always_applicable).
    #   * Boost the most important editable dimension to weight 10.
    #   * Drop the lowest-weight editable dimension as redundant.
    #   * Add a new custom dimension specific to this assistant.
    print("Apply human edits:")
    editable = [d for d in v1.definition.dimensions if not d.always_applicable]
    always_on = [d for d in v1.definition.dimensions if d.always_applicable]

    edited_dimensions = []
    if editable:
        top = max(editable, key=lambda d: d.weight)
        lowest = min(editable, key=lambda d: d.weight)
        print(f"  Boost `{top.id}` weight {top.weight} -> 10.")
        print(f"  Drop `{lowest.id}` (weight={lowest.weight}).")
        for dim in editable:
            if dim.id == lowest.id:
                continue
            edited_dimensions.append(
                {
                    "id": dim.id,
                    "description": dim.description,
                    "weight": 10 if dim.id == top.id else dim.weight,
                }
            )

    new_dimension = {
        "id": "wait_time_expectations_set",
        "description": (
            "Sets clear expectations about wait time, table readiness, or confirmation "
            "delivery so the user knows what happens next."
        ),
        "weight": 4,
    }
    edited_dimensions.append(new_dimension)
    print(f"  Add new dimension `{new_dimension['id']}` (weight={new_dimension['weight']}).")

    # Preserve every ALWAYS-ON dimension verbatim. These are non-editable.
    for dim in always_on:
        print(f"  Preserve ALWAYS-ON dimension `{dim.id}` (weight={dim.weight}) verbatim.")
        edited_dimensions.append(
            {
                "id": dim.id,
                "description": dim.description,
                "weight": dim.weight,
                "always_applicable": True,
            }
        )

    # ------------------------------------------------------------------
    # 3. Save the edited definition as v2.
    # ------------------------------------------------------------------
    print(f"Save edited definition as v2 of `{evaluator_name}`.")
    v2 = project_client.beta.evaluators.create_version(
        name=evaluator_name,
        evaluator_version={
            "name": evaluator_name,
            "categories": [c.value for c in v1.categories],
            "display_name": v1.display_name,
            "description": (v1.description or "") + " (edited)",
            "definition": {
                "type": EvaluatorDefinitionType.RUBRIC,
                "dimensions": edited_dimensions,
                "pass_threshold": v1.definition.pass_threshold or 0.6,
            },
        },
    )
    print(f"v2 created: version=`{v2.version}`.")
    print(f"v2 dimensions ({len(v2.definition.dimensions)}):")
    for dim in v2.definition.dimensions:
        marker = " [ALWAYS-ON]" if dim.always_applicable else ""
        print(f"  - {dim.id} (weight={dim.weight}){marker}")

    # ------------------------------------------------------------------
    # 4. List all versions of the evaluator.
    # ------------------------------------------------------------------
    print(f"List all versions for evaluator `{evaluator_name}`:")
    for ver in project_client.beta.evaluators.list_versions(name=evaluator_name):
        print(f"  - version=`{ver.version}` dimensions={len(ver.definition.dimensions)}")

    # ------------------------------------------------------------------
    # 5. Clean up.
    # ------------------------------------------------------------------
    # Delete the highest version first to avoid any version-ordering issues.
    for version in (v2.version, v1.version):
        if version:
            print(f"Delete evaluator `{evaluator_name}` version `{version}`.")
            project_client.beta.evaluators.delete_version(name=evaluator_name, version=version)
