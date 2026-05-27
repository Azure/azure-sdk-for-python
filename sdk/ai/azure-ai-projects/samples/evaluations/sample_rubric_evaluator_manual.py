# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end scenario showing how to manually author a rubric-based
    evaluator and use it as a testing criterion of an OpenAI evaluation run.
    The sample:

      1. Creates a rubric evaluator with `project_client.beta.evaluators.create_version`,
         supplying scoring dimensions (each with an id, description, and integer
         weight from 1-10) and an optional pass threshold.
      2. Creates an OpenAI evaluation referencing the rubric as a testing criterion.
      3. Runs the evaluation against inline JSONL sample data and prints per-item
         scores.
      4. Cleans up the evaluation and the evaluator version.

    A rubric evaluator is a collection of independent scoring dimensions. At
    evaluation time, an LLM judge scores each applicable dimension on a 1-5
    scale and the runtime emits a normalized aggregate score. Dimensions can
    opt in to `always_applicable` to skip the applicability assessment.

    See `sample_rubric_evaluator_generation_basic.py` for the generation-based
    workflow that produces the same rubric structure automatically from a
    description of the application.

USAGE:
    python sample_rubric_evaluator_manual.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of the LLM model deployment that
       the rubric evaluator's judge will use at evaluation time (e.g. `gpt-4o`, `gpt-4.1`).
    3) POLL_INTERVAL_SECONDS - Optional. Seconds to sleep between status polls
       for the evaluation run. Defaults to 10.
"""

import os
import time
import uuid
from datetime import datetime, timezone

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
    EvaluatorCategory,
    EvaluatorDefinitionType,
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
evaluator_name = f"reservation-quality-manual-{ts}-{short}"

TERMINAL_RUN_STATUSES = {"completed", "failed", "canceled"}

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    # 1. Author the rubric evaluator.
    # Each dimension is scored independently on a 1-5 scale by an LLM judge at
    # evaluation time. `weight` (1-10) controls how strongly each dimension
    # contributes to the normalized aggregate score.
    evaluator = project_client.beta.evaluators.create_version(
        name=evaluator_name,
        evaluator_version={
            "name": evaluator_name,
            "categories": [EvaluatorCategory.QUALITY],
            "display_name": "Reservation Quality (Manual)",
            "description": (
                "Hand-authored rubric evaluating a reservation assistant on intent "
                "resolution, completeness, and tone."
            ),
            "definition": {
                "type": EvaluatorDefinitionType.RUBRIC,
                "dimensions": [
                    {
                        "id": "correct_intent_resolution",
                        "description": (
                            "Correctly identifies the user's reservation intent (new booking, "
                            "modification, or cancellation) and pursues the right workflow."
                        ),
                        "weight": 9,
                    },
                    {
                        "id": "completeness",
                        "description": (
                            "Captures or confirms every reservation detail the user needs "
                            "(party size, date, time, contact info) before completing the task."
                        ),
                        "weight": 6,
                    },
                    {
                        "id": "professional_tone",
                        "description": "Maintains a polite, professional, restaurant-host tone throughout.",
                        "weight": 3,
                    },
                ],
                # `pass_threshold` sets the normalized 0.0-1.0 pass/fail threshold (default 0.5).
                "pass_threshold": 0.6,
            },
        },
    )
    # `isinstance` narrows the discriminated `definition` to the rubric subtype.
    definition = evaluator.definition
    assert isinstance(definition, RubricBasedEvaluatorDefinition)
    print(
        f"Created evaluator `{evaluator.name}` version `{evaluator.version}` with {len(definition.dimensions)} dimensions."
    )

    # 2. Create an OpenAI evaluation that uses the rubric as a testing criterion.
    eval_object = openai_client.evals.create(
        name=f"{evaluator_name}-eval",
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
                name=evaluator_name,
                evaluator_name=evaluator_name,
                # The LLM judge for the rubric uses the deployment supplied here.
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
        name=f"{evaluator_name}-run",
        metadata={"sample": "evaluator_rubric_manual"},
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileContent(
                type="file_content",
                content=[
                    SourceFileContentContent(
                        item={
                            "query": "Can I book a table for 4 tomorrow at 7 PM?",
                            "response": (
                                "Absolutely - I have you down for a table for 4 tomorrow at 7:00 PM. "
                                "Could you share a contact number in case anything changes?"
                            ),
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "query": "I need to cancel my reservation for Friday.",
                            "response": "ok",
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "query": "Can you move my Saturday 8 PM reservation to 8:30?",
                            "response": (
                                "Of course. I've updated your Saturday reservation from 8:00 PM to 8:30 PM. "
                                "Anything else I can help with?"
                            ),
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

    if eval_run.status == "completed":
        for idx, item in enumerate(
            openai_client.evals.runs.output_items.list(run_id=eval_run.id, eval_id=eval_object.id), start=1
        ):
            # Result entries may be typed objects (Azure AI evaluators) or plain dicts (some OpenAI evaluators).
            scores = []
            for r in getattr(item, "results", None) or []:
                name = r.get("name", "?") if isinstance(r, dict) else getattr(r, "name", "?")
                score = r.get("score", "n/a") if isinstance(r, dict) else getattr(r, "score", "n/a")
                scores.append(f"{name}={score}")
            print(f"  item {idx} ({item.status}): {', '.join(scores)}")

    # 4. Clean up.
    print("Cleaning up.")
    openai_client.evals.delete(eval_id=eval_object.id)
    project_client.beta.evaluators.delete_version(name=evaluator_name, version=evaluator.version)
