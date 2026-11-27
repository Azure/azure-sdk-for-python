# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Public item argument rules, operation budgets and patch-body snapshots."""

from __future__ import annotations

import time
from typing import Any, Mapping, Optional

from ._request_settings import (
    COMMON_OPTIONS, OPTION_HEADER_NAMES, build_customer_headers,
    get_match_headers, is_supported_operation_timeout, reject_unsupported_feed_options,
)
from ._response_parse import validate_response_hook_is_synchronous
from ._wire_encoding import serialize_body_to_bytes


_CREATE_ITEM_OPTIONS = frozenset({
    "partitionKey", "indexingDirective", "sessionToken", "initialHeaders",
    "priorityLevel", "responsePayloadOnWriteDisabled", "throughputBucket",
    "excludedLocations", "timeout", "contentType", "utf8DecodingMode",
    "consistencyLevel", "correlatedActivityId", "retry_write", "availabilityStrategy",
})
_CREATE_ITEM_KWARGS = frozenset({
    "container_link", "body", "indexing_directive", "enable_automatic_id_generation",
    "request_options", "feed_options", "timeout", "connection_timeout", "response_hook",
    "tracing_options", "tracing_attributes", "logger", "logging_enable",
}) | frozenset(name for name, option in COMMON_OPTIONS.items() if option in _CREATE_ITEM_OPTIONS)
_CREATE_ITEM_UNSUPPORTED_HEADERS = frozenset({
    "if-match", "if-none-match",
}) | frozenset(header for option, header in OPTION_HEADER_NAMES.items() if option not in _CREATE_ITEM_OPTIONS)


def validate_create_item_arguments(arguments: Mapping[str, Any]) -> None:
    """Check create's option names before shared normalization consumes them.

    Value checks still apply to accepted names: retry_write permits only None,
    for example. Only the selected option mapping is used, preserving
    request_options precedence over feed_options.

    :param Mapping[str, Any] arguments: Create arguments, including request option mappings.
    :return: None. Unsupported arguments raise TypeError before request preparation.
    :rtype: None
    """
    reject_unsupported_feed_options("create_item", arguments.keys() - _CREATE_ITEM_KWARGS, {})
    options = dict(arguments.get("request_options", arguments.get("feed_options")) or {})
    unsupported = set()
    for name in options:
        if not isinstance(name, str):
            raise TypeError("create_item() request option names must be strings.")
        if name in _CREATE_ITEM_OPTIONS:
            continue
        if name.lower() not in _CREATE_ITEM_UNSUPPORTED_HEADERS and (
            name.lower().startswith("x-ms-") or name.lower() == "prefer"
        ):
            continue
        unsupported.add(name)
    reject_unsupported_feed_options("create_item", unsupported, {})
    for headers in (arguments.get("initial_headers"), options.get("initialHeaders")):
        for name in build_customer_headers(headers):
            if name in _CREATE_ITEM_UNSUPPORTED_HEADERS:
                raise TypeError(f"create_item() does not support initial_headers option '{name}'.")


def prepare_item_deadline(
    kwargs: dict[str, Any], method: str, started: float
) -> Optional[float]:
    """Copy request options and return this call's deadline, or None if unset.

    :param dict[str, Any] kwargs: Working keywords updated with copied options and normalized timeout.
    :param str method: Operation name used in timeout errors.
    :param float started: Monotonic operation start time in seconds.
    :return: The monotonic deadline, or None when no timeout is configured.
    :rtype: float or None
    """
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


def prepare_create_item_kwargs(
    kwargs: dict[str, Any], *, response_hook: Any = None
) -> Optional[float]:
    """Reject retired arguments by presence and establish the create budget.

    :param dict[str, Any] kwargs: Working creation keywords updated with isolated request options.
    :keyword callable or None response_hook: Callback to validate as synchronous before dispatch.
    :return: The monotonic creation deadline, or None without a timeout.
    :rtype: float or None
    """
    for name in ("populate_query_metrics", "etag", "match_condition"):
        if name in kwargs:
            raise TypeError(f"create_item() does not accept '{name}'.")
    if response_hook is not None and not callable(response_hook):
        raise TypeError("create_item response_hook must be callable.")
    validate_response_hook_is_synchronous(response_hook, "create_item")
    if "request_options" not in kwargs:
        kwargs["request_options"] = kwargs.get("feed_options")
    return prepare_item_deadline(kwargs, "create_item", time.monotonic())


