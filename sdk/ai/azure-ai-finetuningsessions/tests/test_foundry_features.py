# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Canonical shared preview values preserve the existing fine-tuning header."""

import json

import pytest

from azure.ai.finetuningsessions import models
from azure.ai.finetuningsessions.models import FoundryFeaturesOptInKeys
from azure.ai.finetuningsessions.operations import _operations as generated

MEMBERS = {
    "EVALUATIONS_V1_PREVIEW": "Evaluations=V1Preview",
    "SCHEDULES_V1_PREVIEW": "Schedules=V1Preview",
    "RED_TEAMS_V1_PREVIEW": "RedTeams=V1Preview",
    "INSIGHTS_V1_PREVIEW": "Insights=V1Preview",
    "AGENT_INSIGHTS_V1_PREVIEW": "AgentInsights=V1Preview",
    "MEMORY_STORES_V1_PREVIEW": "MemoryStores=V1Preview",
    "ROUTINES_V2_PREVIEW": "Routines=V2Preview",
    "SKILLS_V1_PREVIEW": "Skills=V1Preview",
    "DATA_GENERATION_JOBS_V1_PREVIEW": "DataGenerationJobs=V1Preview",
    "MODELS_V1_PREVIEW": "Models=V1Preview",
    "MODEL_ROUTER_CONTROLS_V1_PREVIEW": "ModelRouterControls=V1Preview",
    "FINETUNING_SESSIONS_V1_PREVIEW": "FineTuningSessions=V1Preview",
}


def test_canonical_members_preserve_names_values_and_order():
    assert models.__all__.count("FoundryFeaturesOptInKeys") == 1
    assert len(FoundryFeaturesOptInKeys.__members__) == 12
    assert [(name, member.value) for name, member in FoundryFeaturesOptInKeys.__members__.items()] == list(
        MEMBERS.items()
    )
    assert issubclass(FoundryFeaturesOptInKeys, str)


@pytest.mark.parametrize("name,value", MEMBERS.items())
def test_canonical_members_remain_string_backed_and_case_insensitive(name, value):
    member = getattr(FoundryFeaturesOptInKeys, name)
    assert member == value
    assert FoundryFeaturesOptInKeys(value) is member
    assert FoundryFeaturesOptInKeys[name.lower()] is member
    assert getattr(FoundryFeaturesOptInKeys, name.lower()) is member
    with pytest.raises(ValueError):
        FoundryFeaturesOptInKeys(value.lower())
    assert json.loads(json.dumps(member)) == value


@pytest.mark.parametrize(
    "value",
    [
        FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW,
        "FineTuningSessions=V1Preview",
        "FutureFeature=V9Preview",
    ],
)
def test_request_builder_preserves_explicit_header_without_enum_coercion(value):
    request = generated.build_sessions_get_request(session_id="session_test", foundry_features=value, api_version="v1")
    assert request.method == "GET"
    assert request.url == "/fine_tuning/sessions/session_test?api-version=v1"
    assert request.headers["Foundry-Features"] == value
    assert request.headers["Accept"] == "application/json"
