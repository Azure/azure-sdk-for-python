# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for the scenario-specific data generation job input models."""

import pytest
from azure.ai.projects.models import (
    DataGenerationJob,
    DataGenerationJobInputs,
    DataGenerationJobOutputWriteMode,
    DataGenerationModelOptions,
    EvaluationDataGenerationJobInputs,
    EvaluationDataGenerationJobOutputTarget,
    PromptDataGenerationJobSource,
    ReinforcementFineTuningDataGenerationJobInputs,
    ReinforcementFineTuningDataGenerationJobOutputTarget,
    SimpleQnADataGenerationJobOptions,
    SupervisedFineTuningDataGenerationJobInputs,
    SupervisedFineTuningDataGenerationJobOutputTarget,
)


def _sources():
    return [PromptDataGenerationJobSource(description="Seed prompt.", prompt="Generate questions about widgets.")]


def _generation_configuration():
    return SimpleQnADataGenerationJobOptions(max_samples=15, model_options=DataGenerationModelOptions(model="gpt-4o"))


@pytest.mark.parametrize(
    "inputs_cls, output_cls, scenario",
    [
        (EvaluationDataGenerationJobInputs, EvaluationDataGenerationJobOutputTarget, "evaluation"),
        (
            SupervisedFineTuningDataGenerationJobInputs,
            SupervisedFineTuningDataGenerationJobOutputTarget,
            "supervised_finetuning",
        ),
        (
            ReinforcementFineTuningDataGenerationJobInputs,
            ReinforcementFineTuningDataGenerationJobOutputTarget,
            "reinforcement_finetuning",
        ),
    ],
)
def test_data_generation_job_inputs_serialize_scenario_discriminator(inputs_cls, output_cls, scenario):
    inputs = inputs_cls(
        name="sample-job",
        sources=_sources(),
        generation_configuration=_generation_configuration(),
        output_configuration=output_cls(name="sample-output", write_mode=DataGenerationJobOutputWriteMode.OVERWRITE),
    )

    payload = inputs.as_dict()

    assert payload["scenario"] == scenario
    assert payload["name"] == "sample-job"
    assert payload["generation_configuration"]["max_samples"] == 15
    assert payload["output_configuration"] == {"name": "sample-output", "write_mode": "overwrite"}
    assert payload["sources"][0]["prompt"] == "Generate questions about widgets."
    assert "options" not in payload
    assert "output_options" not in payload


def test_data_generation_job_inputs_deserialize_to_scenario_subclass():
    payload = {
        "name": "sample-job",
        "scenario": "supervised_finetuning",
        "sources": [{"type": "prompt", "prompt": "Generate questions."}],
        "generation_configuration": {"type": "simple_qna", "max_samples": 15},
        "output_configuration": {"name": "sample-output"},
    }

    inputs = DataGenerationJobInputs(payload)
    job = DataGenerationJob({**payload, "id": "job-1", "status": "queued"})

    assert inputs.scenario == "supervised_finetuning"
    assert isinstance(inputs.generation_configuration, SimpleQnADataGenerationJobOptions)
    assert inputs.generation_configuration.max_samples == 15
    assert job.id == "job-1"
    assert job.name == "sample-job"
    assert job.scenario == "supervised_finetuning"
