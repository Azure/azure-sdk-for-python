# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""T17 audit meta-test: no response/item JSON body reaches a client unstripped.

Statically walks ``_endpoint_handler.py`` for every ``JSONResponse(...)`` call
and fails if a response/item-shaped body is returned without going through
``strip_internal_metadata`` (spec 025 §A.2). Also asserts the SSE encoder is the
single, stripping chokepoint.
"""

from __future__ import annotations

import ast
from pathlib import Path

import azure.ai.agentserver.responses.hosting._endpoint_handler as endpoint_handler
import azure.ai.agentserver.responses.streaming._sse as sse_module

# First-arg shapes that are NOT response/item bodies (errors, status envelopes).
_SAFE_NAMES = {"err_body", "terminal_error", "headers"}
_SAFE_DICT_KEYS = {"id", "object", "deleted", "error"}


def _first_arg_is_safe(arg: ast.expr) -> bool:
    """Return True if the JSONResponse body cannot carry internal_metadata."""
    # Wrapped in strip_internal_metadata(...) — always safe.
    if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id == "strip_internal_metadata":
        return True
    # Error/status helper variable (e.g. err_body, terminal_error).
    if isinstance(arg, ast.Name) and arg.id in _SAFE_NAMES:
        return True
    # exc.response_body style error envelope.
    if isinstance(arg, ast.Attribute) and arg.attr == "response_body":
        return True
    # Literal dict whose string keys are all status/error keys (delete, error, {}).
    if isinstance(arg, ast.Dict):
        keys = [k.value for k in arg.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)]
        if all(k in _SAFE_DICT_KEYS for k in keys):
            return True
    return False


def test_t17_all_jsonresponse_bodies_stripped_or_safe():
    source = Path(endpoint_handler.__file__).read_text()
    tree = ast.parse(source)
    offenders: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        is_jsonresponse = (isinstance(func, ast.Name) and func.id == "JSONResponse") or (
            isinstance(func, ast.Attribute) and func.attr == "JSONResponse"
        )
        if not is_jsonresponse or not node.args:
            continue
        if not _first_arg_is_safe(node.args[0]):
            offenders.append(node.lineno)
    assert not offenders, (
        "JSONResponse body returned without strip_internal_metadata (or a recognised "
        f"error/status shape) at _endpoint_handler.py lines: {offenders}. "
        "Wrap response/item bodies in strip_internal_metadata(...) per spec 025 §A.2."
    )


def test_t17_sse_encoder_is_single_stripping_chokepoint():
    """The SSE frame builder is only reachable via the stripping encoder."""
    source = Path(sse_module.__file__).read_text()
    # encode_sse_event must call strip_internal_metadata.
    assert "strip_internal_metadata" in source, "SSE encoder must call strip_internal_metadata"
    tree = ast.parse(source)
    build_frame_callers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for inner in ast.walk(node):
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Name)
                    and inner.func.id == "_build_sse_frame"
                ):
                    build_frame_callers.add(node.name)
    # Only encode_sse_event constructs SSE frames; everything else delegates to it.
    assert build_frame_callers <= {"encode_sse_event"}, (
        f"_build_sse_frame called outside the stripping encoder by: {build_frame_callers}"
    )
