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
from ..offer import ThroughputProperties
from .._operation_deadline import legacy_deadline_kwargs, legacy_deadline_options
from ._request_settings import COMMON_OPTIONS, prepare_service_request_settings, validate_operation_timeout
from ._response_parse import with_response_header_snapshot
from ._throughput_rust_routing import offer_response_headers


def prepare_throughput_kwargs(
    kwargs: Mapping[str, Any],
    response_hook: Optional[Callable[..., None]],
) -> dict[str, Any]:
    """Validate a read or replacement callback and copy caller-owned options.

    :param Mapping[str, Any] kwargs: Call keywords whose nested request options are copied.
    :param callable or None response_hook: Callback checked for callability.
    :return: Call keywords with independent nested option mappings.
    :rtype: dict[str, Any]
    """
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
    routing = OperationRouting("get_throughput", supported, capability=capability)
    if is_rust_backend(backend):
        validate_operation_timeout(options.get("timeout"))
        routing.require_rust_support()
        prepare_service_request_settings(options, {}, resource_type="offers")
    return routing


def legacy_throughput_kwargs(
    options: dict[str, Any], transport_kwargs: Mapping[str, Any], original_kwargs: Mapping[str, Any],
    *, deadline: Optional[float] = None,
) -> dict[str, Any]:
    result = dict(transport_kwargs)
    result.setdefault("options", options)
    if "timeout" in original_kwargs:
        result["timeout"] = original_kwargs["timeout"]
    if deadline is not None:
        result["options"] = legacy_deadline_options(result["options"], deadline)
        return legacy_deadline_kwargs(result, deadline)
    return result


def finish_read(
    offers: list[dict[str, Any]],
    client_connection: Any,
    response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]],
) -> ThroughputProperties:
    """Finish a nonempty lookup without allowing callback mutation of its result.

    :param list[dict] offers: Nonempty offer lookup result; the first record supplies throughput.
    :param Any client_connection: Connection supplying fallback headers for legacy results.
    :param callable or None response_hook: Callback receiving isolated headers and offer records.
    :return: Throughput settings isolated from callback mutations.
    :rtype: ~azure.cosmos.ThroughputProperties
    """
    headers = offer_response_headers(offers, client_connection)
    result = _deserialize_throughput(
        throughput=[CosmosDict(deepcopy(offers[0]), response_headers=headers)]
    )
    hook = with_response_header_snapshot(response_hook, copy_body=True)
    if hook is not None:
        hook(headers, offers)
    return result
