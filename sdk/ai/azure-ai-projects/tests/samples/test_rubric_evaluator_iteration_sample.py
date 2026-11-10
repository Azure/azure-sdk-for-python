# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline regression tests for optional rubric dimension weights."""

from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from azure.ai.projects.models import Dimension, RubricBasedEvaluatorDefinition


@pytest.mark.parametrize("configured_weight", [None, 8])
def test_iteration_sample_requires_configured_weights(configured_weight, monkeypatch):
    definition = RubricBasedEvaluatorDefinition(
        dimensions=[
            Dimension(id="strong", description="Important criterion.", weight=configured_weight),
            Dimension(id="weak", description="Redundant criterion.", weight=1),
            Dimension(id="general_quality", description="Preserved criterion.", weight=2, always_applicable=True),
        ]
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

    if configured_weight is None:
        with pytest.raises(ValueError, match="requires a weighted rubric"):
            runpy.run_path(str(sample))
        operations.create_version.assert_not_called()
    else:
        runpy.run_path(str(sample))
        dimensions = operations.create_version.call_args.kwargs["evaluator_version"]["definition"]["dimensions"]
        assert [dimension["id"] for dimension in dimensions] == [
            "strong",
            "wait_time_expectations_set",
            "general_quality",
        ]
        assert dimensions[0]["weight"] == 10
        assert dimensions[-1] == {
            "id": "general_quality",
            "description": "Preserved criterion.",
            "weight": 2,
            "always_applicable": True,
        }
