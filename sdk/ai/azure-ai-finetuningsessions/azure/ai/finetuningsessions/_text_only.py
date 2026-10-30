# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared handwritten text-only serialization and result selection."""

import json
import math
import re
from collections.abc import Mapping
from typing import Any, Callable, Optional, cast

from azure.core.exceptions import DecodeError

from ._exceptions import MalformedResponseError
from ._utils.model_base import SdkJSONEncoder, _deserialize
from .models import (
    OperationResult,
    TextOnlyInvalidSampleChoice,
    TextOnlySampleChoice,
    TextOnlySampleOperationResult,
)


def _object(value: Any, allowed: set[str], required: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) - allowed or required - set(value):
        raise ValueError(f"Expected an object with required keys {sorted(required)} and allowed keys {sorted(allowed)}")
    return value


def _string(value: Any) -> None:
    if not isinstance(value, str):
        raise ValueError("Expected a text string")


def _name(value: Any) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", value) is None:
        raise ValueError("Expected a function name of 1-64 letters, digits, underscores or hyphens")


def _identifier(value: Any) -> None:
    if not isinstance(value, str) or not value or len(value) > 256 or any(c.isspace() for c in value):
        raise ValueError("Expected a nonempty identifier without whitespace (at most 256 characters)")


def _list(value: Any, *, nonempty: bool = False) -> list:
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError("Expected a nonempty list" if nonempty else "Expected a list")
    return value


def _reject_constant(value: str) -> None:
    raise ValueError(f"Non-finite JSON value: {value}")


def _sample_input(value: Any) -> dict:  # pylint: disable=too-many-statements
    data = _object(value, {"messages", "tools"}, {"messages"})
    calls: dict[str, str] = {}
    for message in _list(data["messages"], nonempty=True):
        if not isinstance(message, Mapping):
            raise ValueError("Expected a public text message")
        role = message.get("role")
        if role in ("system", "user"):
            _object(message, {"role", "content"}, {"role", "content"})
            _string(message["content"])
        elif role == "assistant":
            _object(message, {"role", "content", "tool_calls"}, {"role"})
            if message.get("content") is not None:
                _string(message["content"])
            tool_calls = _list(message.get("tool_calls", []))
            if message.get("content") is None and not tool_calls:
                raise ValueError("Assistant content or tool calls are required")
            for call in tool_calls:
                _object(call, {"id", "type", "function"}, {"id", "type", "function"})
                _identifier(call["id"])
                if call["type"] != "function" or call["id"] in calls:
                    raise ValueError("Expected function calls with unique IDs")
                function = _object(call["function"], {"name", "arguments"}, {"name", "arguments"})
                _name(function["name"])
                _string(function["arguments"])
                arguments = json.loads(function["arguments"], parse_constant=_reject_constant)
                if not isinstance(arguments, dict):
                    raise ValueError("Function arguments must encode a JSON object")
                json.dumps(arguments, allow_nan=False)
                calls[call["id"]] = function["name"]
        elif role == "tool":
            _object(message, {"role", "tool_call_id", "content", "name"}, {"role", "tool_call_id", "content"})
            _identifier(message["tool_call_id"])
            _string(message["content"])
            expected = calls.get(message["tool_call_id"])
            if "name" in message:
                _name(message["name"])
                if expected is not None and expected != message["name"]:
                    raise ValueError("Tool-result name does not match its supplied call")
            elif expected is None:
                raise ValueError("A tool result without its preceding call requires name")
        else:
            raise ValueError("Only system, user, assistant and tool text messages are supported")
    names = set()
    for tool in _list(data.get("tools", [])):
        _object(tool, {"type", "function"}, {"type", "function"})
        if tool["type"] != "function":
            raise ValueError("Only function tools are supported")
        function = _object(tool["function"], {"name", "description", "parameters"}, {"name", "parameters"})
        _name(function["name"])
        if function["name"] in names:
            raise ValueError("Function definition names must be unique")
        names.add(function["name"])
        if "description" in function:
            _string(function["description"])
        parameters = function["parameters"]
        if not isinstance(parameters, Mapping) or parameters.get("type") != "object":
            raise ValueError("Function parameters must describe a JSON object")
    return json.loads(json.dumps(data, allow_nan=False))


def _text_sample_body(
    text_only_input: Any,
    prompt_tokens: Any,
    sampling_params: Any,
    *,
    num_samples: int,
    sampling_session_id: Optional[str],
    seq_id: Optional[int],
    prompt_logprobs: bool,
    topk_prompt_logprobs: int,
) -> dict:
    if prompt_tokens is not None:
        raise ValueError("Supply exactly one of prompt_tokens or text_only_input")
    if prompt_logprobs or topk_prompt_logprobs:
        raise ValueError("Text-only sampling does not support prompt logprobs")
    params = json.loads(json.dumps(sampling_params, cls=SdkJSONEncoder, exclude_readonly=True))
    if not isinstance(params, dict):
        raise ValueError("sampling_params is required")
    for key in ("response_format", "stop_criteria", "stop", "stop_token_ids"):
        if params.get(key) is not None:
            raise ValueError(f"Text-only sampling does not support {key}; model-native stops are supplied by the codec")
    body = {"text_only_input": _sample_input(text_only_input), "sampling_params": params, "num_samples": num_samples}
    if sampling_session_id is not None:
        body["sampling_session_id"] = sampling_session_id
    if seq_id is not None:
        body["seq_id"] = seq_id
    return body


