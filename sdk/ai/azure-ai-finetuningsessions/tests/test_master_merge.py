# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Protect master's SDK contracts while retaining the pinned generated base."""

import inspect
import json
from pathlib import Path
import re

import pytest

from azure.ai.finetuningsessions import FineTuningSession
from azure.ai.finetuningsessions.aio import FineTuningSessionClient
from azure.ai.finetuningsessions.models import (
    CreateSessionRequest,
    LoRAConfig,
    ModelInput,
    ModelInputChunk,
    SampleRequest,
    SamplingParams,
)
from azure.ai.finetuningsessions._utils.model_base import SdkJSONEncoder


@pytest.mark.parametrize(
    "method",
    [
        FineTuningSession.create,
        FineTuningSession.create_from_checkpoint,
        FineTuningSessionClient.create_session,
        FineTuningSessionClient.create_session_from_checkpoint,
    ],
)
def test_creation_requires_explicit_lora_configuration(method):
    parameter = inspect.signature(method).parameters["lora_config"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty


@pytest.mark.parametrize("mapping", [False, True])
@pytest.mark.parametrize("data", [{}, {"rank": None}])
def test_rank_validation_covers_mapping_and_keyword_construction(mapping, data):
    with pytest.raises(ValueError, match="lora_config.rank is required"):
        LoRAConfig(data) if mapping else LoRAConfig(**data)


@pytest.mark.parametrize("mapping", [False, True])
@pytest.mark.parametrize("explicit_none", [False, True])
def test_configuration_validation_covers_mapping_and_keyword_construction(mapping, explicit_none):
    data = {"type": "training", "base_model": "test-model"}
    if explicit_none:
        data["lora_config"] = None
    with pytest.raises(ValueError, match="lora_config is required"):
        CreateSessionRequest(data) if mapping else CreateSessionRequest(**data)


@pytest.mark.parametrize("mapping", [False, True])
def test_nested_configuration_uses_the_public_rank_validator(mapping):
    data = {"type": "training", "base_model": "test-model", "lora_config": {}}
    with pytest.raises(ValueError, match="lora_config.rank is required"):
        CreateSessionRequest(data) if mapping else CreateSessionRequest(**data)


@pytest.mark.parametrize(
    "response_format",
    [
        {"type": "json_object"},
        {"type": "json_schema", "json_schema": {"name": "Answer", "schema": {"type": "object"}, "strict": True}},
    ],
)
def test_nested_sampling_preserves_structured_response_format(response_format):
    params = {
        "max_tokens": 16,
        "temperature": 1.0,
        "top_p": 1.0,
        "top_k": -1,
        "response_format": response_format,
    }
    request = SampleRequest(
        num_samples=1,
        prompt=ModelInput(chunks=[ModelInputChunk(tokens=[1, 2])]),
        sampling_params=params,
        topk_prompt_logprobs=0,
    )
    assert isinstance(request.sampling_params, SamplingParams)
    assert request.sampling_params.response_format == response_format
    payload = json.loads(json.dumps(request, cls=SdkJSONEncoder, exclude_readonly=True))
    assert payload["sampling_params"] == params


def test_current_generation_pin_matches_provenance():
    package = Path(__file__).resolve().parents[1]
    provenance = json.loads((package / "eng/generation/provenance.json").read_text(encoding="utf-8"))
    guide = (package / "GENERATION.md").read_text(encoding="utf-8")
    section = guide.split("## Current source pin and review validation", 1)[1].split("\n## ", 1)[0]
    public = "https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/"
    assert f"[tsp-location.yaml]({public}tsp-location.yaml)" in section
    assert f"[eng/generation/provenance.json]({public}eng/generation/provenance.json)" in section
    pointer = (package / "tsp-location.yaml").read_text(encoding="utf-8")
    pin = re.search(r"(?m)^commit:\s*([0-9a-f]{40})\s*$", pointer)
    assert pin is not None
    assert pin.group(1) == provenance["typespec"]["commit"]
