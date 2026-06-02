# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end scenario showing rubric evaluator generation from a single
    `Prompt` source, followed by an OpenAI evaluation run that uses the
    generated evaluator. The sample:

      1. Creates an `EvaluatorGenerationJob` whose only source is an inline
         natural-language description of the application's purpose, capabilities,
         and tools. The service synthesizes a rubric tailored to that application.
      2. Polls the generation job to completion and resolves the generated
         `EvaluatorVersion`.
      3. Creates an OpenAI evaluation referencing the generated evaluator as a
         testing criterion.
      4. Runs the evaluation against inline JSONL sample data.
      5. Cleans up the evaluation and the evaluator version. Deleting the
         evaluator version cascades to delete the generation job record.

    Other source types - `Agent`, `Dataset`, and `traces` - can be used in
    place of (or alongside) the prompt source. See
    `sample_rubric_evaluator_generation_all_sources.py` for examples of each.

USAGE:
    python sample_rubric_evaluator_generation_basic.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of the model used by both the
       generation job and the eval run's LLM judge (e.g. `gpt-4o`, `gpt-4.1`).
       The generation runs inline server side (no deployment required), but the
       eval run's grader does require a model deployment in your project.
    3) POLL_INTERVAL_SECONDS - Optional. Seconds to sleep between status polls
       for both the generation job and the evaluation run. Defaults to 10.
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
from azure.ai.projects.models import (
    JobStatus,
    RubricBasedEvaluatorDefinition,
    TestingCriterionAzureAIEvaluator,
)

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
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    # 1. Generate an evaluator from a single `Prompt` source.
    job = project_client.beta.evaluators.create_generation_job(
        job={
            "model": model_name,
            "name": "Reservation Quality (Generated)",
            "evaluator_name": evaluator_name,
            "evaluator_display_name": "Reservation Quality (Generated)",
            "evaluator_description": "Quality evaluator generated from a prompt describing a restaurant reservation assistant.",
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
        # `operation_id` makes the call idempotent - re-submitting the same id returns the existing job.
        operation_id=f"rubric-eval-basic-{short}",
    )
    print(f"Created generation job `{job.id}`.")

    print(f"Waiting for job `{job.id}` to complete...")
    while job.status not in TERMINAL_STATUSES:
        time.sleep(poll_interval_seconds)
        job = project_client.beta.evaluators.get_generation_job(job.id)
    print(f"Job finished with status `{cast(JobStatus, job.status).value}`.")

    if job.status != JobStatus.SUCCEEDED:
        message = job.error.message if job.error is not None else "<no error message>"
        raise RuntimeError(f"Generation job ended with status `{cast(JobStatus, job.status).value}`: {message}")

    # On success, the evaluator is automatically saved as version 1.
    # `isinstance` narrows the discriminated `definition` to the rubric subtype.
    evaluator = job.result
    assert evaluator is not None
    definition = evaluator.definition
    assert isinstance(definition, RubricBasedEvaluatorDefinition)
    print(
        f"Generated evaluator `{evaluator.name}` v{evaluator.version}: "
        f"{len(definition.dimensions)} dimensions, pass_threshold={definition.pass_threshold}."
    )
    print(f"  Dimensions: {', '.join(d.id for d in definition.dimensions)}")

    # 2. Create an OpenAI evaluation that uses the generated evaluator.
    eval_object = openai_client.evals.create(
        name=f"{evaluator.name}-eval",
        data_source_config=DataSourceConfigCustom(
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
        ),
        testing_criteria=[
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
        ],
    )

    # 3. Run the evaluation against inline JSONL sample data.
    eval_run = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name=f"{evaluator.name}-run",
        metadata={"sample": "rubric_evaluator_generation_basic"},
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileContent(
                type="file_content",
                content=[
                    SourceFileContentContent(
                        item={
                            "query": "Book a table for 4 tomorrow at 7 PM.",
                            "response": "Booked - table for 4 tomorrow at 7:00 PM. A confirmation SMS is on its way.",
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

    print(f"Waiting for eval run `{eval_run.id}` to complete...")
    while eval_run.status not in TERMINAL_RUN_STATUSES:
        time.sleep(poll_interval_seconds)
        eval_run = openai_client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_object.id)
    print(f"Eval run finished with status `{eval_run.status}`. Result counts: {eval_run.result_counts}.")

    # 4. Clean up. `delete_version` cascades to delete the generation job record.
    print("Cleaning up.")
    openai_client.evals.delete(eval_id=eval_object.id)
    project_client.beta.evaluators.delete_version(name=evaluator.name, version=evaluator.version)
