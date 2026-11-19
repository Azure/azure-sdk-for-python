# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline tests for rubric evaluator sample behavior."""

from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest

from azure.ai.projects.models import Dimension, RubricBasedEvaluatorDefinition


@pytest.fixture
def sample_clients(monkeypatch):
    client = MagicMock()
    project_client = client.__enter__.return_value
    openai_client = project_client.get_openai_client.return_value.__enter__.return_value
    monkeypatch.setattr("azure.ai.projects.AIProjectClient", MagicMock(return_value=client))
    monkeypatch.setattr("azure.identity.DefaultAzureCredential", MagicMock())
    monkeypatch.setattr("dotenv.load_dotenv", MagicMock())
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test")
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "test-model")
    return project_client, openai_client


@pytest.mark.parametrize(("failure", "created_count"), [("safety", 2), ("run", 3)])
def test_manual_sample_cleans_created_resources_on_failure(sample_clients, failure, created_count):
    project_client, openai_client = sample_clients
    operations = project_client.evaluators
    definition = RubricBasedEvaluatorDefinition(dimensions=[])
    version = SimpleNamespace(name="test", version="1", definition=definition)
    if failure == "safety":
        operations.create_version.side_effect = [version, version, RuntimeError("safety unavailable")]
    else:
        operations.create_version.side_effect = [version, version, version]
        openai_client.evals.create.return_value = SimpleNamespace(id="eval-id")
        openai_client.evals.runs.create.side_effect = RuntimeError("run failed")

    sample = Path(__file__).parents[2] / "samples" / "evaluations" / "sample_rubric_evaluator_manual.py"
    with pytest.raises(RuntimeError):
        runpy.run_path(str(sample))

    create_calls = operations.create_version.call_args_list[:created_count]
    assert operations.delete_version.call_args_list == [
        call(name=create_call.kwargs["name"], version="1") for create_call in reversed(create_calls)
    ]
    if failure == "safety":
        openai_client.evals.delete.assert_not_called()
    else:
        openai_client.evals.delete.assert_called_once_with(eval_id="eval-id")


def test_iteration_sample_cleans_initial_version_if_edit_fails(sample_clients):
    project_client, _ = sample_clients
    operations = project_client.evaluators
    definition = RubricBasedEvaluatorDefinition(dimensions=[Dimension(id="criterion", description="A criterion")])
    version = SimpleNamespace(
        name="test", version="1", definition=definition, categories=[], display_name="Test", description="Test"
    )
    poller = operations.begin_create_generation_job.return_value
    poller.done.return_value = True
    poller.result.return_value = version
    operations.create_version.side_effect = RuntimeError("edit failed")

    sample = Path(__file__).parents[2] / "samples" / "evaluations" / "sample_rubric_evaluator_generation_iterate.py"
    with pytest.raises(RuntimeError, match="edit failed"):
        runpy.run_path(str(sample))

    job = operations.begin_create_generation_job.call_args.kwargs["job"]
    operations.delete_version.assert_called_once_with(name=job.evaluator_name, version="1")


def test_safety_generation_sample_distinguishes_unspecified_behavior(sample_clients, monkeypatch, capsys):
    project_client, _ = sample_clients
    definition = RubricBasedEvaluatorDefinition(
        dimensions=[
            Dimension(id="permitted", description="Allowed behavior", allowed=True),
            Dimension(id="prohibited", description="Disallowed behavior", allowed=False),
            Dimension(id="unspecified", description="Missing classification"),
        ]
    )
    poller = project_client.evaluators.begin_create_generation_job.return_value
    poller.done.return_value = True
    poller.result.return_value = SimpleNamespace(name="test", version="1", definition=definition)
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "test-agent")
    monkeypatch.delenv("FOUNDRY_REFERENCE_DATASET_NAME", raising=False)
    monkeypatch.delenv("FOUNDRY_REFERENCE_DATASET_VERSION", raising=False)

    sample = Path(__file__).parents[2] / "samples" / "evaluations" / "sample_rubric_evaluator_generation_all_sources.py"
    runpy.run_path(str(sample))
    output = capsys.readouterr().out
    assert "[allowed] permitted: Allowed behavior" in output
    assert "[disallowed] prohibited: Disallowed behavior" in output
    assert "[unspecified] unspecified: Missing classification" in output