def prepare_replace_item_kwargs(kwargs: dict[str, Any]) -> None:
    """Carry one replacement budget through preparation, metadata, and the write.

    :param dict[str, Any] kwargs: Working replacement keywords receiving a deadline unless already present.
    :return: None.
    :rtype: None
    """
    if "_item_operation_deadline" not in kwargs:
        if "request_options" not in kwargs:
            kwargs["request_options"] = kwargs.get("feed_options")
        deadline = prepare_item_deadline(kwargs, "replace_item", time.monotonic())
        if deadline is not None:
            kwargs["_item_operation_deadline"] = deadline


def prepare_item_target(kwargs: dict[str, Any], item: Any) -> None:
    """Retain mapping validation without building a legacy document address.

    :param dict[str, Any] kwargs: Working keywords receiving the target's resource address when applicable.
    :param str or Mapping[str, Any] item: Item ID or properties containing its ``_self`` address.
    :return: None.
    :rtype: None
    """
    if "document_link" in kwargs or "_item_self_link" in kwargs:
        raise TypeError("Item addressing must be supplied through the item argument.")
    if not isinstance(item, str):
        kwargs["_item_self_link"] = item["_self"]


def prepare_read_item_kwargs(
    kwargs: dict[str, Any], partition_key: Any, *, response_hook: Any = None
) -> Optional[float]:
    """Validate before metadata I/O and isolate the caller's option mapping.

    :param dict[str, Any] kwargs: Working read keywords updated with conditions, options, and deadline.
    :param Any partition_key: Public partition key stored in the read options.
    :keyword callable or None response_hook: Callback checked for callability.
    :return: The monotonic read deadline, or None without a timeout.
    :rtype: float or None
    """
    if "populate_query_metrics" in kwargs:
        raise TypeError("read_item() does not accept 'populate_query_metrics'.")
    if response_hook is not None and not callable(response_hook):
        raise TypeError("read_item response_hook must be callable.")
    if "request_options" not in kwargs:
        kwargs["request_options"] = kwargs.get("feed_options")
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


def build_patch_operations_payload(
    patch_operations: Any, *, filter_predicate: Optional[str] = None
) -> dict[str, Any]:
    """Build the patch body dictionary, converting increment to the service's incr.

    :param list[dict] patch_operations: Nonempty sequence of patch operation dictionaries.
    :keyword str or None filter_predicate: SQL condition guarding the patch.
    :return: Body containing translated operations and an optional condition.
    :rtype: dict[str, Any]
    """
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
    payload: dict[str, Any] = {"operations": translated}
    if filter_predicate is not None:
        if not isinstance(filter_predicate, str):
            raise TypeError("patch_item filter_predicate must be a string.")
        payload["condition"] = filter_predicate
    return payload


def serialize_patch_body(
    patch_operations: Any, *, compact_utf8: bool = False,
    filter_predicate: Optional[str] = None,
) -> bytes:
    """Create body bytes before execution can give control back to the customer app.

    :param list[dict] patch_operations: Nonempty sequence of patch operation dictionaries.
    :keyword bool compact_utf8: Whether to encode non-ASCII characters directly as UTF-8.
    :keyword str or None filter_predicate: SQL condition guarding the patch.
    :return: UTF-8 JSON patch payload with non-finite numbers rejected.
    :rtype: bytes
    """
    return serialize_body_to_bytes(
        build_patch_operations_payload(patch_operations, filter_predicate=filter_predicate),
        ensure_ascii=not compact_utf8,
        allow_nan=False,
    )


def prepare_patch_item_kwargs(kwargs: dict[str, Any]) -> None:
    """Normalize caller guards and establish one operation budget.

    :param dict[str, Any] kwargs: Working patch keywords updated with If-Match and an operation deadline.
    :return: None.
    :rtype: None
    """
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
    """Reject unsupported guards and ambiguous header overrides before I/O.

    :param dict[str, Any] options: Working options updated with a single validated If-Match condition.
    :return: None.
    :rtype: None
    """
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
