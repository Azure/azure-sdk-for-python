# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Required service inputs and additive public sampling contracts."""

import ast
from copy import deepcopy
import inspect
import json
from types import SimpleNamespace
from typing import Any, Dict, Optional, get_args, get_origin, get_type_hints
from unittest.mock import AsyncMock, Mock

import pytest

from azure.ai.finetuningsessions import FineTuningSession, _unions, models
from azure.ai.finetuningsessions._patch import _SdkJSONEncoder
from azure.ai.finetuningsessions._utils.model_base import SdkJSONEncoder
from azure.ai.finetuningsessions.aio import FineTuningSessionClient
from azure.ai.finetuningsessions.models import (
    CreateSessionRequest,
    LoRAConfig,
    ModelInput,
    ModelInputChunk,
    OperationResult,
    SampledSequence,
    SampleOperationResult,
    SampleRequest,
    SamplingOperationResult,
    SamplingParams,
)


_CREATE_METHODS = [
    FineTuningSession.create,
    FineTuningSession.create_from_checkpoint,
    FineTuningSessionClient.create_session,
    FineTuningSessionClient.create_session_from_checkpoint,
]


def _wire(model):
    return json.loads(json.dumps(model, cls=_SdkJSONEncoder, exclude_readonly=True))


def _model_type_hints(model):
    # Generated base classes use TYPE_CHECKING-only imports. Supply their real
    # namespaces while resolving all inherited annotations; do not skip fields.
    return get_type_hints(model, localns={"_models": models, "_unions": _unions})


def _creation_options(method):
    options = {"base_model": "test-model"}
    if "checkpoint" in method.__name__:
        options["checkpoint_path"] = "loom://model_deadbeef/weights/checkpoint-1"
    return options


