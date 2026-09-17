# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Public item argument rules, operation budgets and patch-body snapshots."""

from __future__ import annotations

import time
from typing import Any, Mapping, Optional

from ._request_settings import get_match_headers, is_supported_operation_timeout
from ._wire_encoding import serialize_body_to_bytes


def prepare_item_deadline(
    kwargs: dict[str, Any], method: str, started: float
) -> Optional[float]:
    """Copy request options and return the budget owned by this public call."""
    options = dict(kwargs.get("request_options") or {})
    kwargs["request_options"] = options
    timeout = kwargs.get("timeout", options.get("timeout"))
    if not is_supported_operation_timeout(timeout):
        raise ValueError(
            f"{method} timeout must be None or a finite number of seconds >= 1 and < 2**64."
        )
    if timeout is None:
        return None
    kwargs["timeout"] = timeout
    return started + float(timeout)


def prepare_create_item_kwargs(kwargs: dict[str, Any]) -> Optional[float]:
    """Reject retired arguments by presence and establish the create budget."""
    for name in ("populate_query_metrics", "etag", "match_condition"):
        if name in kwargs:
            raise TypeError(f"create_item() does not accept '{name}'.")
    return prepare_item_deadline(kwargs, "create_item", time.monotonic())


def prepare_item_target(kwargs: dict[str, Any], item: Any) -> None:
    """Retain mapping validation without building a legacy document address."""
    if "document_link" in kwargs or "_item_self_link" in kwargs:
        raise TypeError("Item addressing must be supplied through the item argument.")
    if not isinstance(item, str):
        kwargs["_item_self_link"] = item["_self"]


def prepare_read_item_kwargs(
    kwargs: dict[str, Any], partition_key: Any
) -> Optional[float]:
    """Validate before metadata I/O and isolate the caller's option mapping."""
    if "populate_query_metrics" in kwargs:
        raise TypeError("read_item() does not accept 'populate_query_metrics'.")
    options = dict(kwargs.get("request_options") or {})
    if_match, if_none_match = get_match_headers(kwargs)
    # Wildcard conditions ignore an accompanying ETag; never leak it to transport.
    kwargs.pop("etag", None)
    if if_match:
        options["accessCondition"] = {"type": "IfMatch", "condition": if_match}
    if if_none_match:
        options["accessCondition"] = {"type": "IfNoneMatch", "condition": if_none_match}
    options["partitionKey"] = partition_key
    kwargs["request_options"] = options
    deadline = prepare_item_deadline(kwargs, "read_item", time.monotonic())
    if deadline is not None:
        kwargs["_item_operation_deadline"] = deadline
    return deadline


def build_patch_operations_payload(patch_operations: Any) -> dict[str, Any]:
    """Use the service's canonical increment spelling, also accepted by the driver."""
    if not isinstance(patch_operations, list):
        raise TypeError("patch_operations must be a list of operation dictionaries.")
    if not patch_operations:
        raise ValueError("patch_operations must not be empty.")
    translated = []
    for operation in patch_operations:
        if not isinstance(operation, dict):
            raise TypeError("Each patch operation must be a dictionary.")
        if operation.get("op") == "increment":
            operation = {**operation, "op": "incr"}
        translated.append(operation)
    return {"operations": translated}


def serialize_patch_body(patch_operations: Any, *, compact_utf8: bool = False) -> bytes:
    """Snapshot the operations before backend dispatch can yield to caller code."""
    return serialize_body_to_bytes(
        build_patch_operations_payload(patch_operations),
        ensure_ascii=not compact_utf8,
        allow_nan=False,
    )


def prepare_patch_item_kwargs(kwargs: dict[str, Any]) -> None:
    """Normalize caller guards and establish one operation budget."""
    hook = kwargs.get("response_hook")
    if hook is not None and not callable(hook):
        raise TypeError("patch_item response_hook must be callable.")
    if_match, if_none_match = get_match_headers(kwargs)
    kwargs.pop("etag", None)
    if if_none_match is not None:
        raise NotImplementedError(
            "The Rust patch backend does not support If-None-Match."
        )
    if if_match is not None:
        if not isinstance(if_match, str) or not if_match.strip():
            raise ValueError("patch_item If-Match must be a non-empty ETag string.")
        kwargs["if_match"] = if_match
    if "_item_operation_deadline" not in kwargs:
        deadline = prepare_item_deadline(kwargs, "patch_item", time.monotonic())
        if deadline is not None:
            kwargs["_item_operation_deadline"] = deadline


def apply_patch_item_options(options: dict[str, Any]) -> None:
    """Reject unsupported guards and ambiguous header overrides before I/O."""
    if options.get("filterPredicate") is not None:
        raise NotImplementedError("The Rust backend does not support filtered patches.")
    options.pop("filterPredicate", None)
    matches = []
    condition = options.get("accessCondition")
    if condition is not None:
        if not isinstance(condition, Mapping):
            raise TypeError("patch_item access_condition must be a mapping.")
        kind = condition.get("type")
        if kind == "IfNoneMatch":
            raise NotImplementedError(
                "The Rust patch backend does not support If-None-Match."
            )
        if kind != "IfMatch":
            raise ValueError("patch_item access_condition must specify IfMatch.")
        matches.append(condition.get("condition"))

    initial = options.get("initialHeaders")
    if initial is not None and not isinstance(initial, Mapping):
        raise TypeError("patch_item initial_headers must be a mapping.")
    initial = dict(initial or {})
    for headers in (initial, options):
        for name in list(headers):
            if not isinstance(name, str):
                raise TypeError("Request header names must be strings.")
            if name.lower() == "if-none-match":
                raise NotImplementedError(
                    "The Rust patch backend does not support If-None-Match."
                )
            if name.lower() == "if-match":
                matches.append(headers.pop(name))
    if matches:
        if any(not isinstance(value, str) or not value.strip() for value in matches):
            raise ValueError("patch_item If-Match must be a non-empty ETag string.")
        if any(value != matches[0] for value in matches[1:]):
            raise ValueError("patch_item received conflicting If-Match conditions.")
        options["accessCondition"] = {"type": "IfMatch", "condition": matches[0]}
    if "initialHeaders" in options:
        options["initialHeaders"] = initial
