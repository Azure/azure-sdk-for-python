# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end scenario showing every rubric evaluator generation source type
    in a single sample file. There are four source types:

      1. `Prompt`  - an inline natural-language description of the application.
      2. `Agent`   - references an agent registered in the Foundry project.
      3. `Dataset` - references an uploaded dataset (name + version).
      4. `traces`  - Application Insights conversation traces for an agent,
         within a time window.

    The first three source types can be combined into a single generation job
    to produce a richer rubric. The `traces` source type requires a companion
    source (the service rejects `traces`-only source arrays), so this sample
    submits it as a separate, second job paired with an `Agent` companion.

    Optional environment variables let you skip variants where you don't have
    a suitable agent, dataset, or recent traces in the target Foundry project.

USAGE:
    python sample_rubric_evaluator_generation_all_sources.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of the LLM model deployment that
       the generation job will use (e.g. `gpt-4o`, `gpt-4.1`).
    3) FOUNDRY_AGENT_NAME - Optional. Name of an agent registered in the project.
       Enables the `Agent` source and the `traces`-source job.
    4) FOUNDRY_REFERENCE_DATASET_NAME - Optional. Name of an uploaded dataset.
       Enables the `Dataset` source.
    5) FOUNDRY_REFERENCE_DATASET_VERSION - Optional. Version of the uploaded dataset.
       Enables the `Dataset` source.
    6) FOUNDRY_TRACES_WINDOW_DAYS - Optional. Look-back window in days for the
       `traces` source. Defaults to 7.
    7) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between
       generation job status polls. Defaults to 10.