@pytest.mark.parametrize("method", _CREATE_METHODS)
def test_creation_requires_explicit_lora_configuration(method):
    parameter = inspect.signature(method).parameters["lora_config"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
    assert get_type_hints(method)["lora_config"] is LoRAConfig


@pytest.mark.parametrize(
    "model, field, annotation",
    [(LoRAConfig, "rank", int), (CreateSessionRequest, "lora_config", LoRAConfig)],
)
def test_required_model_annotations_and_keyword_overloads(model, field, annotation):
    assert _model_type_hints(model)[field] is annotation
    # Inspect overload source as well as runtime hints, including on Python 3.10
    # where typing.get_overloads is unavailable. Do not skip signature checks.
    definition = ast.parse(inspect.getsource(model)).body[0]
    overloads = [
        method
        for method in definition.body
        if isinstance(method, ast.FunctionDef)
        and method.name == "__init__"
        and any(parameter.arg == field for parameter in method.args.kwonlyargs)
    ]
    assert len(overloads) == 1
    overload = overloads[0]
    assert any(isinstance(decorator, ast.Name) and decorator.id == "overload" for decorator in overload.decorator_list)
    index = next(index for index, parameter in enumerate(overload.args.kwonlyargs) if parameter.arg == field)
    assert overload.args.kw_defaults[index] is None
    assert ast.unparse(overload.args.kwonlyargs[index].annotation) == annotation.__name__


@pytest.mark.parametrize("mapping", [False, True])
@pytest.mark.parametrize("data", [{}, {"rank": None}])
def test_rank_validation_covers_mapping_and_keyword_construction(mapping, data):
    original = deepcopy(data)
    with pytest.raises(ValueError, match="lora_config.rank is required"):
        LoRAConfig(data) if mapping else LoRAConfig(**data)
    assert data == original


@pytest.mark.parametrize("mapping", [False, True])
@pytest.mark.parametrize("explicit_none", [False, True])
def test_configuration_validation_covers_mapping_and_keyword_construction(mapping, explicit_none):
    data = {"type": "training", "base_model": "test-model"}
    if explicit_none:
        data["lora_config"] = None
    original = deepcopy(data)
    with pytest.raises(ValueError, match="lora_config is required"):
        CreateSessionRequest(data) if mapping else CreateSessionRequest(**data)
    assert data == original


@pytest.mark.parametrize("mapping", [False, True])
@pytest.mark.parametrize("config", [{}, {"rank": None}, {"alpha": 64.0}])
def test_nested_configuration_uses_the_public_rank_validator(mapping, config):
    data = {"type": "training", "base_model": "test-model", "lora_config": config}
    original = deepcopy(data)
    with pytest.raises(ValueError, match="lora_config.rank is required"):
        CreateSessionRequest(data) if mapping else CreateSessionRequest(**data)
    assert data == original


@pytest.mark.asyncio
@pytest.mark.parametrize("method", _CREATE_METHODS)
@pytest.mark.parametrize(
    "supplied, exception, message",
    [
        ({}, TypeError, "lora_config"),
        ({"lora_config": None}, ValueError, "lora_config is required"),
        ({"lora_config": {}}, ValueError, "lora_config.rank is required"),
        ({"lora_config": {"rank": None}}, ValueError, "lora_config.rank is required"),
        ({"lora_config": {"alpha": 64.0}}, ValueError, "lora_config.rank is required"),
    ],
    ids=["omitted-config", "null-config", "missing-rank", "null-rank", "alpha-without-rank"],
)
async def test_invalid_creation_inputs_are_rejected_before_io(method, supplied, exception, message):
    asynchronous = inspect.iscoroutinefunction(method)
    send = (AsyncMock if asynchronous else Mock)(side_effect=AssertionError("invalid input reached I/O"))
    client = SimpleNamespace(send_request=send)
    options = {**_creation_options(method), **deepcopy(supplied)}
    original = deepcopy(options)
    with pytest.raises(exception, match=message):
        if asynchronous:
            await method(client, **options)
        else:
            method(client, **options)
    send.assert_not_called()
    if asynchronous:
        send.assert_not_awaited()
    assert options == original


@pytest.mark.parametrize("mapping", [False, True])
@pytest.mark.parametrize("rank", [16, 32])
def test_lora_rank_does_not_inject_optional_service_defaults(mapping, rank):
    data = {"rank": rank}
    original = deepcopy(data)
    config = LoRAConfig(data) if mapping else LoRAConfig(**data)
    assert config.rank == rank
    assert config.alpha is None
    assert config.seed is None
    assert config.freeze_vision_tower is None
    assert config.freeze_multi_modal_projector is None
    assert config.as_dict() == {"rank": rank}
    assert _wire(config) == {"rank": rank}
    assert data == original


@pytest.mark.parametrize("mapping", [False, True])
@pytest.mark.parametrize("rank", [16, 32])
def test_nested_configuration_roundtrip_preserves_omissions_and_input(mapping, rank):
    data = {"type": "training", "base_model": "test-model", "lora_config": {"rank": rank}}
    original = deepcopy(data)
    request = CreateSessionRequest(data) if mapping else CreateSessionRequest(**data)
    assert isinstance(request.lora_config, LoRAConfig)
    assert request.lora_config.rank == rank
    assert request.lora_config.as_dict() == {"rank": rank}
    assert _wire(request) == original
    restored = CreateSessionRequest(_wire(request))
    assert isinstance(restored.lora_config, LoRAConfig)
    assert restored.lora_config.rank == rank
    assert _wire(restored) == original
    assert data == original


@pytest.mark.parametrize("mapping", [False, True])
@pytest.mark.parametrize("rank", [16, 32])
def test_explicit_optional_lora_settings_survive_nested_serialization(mapping, rank):
    data = {
        "rank": rank,
        "alpha": 64.0,
        "seed": 42,
        "freeze_vision_tower": False,
        "freeze_multi_modal_projector": True,
    }
    original = deepcopy(data)
    config = LoRAConfig(data) if mapping else LoRAConfig(**data)
    request = CreateSessionRequest(type="training", base_model="test-model", lora_config=config)
    serialized = _wire(request)["lora_config"]
    assert serialized == original
    assert serialized["rank"] == rank
    assert serialized["freeze_vision_tower"] is False
    assert serialized["freeze_multi_modal_projector"] is True
    assert data == original


class _RequestCaptured(Exception):
    """Stop at the fake I/O boundary after the real request is serialized."""


@pytest.mark.asyncio
@pytest.mark.parametrize("method", _CREATE_METHODS)
@pytest.mark.parametrize("rank", [16, 32])
@pytest.mark.parametrize("mapping", [False, True])
async def test_creation_serializes_only_the_explicit_rank_without_mutating_input(method, rank, mapping):
    data = {"rank": rank}
    config = data if mapping else LoRAConfig(rank=rank)
    original = deepcopy(data)
    asynchronous = inspect.iscoroutinefunction(method)
    send = (AsyncMock if asynchronous else Mock)(side_effect=_RequestCaptured)
    client = SimpleNamespace(send_request=send)
    with pytest.raises(_RequestCaptured):
        if asynchronous:
            await method(client, lora_config=config, **_creation_options(method))
        else:
            method(client, lora_config=config, **_creation_options(method))
    assert send.call_count == 1
    if asynchronous:
        assert send.await_count == 1
    request = send.call_args.args[0]
    assert request.method == "POST"
    assert json.loads(request.content)["lora_config"] == {"rank": rank}
    assert data == original
    if not mapping:
        assert config.as_dict() == {"rank": rank}


def test_sampling_result_alias_is_identical_and_publicly_exported():
    assert SamplingOperationResult is SampleOperationResult
    assert models.SamplingOperationResult is models.SampleOperationResult
    assert models.__all__.count("SamplingOperationResult") == 1
    assert models.__all__.count("SampleOperationResult") == 1
    exported = {}
    exec("from azure.ai.finetuningsessions.models import *", exported)
    assert exported["SamplingOperationResult"] is SampleOperationResult
    assert exported["SampleOperationResult"] is SampleOperationResult


@pytest.mark.parametrize("result_type", [SampleOperationResult, SamplingOperationResult], ids=["canonical", "alias"])
def test_sampling_result_annotations_retain_nested_nullability(result_type):
    hints = _model_type_hints(result_type)
    assert get_origin(hints["sequences"]) is list
    (element,) = get_args(hints["sequences"])
    if isinstance(element, str):
        # Python 3.10 can retain a string inside a built-in generic alias even
        # after get_type_hints. Check that exact reference and resolve it.
        assert element == "_models.SampledSequence"
        element = getattr(models, element.removeprefix("_models."))
    assert element is SampledSequence
    assert hints["prompt_logprobs"] == Optional[list[Optional[float]]]
    assert hints["topk_prompt_logprobs"] == Optional[list[Optional[list[tuple[int, float]]]]]


@pytest.mark.parametrize("result_type", [SampleOperationResult, SamplingOperationResult], ids=["canonical", "alias"])
@pytest.mark.parametrize("mapping", [False, True])
def test_sampling_result_alias_roundtrip_retains_typed_sequences_and_nullable_pairs(result_type, mapping):
    payload = {
        "type": "sample",
        "sequences": [{"tokens": [11, 12], "text": "answer", "logprobs": [-0.1, -0.2]}],
        "prompt_logprobs": [None, -1.5],
        "topk_prompt_logprobs": [None, [[7, -0.25], [9, -1.25]]],
        "metrics": {"latency_ms": 12, "cached": False},
    }
    original = deepcopy(payload)
    result = result_type(payload) if mapping else result_type(**{k: v for k, v in payload.items() if k != "type"})
    assert type(result) is SampleOperationResult
    assert isinstance(result.sequences[0], SampledSequence)
    assert result.sequences[0].tokens == [11, 12]
    assert result.sequences[0].text == "answer"
    assert result.prompt_logprobs == [None, -1.5]
    # The established runtime preserves JSON-array pairs as lists; tuple
    # annotations do not imply a conversion of the stored wire representation.
    assert result.topk_prompt_logprobs == [None, [[7, -0.25], [9, -1.25]]]
    assert _wire(result) == original
    restored = SamplingOperationResult(_wire(result))
    assert type(restored) is SampleOperationResult
    assert isinstance(restored.sequences[0], SampledSequence)
    assert restored.topk_prompt_logprobs == result.topk_prompt_logprobs
    assert _wire(restored) == original
    discriminated = OperationResult._deserialize(_wire(result), [])
    assert type(discriminated) is SampleOperationResult
    assert _wire(discriminated) == original
    assert payload == original


def test_sampling_response_format_annotation_is_optional_json_mapping():
    assert _model_type_hints(SamplingParams)["response_format"] == Optional[Dict[str, Any]]


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
    original = deepcopy(params)
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
    assert payload["sampling_params"] == original
    restored = SampleRequest(payload)
    assert isinstance(restored.sampling_params, SamplingParams)
    assert restored.sampling_params.response_format == response_format
    assert _wire(restored) == payload
    assert params == original


@pytest.mark.parametrize("mapping", [False, True])
@pytest.mark.parametrize("explicit_none", [False, True])
def test_sampling_response_format_omission_and_none_nested_roundtrip(mapping, explicit_none):
    data = {"max_tokens": 16, "temperature": 1.0, "top_p": 1.0, "top_k": -1}
    expected = deepcopy(data)
    if explicit_none:
        data["response_format"] = None
        if mapping:
            expected["response_format"] = None
    original = deepcopy(data)
    params = SamplingParams(data) if mapping else SamplingParams(**data)
    assert params.response_format is None
    assert _wire(params) == expected
    assert ("response_format" in params) is (mapping and explicit_none)
    request = SampleRequest(
        num_samples=1,
        prompt=ModelInput(chunks=[ModelInputChunk(tokens=[1, 2])]),
        sampling_params=params,
        topk_prompt_logprobs=0,
    )
    payload = _wire(request)
    assert payload["sampling_params"] == expected
    restored = SampleRequest(payload)
    assert isinstance(restored.sampling_params, SamplingParams)
    assert restored.sampling_params.response_format is None
    assert ("response_format" in restored.sampling_params) is (mapping and explicit_none)
    assert _wire(restored) == payload
    assert data == original


@pytest.mark.parametrize("mapping", [False, True])
@pytest.mark.parametrize("explicit_none", [False, True])
def test_nested_sampling_mapping_preserves_null_versus_omitted_response_format(mapping, explicit_none):
    params = {"max_tokens": 16, "temperature": 1.0, "top_p": 1.0, "top_k": -1}
    if explicit_none:
        params["response_format"] = None
    data = {
        "num_samples": 1,
        "prompt": {"chunks": [{"tokens": [1, 2]}]},
        "sampling_params": params,
        "topk_prompt_logprobs": 0,
    }
    original = deepcopy(data)
    request = SampleRequest(data) if mapping else SampleRequest(**data)
    assert isinstance(request.sampling_params, SamplingParams)
    assert request.sampling_params.response_format is None
    assert ("response_format" in request.sampling_params) is explicit_none
    payload = _wire(request)
    assert payload == original
    restored = SampleRequest(payload)
    assert isinstance(restored.sampling_params, SamplingParams)
    assert ("response_format" in restored.sampling_params) is explicit_none
    assert _wire(restored) == original
    assert data == original
