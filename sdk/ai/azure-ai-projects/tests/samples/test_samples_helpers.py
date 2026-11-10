# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared base code for sample tests - sync dependencies only."""

import functools
import math
from typing import Mapping, Any
from devtools_testutils import EnvironmentVariableLoader, add_body_key_sanitizer
from llm_instructions import (
    agent_tools_instructions,
    agents_instructions,
    chat_completions_instructions,
    memories_instructions,
    resource_management_instructions,
)

_AUDIO_DATASET_ID = "azureai://accounts/sanitized-account-name/projects/sanitized-project-name/data/audio-conversations/versions/1"

audioEvaluationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "",
    foundry_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    foundry_model_name="sanitized-model-deployment-name",
    foundry_dataset_id=_AUDIO_DATASET_ID,
)

voiceSimulationPreparer = functools.partial(
    EnvironmentVariableLoader,
    "",
    foundry_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    foundry_model_name="sanitized-model-deployment-name",
    foundry_agent_name="sanitized-agent-name",
    foundry_agent_version="1",
    foundry_simulator_model_name="sanitized-model-deployment-name",
    foundry_simulator_voice="en-US-AvaNeural",
)


def sanitize_audio_evaluation_dataset():
    # Account/project sanitizers run before the preparer's full-ID replacement.
    add_body_key_sanitizer(
        json_path="data_source.source.id", value=_AUDIO_DATASET_ID, function_scoped=True
    )


def assert_audio_evaluation_results(output_calls, metrics):
    """Check grading completeness without treating low scores as execution failures."""
    assert output_calls, "The sample produced no evaluation output items"
    for call in output_calls:
        item = call.args[0].model_dump()
        results = item["results"]
        assert len(results) == len(metrics)
        assert {result["name"] for result in results} == set(metrics)
        for result in results:
            assert result.get("status") == "completed", result
            assert not result.get("error"), result
            score = result.get("score")
            assert isinstance(score, (int, float)) and not isinstance(score, bool)
            assert math.isfinite(score)


def get_sample_env_vars(env_kwargs: Mapping[str, Any]) -> dict[str, str]:
    # Map sample env-var names (uppercase) to string values only.
    # Non-string values are filtered out to maintain type safety.
    mapping: dict[str, str] = {}
    for key, value in env_kwargs.items():
        if isinstance(key, str) and isinstance(value, str):
            mapping[key.upper()] = value
    return mapping
