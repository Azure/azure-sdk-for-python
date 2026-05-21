# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end scenario showing adaptive evaluator generation from a single
    `Prompt` source, followed by an OpenAI evaluation run that uses the
    generated evaluator. The sample:

      1. Creates an `EvaluatorGenerationJob` whose only source is an inline
         natural-language description of the application's purpose, capabilities,
         and tools. The service synthesizes a rubric tailored to that application.
      2. Polls the generation job to completion and resolves the generated
         `EvaluatorVersion`.
      3. Creates an OpenAI evaluation (`client.evals.create`) referencing the
         generated evaluator as a testing criterion.
      4. Runs the evaluation against inline JSONL sample data.
      5. Cleans up the evaluation and the evaluator version. Deleting the
         evaluator version cascades to delete the generation job record.

    Other source types - `Agent`, `Dataset`, and `traces` - can be used in
    place of (or alongside) the prompt source. See
    `sample_adaptive_eval_generation_all_sources.py` for examples of each.

USAGE:
    python sample_adaptive_eval_generation_basic.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of the LLM model deployment that
       the generation job will use (e.g. `gpt-4o`, `gpt-4.1`).
    3) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between status
       polls for both the generation job and the evaluation run. Defaults to 10.
"""

import os
import time
import uuid
from datetime import datetime, timezone
from typing import cast

from dotenv import load_dotenv
from openai.types.eval_create_params import DataSourceConfigCustom
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import JobStatus, TestingCriterionAzureAIEvaluator

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Unique per-run name so repeated runs do not collide.
ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
short = uuid.uuid4().hex[:6]
evaluator_name = f"reservation-quality-generated-{ts}-{short}"

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}
TERMINAL_RUN_STATUSES = {"completed", "failed", "canceled"}

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
    project_client.get_openai_client() as openai_client,
):

    # ------------------------------------------------------------------
    # 1. Generate an evaluator from a single `Prompt` source.
    # ------------------------------------------------------------------
    # The body is sent as a plain dict to match the wire shape expected by
    # the 2025-11-15-preview API.
    print(f"Create generation job for evaluator `{evaluator_name}`.")
    job = project_client.beta.evaluators.create_generation_job(
        job={
            "model": model_name,
            "name": "Reservation Quality (Generated)",
            "evaluator_name": evaluator_name,
            "evaluator_display_name": "Reservation Quality (Generated)",
            "evaluator_description": (
                "Quality evaluator generated from a prompt describing a "
                "restaurant reservation assistant."
            ),
            "sources": [
                {
                    "type": "Prompt",
                    "description": "Application overview - purpose, capabilities, and tools.",
                    "prompt": (
                        "You are evaluating a restaurant reservation assistant. The assistant helps "
                        "users create, modify, and cancel reservations at participating restaurants. "
                        "It can:\n"
                        "  - Search for restaurants by name, cuisine, or neighborhood.\n"
                        "  - Check table availability for a requested date, time, and party size.\n"
                        "  - Create, update, and cancel reservations on behalf of the user.\n"
                        "  - Send SMS or email confirmations through a notifications tool.\n"
                        "It must always confirm the user's intent before committing changes, "
                        "ask follow-up questions when details are missing, and maintain a polite "
                        "restaurant-host tone."
                    ),
                }
            ],
        },
        # `operation_id` makes the call idempotent - re-submitting the same id
        # returns the existing job instead of creating a duplicate.
        operation_id=f"adaptive-eval-basic-{short}",
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

    if job.usage is not None:
        print(f"Token usage: {job.usage}")

    # On success, the evaluator is automatically saved as version 1.
    evaluator = job.result
    print(f"Generated evaluator: name=`{evaluator.name}` version=`{evaluator.version}`.")
    print(f"Categories: {[c.value for c in evaluator.categories]}")
    print(f"Pass threshold: {evaluator.definition.pass_threshold}")
    print(f"Dimensions ({len(evaluator.definition.dimensions)}):")
    for dim in evaluator.definition.dimensions:
        # Quality evaluators always include a non-editable `general_quality`
        # residual dimension with always_applicable=True.
        marker = " [ALWAYS-ON]" if dim.always_applicable else ""
        print(f"  - {dim.id} (weight={dim.weight}){marker}: {dim.description[:120]}")

    # ------------------------------------------------------------------
    # 2. Create an OpenAI evaluation that uses the generated evaluator.
    # ------------------------------------------------------------------
    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "response": {"type": "string"},
            },
            "required": ["query", "response"],
        },
        include_sample_schema=True,
    )

    testing_criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name=evaluator.name,
            evaluator_name=evaluator.name,
            initialization_parameters={"deployment_name": model_name},
            data_mapping={
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        )
    ]

    print("Create the evaluation.")
    eval_object = openai_client.evals.create(
        name=f"{evaluator.name}-eval",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created (id: {eval_object.id}).")

    # ------------------------------------------------------------------
    # 3. Run the evaluation against inline JSONL sample data.
    # ------------------------------------------------------------------
    print(f"Create an evaluation run for eval `{eval_object.id}`.")
    eval_run = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name=f"{evaluator.name}-run",
        metadata={"sample": "adaptive_eval_generation_basic"},
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileContent(
                type="file_content",
                content=[
                    SourceFileContentContent(
                        item={
                            "query": "Book a table for 4 tomorrow at 7 PM.",
                            "response": (
                                "Booked - table for 4 tomorrow at 7:00 PM. A confirmation "
                                "SMS is on its way."
                            ),
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "query": "Cancel my reservation for Friday night.",
                            "response": "Sure.",
                        }
                    ),
                ],
            ),
        ),
    )
    print(f"Evaluation run created (id: {eval_run.id}).")

    print(f"Poll run `{eval_run.id}` until it reaches a terminal state.", end="", flush=True)
    while eval_run.status not in TERMINAL_RUN_STATUSES:
        time.sleep(poll_interval_seconds)
        eval_run = openai_client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_object.id)
        print(".", end="", flush=True)
    print()
    print(f"Final eval run status: `{eval_run.status}`.")

    if eval_run.status == "completed":
        print(f"Result counts: {eval_run.result_counts}")
        if eval_run.report_url:
            print(f"Eval run report URL: {eval_run.report_url}")
        output_items = list(openai_client.evals.runs.output_items.list(run_id=eval_run.id, eval_id=eval_object.id))
        print(f"Output items (total: {len(output_items)}):")
        for idx, item in enumerate(output_items, start=1):
            results = getattr(item, "results", None) or []
            parts = []
            for r in results:
                # Result entries are returned either as typed objects (Azure AI
                # evaluators) or as plain dicts (some OpenAI-native evaluators).
                if isinstance(r, dict):
                    name = r.get("name", "?")
                    score = r.get("score", "n/a")
                    passed = r.get("passed", "n/a")
                else:
                    name = getattr(r, "name", "?")
                    score = getattr(r, "score", "n/a")
                    passed = getattr(r, "passed", "n/a")
                parts.append(f"{name}={score} ({passed})")
            print(f"  item {idx}: status={item.status} | {', '.join(parts)}")
    else:
        print("Evaluation run did not complete successfully.")

    # ------------------------------------------------------------------
    # 4. Clean up.
    # ------------------------------------------------------------------
    print(f"Delete evaluation `{eval_object.id}`.")
    openai_client.evals.delete(eval_id=eval_object.id)

    print(f"Delete evaluator `{evaluator.name}` version `{evaluator.version}`.")
    # `delete_version` cascades to delete the generation job record as well.
    project_client.beta.evaluators.delete_version(name=evaluator.name, version=evaluator.version)