def _text_training_body(text_only_input: Any, batch: Any, loss_fn: Any, loss_fn_config: Any) -> dict:
    if batch is not None or loss_fn != "cross_entropy" or loss_fn_config is not None:
        raise ValueError("Supply text_only_input alone; put the reference loss function/config inside it")
    data = dict(_object(text_only_input, {"samples", "loss_fn", "loss_fn_config"}, {"samples"}))
    refs = set()
    for sample in _list(data["samples"], nonempty=True):
        _object(sample, {"sample_ref", "advantage"}, {"sample_ref", "advantage"})
        ref = sample["sample_ref"]
        if not isinstance(ref, str) or not ref or ref in refs:
            raise ValueError("Sample references must be nonempty, unique opaque strings")
        refs.add(ref)
        advantage = sample["advantage"]
        try:
            finite = type(advantage) in (int, float) and math.isfinite(advantage)
        except OverflowError:
            finite = False
        if not finite:
            raise ValueError("Each sample reference requires one finite numeric advantage")
    data.setdefault("loss_fn", "importance_sampling")
    if data["loss_fn"] not in ("importance_sampling", "ppo", "cispo", "sapo"):
        raise ValueError("Unsupported text-only loss function")
    if data.get("loss_fn_config") is not None and not isinstance(data["loss_fn_config"], Mapping):
        raise ValueError("loss_fn_config must be an object")
    return {"text_only_input": json.loads(json.dumps(data, allow_nan=False))}


def _is_protected_mutation(subpath: str, body: Any) -> bool:
    return isinstance(body, Mapping) and (subpath.endswith("/forward_backward") and "text_only_input" in body)


def _text_training_response(
    load_json: Callable[[], Any],
    *,
    submission: bool,
    on_submit: Optional[Callable[[str], None]] = None,
) -> dict:
    try:
        body = load_json()
    except (DecodeError, ValueError) as exc:
        raise MalformedResponseError("Protected training returned invalid JSON") from exc
    if not isinstance(body, dict):
        raise MalformedResponseError("Protected training response must be an object")
    if submission:
        request_id = body.get("request_id")
        session_id = body.get("session_id")
        if not isinstance(request_id, str) or not request_id.strip():
            raise MalformedResponseError("Protected training response requires a nonempty request_id")
        if on_submit is not None:
            on_submit(request_id)
        if "session_id" in body and (not isinstance(session_id, str) or not session_id.strip()):
            raise MalformedResponseError(
                "Protected training response has an invalid session_id",
                request_id=request_id,
            )
    elif body.get("status") not in ("pending", "completed", "failed"):
        raise MalformedResponseError("Protected training response has an invalid operation status")
    elif body["status"] == "completed":
        result = body.get("result")
        if (
            not isinstance(result, dict)
            or result.get("loss_fn_output_type") != "scalar"
            or result.get("loss_fn_outputs") != []
            or not isinstance(result.get("metrics"), dict)
        ):
            raise MalformedResponseError("Protected training response requires a scalar training result")
        for value in result["metrics"].values():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise MalformedResponseError("Protected training metrics must be finite numbers")
            try:
                finite = math.isfinite(value)
            except OverflowError as exc:
                raise MalformedResponseError("Protected training metrics must be finite numbers") from exc
            if not finite:
                raise MalformedResponseError("Protected training metrics must be finite numbers")
    return body


def _operation_result(normalized: dict) -> OperationResult:
    if normalized.get("type", "sample") == "sample" and "choices" in normalized:
        choices = []
        indices = set()
        refs = set()
        for choice in _list(normalized["choices"], nonempty=True):
            if (
                not isinstance(choice, Mapping)
                or not isinstance(choice.get("sample_ref"), str)
                or not choice["sample_ref"]
            ):
                raise ValueError("Text-only choices must contain nonempty opaque string sample references")
            index = choice.get("index")
            if (
                type(index) is not int  # pylint: disable=unidiomatic-typecheck
                or index < 0
                or index in indices
                or choice["sample_ref"] in refs
            ):
                raise ValueError("Text-only choices require unique nonnegative indices and references")
            indices.add(index)
            refs.add(choice["sample_ref"])
            if "outcome" in choice:
                _object(
                    choice,
                    {"index", "sample_ref", "outcome", "reason", "finish_reason"},
                    {"index", "sample_ref", "outcome", "reason", "finish_reason"},
                )
                if (
                    choice["outcome"] != "invalid_model_output"
                    or choice["reason"]
                    not in (
                        "output_token_limit",
                        "missing_private_boundary",
                        "malformed_tool_call",
                        "invalid_tool_arguments",
                        "invalid_public_output",
                    )
                    or choice["finish_reason"] not in ("stop", "length")
                    or (choice["finish_reason"] == "length") != (choice["reason"] == "output_token_limit")
                ):
                    raise ValueError("Invalid protected completion classification")
                choices.append(_deserialize(TextOnlyInvalidSampleChoice, choice))
            else:
                _object(
                    choice,
                    {"index", "message", "sample_ref", "finish_reason"},
                    {"index", "message", "sample_ref", "finish_reason"},
                )
                if choice["finish_reason"] not in ("stop", "tool_calls"):
                    raise ValueError("Invalid public completion termination")
                _sample_input({"messages": [choice["message"]]})
                if choice["message"].get("role") != "assistant" or (
                    bool(choice["message"].get("tool_calls")) != (choice["finish_reason"] == "tool_calls")
                ):
                    raise ValueError("Public completion must be an assistant action matching its termination")
                choices.append(_deserialize(TextOnlySampleChoice, choice))
        result = cast(
            TextOnlySampleOperationResult, _deserialize(TextOnlySampleOperationResult, {**normalized, "choices": []})
        )
        result.choices = choices
        return result
    return cast(OperationResult, _deserialize(OperationResult, normalized))
