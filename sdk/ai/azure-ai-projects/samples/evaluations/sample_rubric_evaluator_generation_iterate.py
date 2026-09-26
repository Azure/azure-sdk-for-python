# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    End-to-end scenario showing the human-in-the-loop iteration workflow for
    rubric evaluators. This is the typical pattern when the first generated
    rubric is a good starting point but a domain expert wants to tune the
    weighting or add custom dimensions. The sample:

      1. Generates v1 of an evaluator from a single `Prompt` source.
      2. Edits the dimensions locally - boosts the highest-weight editable
         dimension to 10, drops the lowest-weight editable dimension, and
         adds a new custom dimension. The non-editable `general_quality`
         ALWAYS-ON dimension is preserved verbatim.
      3. Saves the edited definition as v2 with `create_version`.
      4. Calls `list_versions` to enumerate v1 and v2.
      5. Cleans up by deleting both versions.

USAGE:
    python sample_rubric_evaluator_generation_iterate.py

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
import time
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    EvaluatorCategory,
    EvaluatorDefinitionType,
    EvaluatorGenerationInputs,
    EvaluatorGenerationJob,
    PromptEvaluatorGenerationJobSource,
    RubricBasedEvaluatorDefinition,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Unique per-run name so repeated runs do not collide.
ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
short = uuid.uuid4().hex[:6]
evaluator_name = f"reservation-quality-iterate-{ts}-{short}"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    # 1. Generate v1 of the evaluator from a single `Prompt` source.
    print("Begin creating an evaluator generation job.")
    poller = project_client.beta.evaluators.begin_create_generation_job(
        job=EvaluatorGenerationJob(
            inputs=EvaluatorGenerationInputs(
                model=model_name,
                evaluator_name=evaluator_name,
                evaluator_display_name="Reservation Quality (iterate)",
                evaluator_description="Starting point for human-in-the-loop iteration.",
                sources=[
                    PromptEvaluatorGenerationJobSource(
                        description="Inline application overview.",
                        prompt=(
                            "You are evaluating a restaurant reservation assistant that creates, "
                            "modifies, and cancels reservations. It uses tools for restaurant "
                            "lookup, availability checking, and notifications. It must confirm "
                            "user intent before committing changes."
                        ),
                    ),
                ],
            ),
        ),
        operation_id=f"rubric-iterate-{short}",
        polling_interval=poll_interval_seconds,
    )

    # Optional: While SDK is polling, periodically print the job status until the job is complete
    print("Periodically check job status:")
    while not poller.done():
        print(f"\tstatus=`{poller.status()}`")
        time.sleep(poll_interval_seconds)

    # Since done() is true, result() returns the final deserialized job result without
    # waiting further. It also propagates any LRO polling exception.
    v1 = poller.result()
    print(f"Final LRO status: `{poller.status()}`.")
    print(f"Evaluator generation result: {v1}")

    # `isinstance` narrows the discriminated `definition` to the rubric subtype.
    v1_definition = v1.definition
    assert isinstance(v1_definition, RubricBasedEvaluatorDefinition)
    print(
        f"v1 created with {len(v1_definition.dimensions)} dimensions: {', '.join(d.id for d in v1_definition.dimensions)}"
    )

    # 2. Edit dimensions locally.
    # Domain-expert edits:
    #   * Always preserve the ALWAYS-ON `general_quality` residual dimension
    #     exactly as-is (id, weight, description, always_applicable).
    #   * Boost the most important editable dimension to weight 10.
    #   * Drop the lowest-weight editable dimension as redundant.
    #   * Add a new custom dimension specific to this assistant.
    editable = [d for d in v1_definition.dimensions if not d.always_applicable]
    always_on = [d for d in v1_definition.dimensions if d.always_applicable]

    edited_dimensions = []
    if editable:
        top = max(editable, key=lambda d: d.weight)
        lowest = min(editable, key=lambda d: d.weight)
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

    edited_dimensions.append(
        {
            "id": "wait_time_expectations_set",
            "description": (
                "Sets clear expectations about wait time, table readiness, or confirmation "
                "delivery so the user knows what happens next."
            ),
            "weight": 4,
        }
    )

    # Preserve every ALWAYS-ON dimension verbatim. These are non-editable.
    for dim in always_on:
        edited_dimensions.append(
            {
                "id": dim.id,
                "description": dim.description,
                "weight": dim.weight,
                "always_applicable": True,
            }
        )

    # 3. Save the edited definition as v2.
    # TODO: Remove this suppression once TypeSpec typing for EvaluatorVersion is fixed.
    v2 = project_client.beta.evaluators.create_version(  # type: ignore[call-overload]  # pyright: ignore[reportCallIssue]
        name=evaluator_name,
        evaluator_version={  # pyright: ignore[reportArgumentType]
            "name": evaluator_name,
            # Narrow each category to its enum value (the categories list is Union[str, EvaluatorCategory]).
            "categories": [c.value if isinstance(c, EvaluatorCategory) else c for c in v1.categories],
            "display_name": v1.display_name,
            "description": (v1.description or "") + " (edited)",
            "definition": {
                "type": EvaluatorDefinitionType.RUBRIC,
                "dimensions": edited_dimensions,
                "pass_threshold": v1_definition.pass_threshold or 0.6,
            },
        },
    )
    v2_definition = v2.definition
    assert isinstance(v2_definition, RubricBasedEvaluatorDefinition)
    print(
        f"v2 created with {len(v2_definition.dimensions)} dimensions: {', '.join(d.id for d in v2_definition.dimensions)}"
    )

    # 4. List all versions of the evaluator.
    print(f"All versions of `{evaluator_name}`:")
    for ver in project_client.beta.evaluators.list_versions(name=evaluator_name):
        ver_definition = ver.definition
        assert isinstance(ver_definition, RubricBasedEvaluatorDefinition)
        print(f"  - v{ver.version}: {len(ver_definition.dimensions)} dimensions")

    # 5. Clean up. Delete the highest version first to avoid any ordering issues.
    print("Cleaning up.")
    for version in (v2.version, v1.version):
        if version:
            project_client.beta.evaluators.delete_version(name=evaluator_name, version=version)
