# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline regression tests for optional rubric dimension weights."""

from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest

from azure.ai.projects.models import Dimension, RubricBasedEvaluatorDefinition, RubricScoring, RubricScoringMode


@pytest.mark.parametrize(
    (
        "configured_weight",
        "generated_weight",
        "general_weight",
        "general_generated_weight",
        "other_weights",
        "expected_weights",
    ),
    [
        (
            8,
            1,
            2,
            7,
            [("weak", 2, None), ("middle", 4, None)],
            [("strong", 10), ("middle", 4), ("wait_time_expectations_set", 4), ("general_quality", 2)],
        ),
        (
            None,
            6,
            None,
            5,
            [("weak", None, 2), ("middle", None, 4)],
            [("strong", None), ("middle", None), ("wait_time_expectations_set", None), ("general_quality", None)],
        ),
        (
            None,
            None,
            None,
            None,
            [("weak", None, 2), ("middle", None, 4)],
            [("weak", None), ("middle", None), ("wait_time_expectations_set", None), ("general_quality", None)],
        ),
        (
            1,
            None,
            2,
            None,
            [("weak", 1, None), ("middle", 1, None)],
            [("weak", 1), ("middle", 10), ("wait_time_expectations_set", 4), ("general_quality", 2)],
        ),
        (
            5,
            None,
            2,
            None,
            [],
            [("strong", 10), ("wait_time_expectations_set", 4), ("general_quality", 2)],
        ),
    ],
    ids=["configured", "generated", "default", "equal-weights", "single-editable"],
)
def test_iteration_sample_uses_effective_weights(
    configured_weight,
    generated_weight,
    general_weight,
    general_generated_weight,
    other_weights,
    expected_weights,
    monkeypatch,
):
    definition = RubricBasedEvaluatorDefinition(
        dimensions=[
            Dimension(
                {
                    "id": "strong",
                    "description": "Important criterion.",
                    "weight": configured_weight,
                    "generated_weight": generated_weight,
                }
            ),
            *[
                Dimension(
                    {
                        "id": dimension_id,
                        "description": "Additional criterion.",
                        "weight": weight,
                        "generated_weight": suggested,
                    }
                )
                for dimension_id, weight, suggested in other_weights
            ],
            Dimension(
                {
                    "id": "general_quality",
                    "description": "Preserved criterion.",
                    "weight": general_weight,
                    "generated_weight": general_generated_weight,
                    "always_applicable": True,
                }
            ),
        ],
        scoring=RubricScoring(mode=RubricScoringMode.LIKERT),
        pass_threshold=0.0,
    )
    version = SimpleNamespace(
        definition=definition, categories=[], display_name="Test rubric", description="Test definition", version="1"
    )
    client = MagicMock()
    operations = client.__enter__.return_value.evaluators
    poller = operations.begin_create_generation_job.return_value
    poller.done.return_value = True
    poller.result.return_value = version
    operations.create_version.return_value = SimpleNamespace(definition=definition, version="2")
    operations.list_versions.return_value = [version]
    monkeypatch.setattr("azure.ai.projects.AIProjectClient", MagicMock(return_value=client))
    monkeypatch.setattr("azure.identity.DefaultAzureCredential", MagicMock())
    monkeypatch.setattr("dotenv.load_dotenv", MagicMock())
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test")
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "test-model")
    sample = Path(__file__).parents[2] / "samples" / "evaluations" / "sample_rubric_evaluator_generation_iterate.py"

    runpy.run_path(str(sample))
    job = operations.begin_create_generation_job.call_args.kwargs["job"]
    assert job.scoring.mode == RubricScoringMode.LIKERT
    edited_definition = operations.create_version.call_args.kwargs["evaluator_version"]["definition"]
    assert edited_definition["scoring"]["mode"] == RubricScoringMode.LIKERT
    assert edited_definition["pass_threshold"] == 0.0
    dimensions = edited_definition["dimensions"]
    assert [(dimension["id"], dimension.get("weight")) for dimension in dimensions] == expected_weights
    general = {
        "id": "general_quality",
        "description": "Preserved criterion.",
        "always_applicable": True,
    }
    if general_weight is not None:
        general["weight"] = general_weight
    else:
        assert all("weight" not in dimension for dimension in dimensions)
    assert dimensions[-1] == general
    assert operations.delete_version.call_args_list == [
        call(name=job.evaluator_name, version="2"),
        call(name=job.evaluator_name, version="1"),
    ]