"""

import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, cast

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import JobStatus

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME")
dataset_name = os.environ.get("FOUNDRY_REFERENCE_DATASET_NAME")
dataset_version = os.environ.get("FOUNDRY_REFERENCE_DATASET_VERSION")
traces_window_days = int(os.environ.get("FOUNDRY_TRACES_WINDOW_DAYS", "7"))
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Unique per-run suffix so repeated runs do not collide on evaluator name.
ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
short = uuid.uuid4().hex[:6]
multi_name = f"multi-source-{ts}-{short}"
traces_name = f"traces-source-{ts}-{short}"

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

multi_evaluator_version = ""
traces_evaluator_version = ""

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
    # 1. Combined Prompt + Agent + Dataset generation job.
    # ------------------------------------------------------------------
    print("Build sources for the combined generation job:")
    multi_sources: List[Dict[str, Any]] = [
        {
            "type": "Prompt",
            "description": "Inline application overview.",
            "prompt": (
                "You are evaluating a customer-support assistant that helps users "
                "manage their accounts, troubleshoot issues, and place orders. The "
                "assistant uses tools for account lookup, password reset, and order "
                "creation. It must confirm intent before performing destructive "
                "actions and maintain a patient, professional tone."
            ),
        }
    ]
    if agent_name:
        print(f"  Including Agent source: `{agent_name}`.")
        multi_sources.append(
            {
                "type": "Agent",
                "description": "Agent metadata enriches the rubric with tool and instruction signals.",
                "agent_name": agent_name,
            }
        )
    else:
        print("  Skipping Agent source (FOUNDRY_AGENT_NAME not set).")

    if dataset_name and dataset_version:
        print(f"  Including Dataset source: `{dataset_name}` v`{dataset_version}`.")
        multi_sources.append(
            {
                "type": "Dataset",
                "description": "Reference examples ground dimensions in real data.",
                "name": dataset_name,
                "version": dataset_version,
            }
        )
    else:
        print("  Skipping Dataset source (FOUNDRY_REFERENCE_DATASET_NAME / _VERSION not set).")

    print(f"Create combined generation job for evaluator `{multi_name}`.")
    multi_job = project_client.beta.evaluators.create_generation_job(
        job={
            "model": model_name,
            "name": "Multi-source generation",
            "evaluator_name": multi_name,
            "evaluator_display_name": "Customer Support Quality (multi-source)",
            "evaluator_description": "Generated from prompt, agent, and dataset signals.",
            "sources": multi_sources,
        },
        operation_id=f"rubric-multi-{short}",
    )
    print(f"Created generation job `{multi_job.id}` (status: `{cast(JobStatus, multi_job.status).value}`).")

    print(f"Poll job `{multi_job.id}` until it reaches a terminal state.", end="", flush=True)
    while multi_job.status not in TERMINAL_STATUSES:
        time.sleep(poll_interval_seconds)
        multi_job = project_client.beta.evaluators.get_generation_job(multi_job.id)
        print(".", end="", flush=True)
    print()
    print(f"Final job status: `{cast(JobStatus, multi_job.status).value}`.")

    if multi_job.status != JobStatus.SUCCEEDED:
        message = multi_job.error.message if multi_job.error is not None else "<no error message>"
        print(
            f"Combined job `{multi_job.id}` ended with status "
            f"`{cast(JobStatus, multi_job.status).value}`: {message}"
        )
    else:
        evaluator = multi_job.result
        multi_evaluator_version = evaluator.version or ""
        print(f"Generated evaluator: name=`{evaluator.name}` version=`{evaluator.version}`.")
        print(f"Categories: {[c.value for c in evaluator.categories]}")
        print(f"Dimensions ({len(evaluator.definition.dimensions)}):")
        for dim in evaluator.definition.dimensions:
            marker = " [ALWAYS-ON]" if dim.always_applicable else ""
            print(f"  - {dim.id} (weight={dim.weight}){marker}")

    # ------------------------------------------------------------------
    # 2. Separate `traces` + Agent companion generation job.
    # ------------------------------------------------------------------
    # The traces source requires a companion source because the service
    # rejects sources arrays consisting only of traces. The Agent source
    # is the typical companion.
    if not agent_name:
        print("Skip traces job: requires FOUNDRY_AGENT_NAME for both the traces source and companion.")
    else:
        print(f"Create traces-source generation job for evaluator `{traces_name}`.")
        print(f"  agent=`{agent_name}` look-back window: {traces_window_days} days")
        now = int(time.time())
        start_time = now - traces_window_days * 24 * 3600
        end_time = now + 600  # small padding for clock skew

        traces_job = project_client.beta.evaluators.create_generation_job(
            job={
                "model": model_name,
                "name": "Traces-source generation",
                "evaluator_name": traces_name,
                "evaluator_display_name": "Customer Support Quality (from traces)",
                "evaluator_description": "Generated from real Application Insights conversation traces.",
                "sources": [
                    {
                        "type": "traces",
                        "description": "Application Insights conversation traces for the agent.",
                        "agent_name": agent_name,
                        "start_time": start_time,
                        "end_time": end_time,
                    },
                    {
                        "type": "Agent",
                        "description": "Companion source (service rejects traces-only).",
                        "agent_name": agent_name,
                    },
                ],
            },
            operation_id=f"rubric-traces-{short}",
        )
        print(f"Created generation job `{traces_job.id}` (status: `{cast(JobStatus, traces_job.status).value}`).")

        print(f"Poll job `{traces_job.id}` until it reaches a terminal state.", end="", flush=True)
        while traces_job.status not in TERMINAL_STATUSES:
            time.sleep(poll_interval_seconds)
            traces_job = project_client.beta.evaluators.get_generation_job(traces_job.id)
            print(".", end="", flush=True)
        print()
        print(f"Final job status: `{cast(JobStatus, traces_job.status).value}`.")

        if traces_job.status != JobStatus.SUCCEEDED:
            message = traces_job.error.message if traces_job.error is not None else "<no error message>"
            print(
                f"Traces job `{traces_job.id}` ended with status "
                f"`{cast(JobStatus, traces_job.status).value}`: {message}"
            )
        else:
            evaluator = traces_job.result
            traces_evaluator_version = evaluator.version or ""
            print(f"Generated evaluator: name=`{evaluator.name}` version=`{evaluator.version}`.")
            print(f"Categories: {[c.value for c in evaluator.categories]}")
            print(f"Dimensions ({len(evaluator.definition.dimensions)}):")
            for dim in evaluator.definition.dimensions:
                marker = " [ALWAYS-ON]" if dim.always_applicable else ""
                print(f"  - {dim.id} (weight={dim.weight}){marker}")

    # ------------------------------------------------------------------
    # 3. Clean up.
    # ------------------------------------------------------------------
    # `delete_version` cascades to delete the generation job record as well.
    if multi_evaluator_version:
        print(f"Delete evaluator `{multi_name}` version `{multi_evaluator_version}`.")
        project_client.beta.evaluators.delete_version(name=multi_name, version=multi_evaluator_version)
    if traces_evaluator_version:
        print(f"Delete evaluator `{traces_name}` version `{traces_evaluator_version}`.")
        project_client.beta.evaluators.delete_version(name=traces_name, version=traces_evaluator_version)
