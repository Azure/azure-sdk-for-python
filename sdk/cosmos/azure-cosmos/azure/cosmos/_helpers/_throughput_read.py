# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared input validation and result ownership for throughput reads."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping, Optional

from .._backend.capabilities import OperationRouting
from .._backend.constants import is_rust_backend
from .._base import _deserialize_throughput
from .._cosmos_responses import CosmosDict
from .._offer_rust_routing import offer_response_headers
from ..offer import ThroughputProperties
from ._request_settings import COMMON_OPTIONS, is_supported_operation_timeout, prepare_service_request_settings
from ._response_parse import with_response_header_snapshot


def prepare_read_kwargs(
    kwargs: Mapping[str, Any],
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
) -> dict[str, Any]:
    if response_hook is not None and not callable(response_hook):
        raise TypeError("response_hook must be callable or None")
    copied = dict(kwargs)
    for name in ("request_options", "feed_options"):
        if name in copied:
            if not isinstance(copied[name], Mapping):
                raise TypeError(f"{name} must be a mapping")
            copied[name] = deepcopy(dict(copied[name]))
    for name in COMMON_OPTIONS:
        if name in copied:
            copied[name] = deepcopy(copied[name])
    if isinstance(copied.get("options"), Mapping):
        copied["options"] = deepcopy(dict(copied["options"]))
    return copied


def read_routing(
    backend: Any,
    options: Mapping[str, Any],
    *,
    supported: bool,
    capability: str,
) -> OperationRouting:
    routing = OperationRouting(
        "read_offer",
        supported and is_supported_operation_timeout(options.get("timeout")),
        capability=capability,
    )
    if is_rust_backend(backend):
        routing.uses_legacy()
        prepare_service_request_settings(options, {}, resource_type="offers")
    return routing


def legacy_read_kwargs(
    options: dict[str, Any], transport_kwargs: Mapping[str, Any], original_kwargs: Mapping[str, Any],
) -> dict[str, Any]:
    result = dict(transport_kwargs)
    result.setdefault("options", options)
    if "timeout" in original_kwargs:
        result["timeout"] = original_kwargs["timeout"]
    return result


def finish_read(
    offers: list[dict[str, Any]],
    client_connection: Any,
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
) -> ThroughputProperties:
    """Finish a nonempty lookup without allowing callback mutation of its result."""
    headers = offer_response_headers(offers, client_connection)
    result = _deserialize_throughput(
        throughput=[CosmosDict(deepcopy(offers[0]), response_headers=headers)]
    )
    hook = with_response_header_snapshot(response_hook, copy_body=True)
    if hook is not None:
        hook(headers, offers)
    return result
