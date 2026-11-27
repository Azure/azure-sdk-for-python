# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Prepare client configuration for the binding, without executing requests.

A customer app wants its orders client to prefer West US and allow two seconds
for an operation, including retries. Synchronous and asynchronous clients must interpret
those choices consistently. This module gives both Python wrappers one place to
check selected client-construction options and prepare settings they can retain.

The configuration follows this path::

    Customer app supplies preferred_locations=["West US"], timeout=2
        -> Python wrapper factory passes the relevant options to build_client_config
        -> builder returns checked PreparedClientConfig settings
        -> Python wrapper retains those settings
        -> binding later uses them when acquiring a driver handle

PreparedClientConfig is a read-only record, not a running client or a driver
handle. Its region sequences become tuples so later customer app edits to the
original lists cannot change the prepared settings. The builder returns None
when no configuration record is needed.

This module does not prepare the endpoint or credential, acquire a driver
handle, initialize CosmosDriverRuntime, or send requests to the service backend.
It prepares client-level settings, not the options for an individual order read.

Connection settings instead belong to ConnectionPoolOptions on a CosmosRuntime
passed to the client with runtime=. Rust-backed clients reject connection_timeout
as a client keyword.

During Python wrapper construction, the binding rejects retired client-level
network fields in the prepared configuration. It does not initialize a runtime,
reserve settings, or compare them with an existing runtime. The same rejection
also runs when driver acquisition converts the prepared configuration.
"""
from __future__ import annotations

import math
import os
from collections.abc import Mapping
from dataclasses import fields
from numbers import Real
from typing import Any, Optional, Sequence, Tuple

from .._availability_strategy_config import (
    CrossRegionHedgingStrategy, DEFAULT_THRESHOLD_MS, reject_rust_threshold_steps,
)
from ..documents import ConsistencyLevel
from .constants import FAULT_INJECTION_ENV_VAR
from .contracts import PreparedClientConfig, PreparedFaultInjectionRule
from ._immutable import freeze_headers
from .request_settings import reject_trigger_header

# Python names are preserved here; the binding maps them to read strategies.
_ALL_CONSISTENCY_LEVELS = (
    ConsistencyLevel.Strong,
    ConsistencyLevel.BoundedStaleness,
    ConsistencyLevel.Session,
    ConsistencyLevel.Eventual,
    ConsistencyLevel.ConsistentPrefix,
)

_RUST_FAULT_OPERATION_TYPES = frozenset(
    (
        "All",
        "ReadItem",
        "QueryItem",
        "CreateItem",
        "UpsertItem",
        "ReplaceItem",
        "DeleteItem",
        "PatchItem",
        "BatchItem",
        "ChangeFeedItem",
        "MetadataReadContainer",
        "MetadataReadDatabaseAccount",
        "MetadataQueryPlan",
        "MetadataPartitionKeyRanges",
    )
)
_RUST_FAULT_RULE_FIELDS = frozenset(field.name for field in fields(PreparedFaultInjectionRule))


def _normalize_locations(
    value: Optional[Sequence[str]], arg_name: str
) -> Tuple[str, ...]:
    """Copy a sequence of nonblank region names to a tuple.

    Require ["West US"], not "West US": converting the latter directly to a
    tuple would treat each character as a region. None or an empty sequence
    supplies no preferred or excluded regions.

    Preserve order and spelling, including surrounding whitespace on nonblank
    names. Region names are later matched without regard to case or spaces, so
    "West US" and "westus" select the same region. This checks the input shape,
    not whether a region exists in the account. Invalid sequences or
    blank/non-string entries raise ValueError.

    :param value: Region-name sequence to snapshot, or None.
    :type value: typing.Sequence[str] or None
    :param arg_name: Caller option name included in validation failures.
    :type arg_name: str
    :return: Tuple of validated region names in their supplied order.
    :rtype: tuple[str, ...]
    """
    if value is None:
        return ()
    if isinstance(value, (str, bytes)):
        raise ValueError(
            "{name} must be a list of region names, such as ['West US'], "
            "not a single string; got {val!r}.".format(name=arg_name, val=value)
        )
    if not isinstance(value, Sequence):
        raise ValueError("{} must be a list of region names.".format(arg_name))
    if any(not isinstance(region, str) or not region.strip() for region in value):
        raise ValueError("{} must contain non-empty region-name strings.".format(arg_name))
    return tuple(value)


def build_client_config(
    preferred_locations: Optional[Sequence[str]] = None,
    *,
    excluded_locations: Optional[Sequence[str]] = None,
    throttling_max_retry_count: Optional[int] = None,
    throttling_max_retry_wait_time_seconds: Optional[float] = None,
    availability_strategy: Any = None,
    user_agent_suffix: Optional[str] = None,
    consistency_level: Optional[str] = None,
    utf8_decoding_mode: Optional[str] = None,
    operation_timeout_seconds: Optional[float] = None,
    fault_injection_rules: Optional[Sequence[Mapping[str, Any]]] = None,
    headers: Optional[Mapping[str, str]] = None,
) -> Optional[PreparedClientConfig]:
    """Build the prepared client settings retained by either Python wrapper.

    Preserve the difference between an explicit value and None. For example,
    throttling_max_retry_count=0 disables throttle retries; None uses the driver default.
    Region names become tuples, internal test rules become read-only records,
    and an empty User-Agent suffix becomes None.

    Preferred regions, retries, and the overall operation budget configure a
    CosmosDriver object. Network settings instead belong to the selected
    CosmosRuntime and are not carried in this record. Native validation still
    rejects retired fields supplied by old callers.

    Return None when all options leave nothing to carry in a configuration
    record. This does not mean every setting uses an unmodified driver default:
    an absent hedging threshold makes the binding select a disabled client
    strategy for sending additional requests while one is pending. Driver
    environment overrides still apply. Other unspecified options retain their
    applicable driver, account, or shared connection settings.

    :param preferred_locations: Ordered preferred region names, or None.
    :type preferred_locations: typing.Sequence[str] or None
    :keyword excluded_locations: Region names to exclude, or None.
    :paramtype excluded_locations: typing.Sequence[str] or None
    :keyword throttling_max_retry_count: Maximum throttle retries, or None for the driver default.
    :paramtype throttling_max_retry_count: int or None
    :keyword throttling_max_retry_wait_time_seconds: Ordinary throttle retry waiting threshold, or None.
    :paramtype throttling_max_retry_wait_time_seconds: float or None
    :keyword availability_strategy: Cross-region hedging configuration or enablement flag.
    :paramtype availability_strategy: typing.Any
    :keyword user_agent_suffix: Optional application label appended to the User-Agent.
    :paramtype user_agent_suffix: str or None
    :keyword consistency_level: Requested Python consistency name, or None for the account default.
    :paramtype consistency_level: str or None
    :keyword utf8_decoding_mode: Strict or Lossy response decoding, or None for the default.
    :paramtype utf8_decoding_mode: str or None
    :keyword operation_timeout_seconds: Default overall operation budget in seconds, or None.
    :paramtype operation_timeout_seconds: float or None
    :keyword fault_injection_rules: Internal test-only fault rule mappings, or None.
    :paramtype fault_injection_rules: typing.Sequence[typing.Mapping[str, typing.Any]] or None
    :keyword headers: Default application request headers to snapshot, or None.
    :paramtype headers: typing.Mapping[str, str] or None
    :return: Prepared configuration, or None when no options require a record.
    :rtype: ~azure.cosmos._backend.contracts.PreparedClientConfig or None
    """
    preferred = _normalize_locations(preferred_locations, "preferred_locations")
    if operation_timeout_seconds is not None:
        from .._helpers._request_settings import (
            is_supported_operation_timeout,  # pylint: disable=import-outside-toplevel
        )

        if not is_supported_operation_timeout(operation_timeout_seconds):
            raise ValueError("timeout must be finite, non-boolean seconds >= 1 and < 2**64.")
    excluded = _normalize_locations(excluded_locations, "excluded_locations")
    if throttling_max_retry_count is not None and (
        isinstance(throttling_max_retry_count, bool)
        or not isinstance(throttling_max_retry_count, int)
        or not 0 <= throttling_max_retry_count <= 2**32 - 1
    ):
        raise ValueError(
            "retry_throttle_total (or its retry_total alias) must be an integer between 0 and 2**32 - 1."
        )
    if throttling_max_retry_wait_time_seconds is not None and (
        isinstance(throttling_max_retry_wait_time_seconds, bool)
        or not isinstance(throttling_max_retry_wait_time_seconds, Real)
        or not 0 <= throttling_max_retry_wait_time_seconds < 2**64
        # Converting an integer to the binding's float can round it up to 2**64.
        or float(throttling_max_retry_wait_time_seconds) >= 2**64
    ):
        raise ValueError(
            "throttle_retry_wait_threshold_seconds (or its retry_backoff_max alias) "
            "must be finite nonnegative seconds below 2**64."
        )
    hedging_threshold_ms = _resolve_hedging(availability_strategy)
    # An empty label should not add anything to the User-Agent header.
    suffix = user_agent_suffix or None
    consistency = _resolve_consistency_level(consistency_level)
    prepared_fault_rules = _prepare_fault_injection_rules(fault_injection_rules)
    prepared_headers = freeze_headers(headers if headers is not None else {})
    for name in prepared_headers:
        reject_trigger_header(name)
    if (
        not preferred
        and not excluded
        and all(value is None for value in (
            throttling_max_retry_count,
            throttling_max_retry_wait_time_seconds,
            hedging_threshold_ms,
            suffix,
            consistency,
            utf8_decoding_mode,
            operation_timeout_seconds,
        ))
        and not prepared_fault_rules
        and not prepared_headers
    ):
        return None
    return PreparedClientConfig(
        preferred_locations=preferred,
        excluded_locations=excluded,
        throttling_max_retry_count=throttling_max_retry_count,
        throttling_max_retry_wait_time_seconds=throttling_max_retry_wait_time_seconds,
        hedging_threshold_ms=hedging_threshold_ms,
        user_agent_suffix=suffix,
        consistency_level=consistency,
        utf8_decoding_mode=utf8_decoding_mode,
        operation_timeout_seconds=operation_timeout_seconds,
        fault_injection_rules=prepared_fault_rules,
        headers=prepared_headers,
    )


def _prepare_fault_response(
    rule: Mapping[str, Any], index: int
) -> tuple[Optional[int], Optional[str], int, bytes, dict[str, str]]:
    """Validate the synthetic response or transport failure in one fault rule.

    :param rule: Fault-rule mapping whose response settings are being prepared.
    :type rule: typing.Mapping[str, typing.Any]
    :param index: Rule position used in validation errors.
    :type index: int
    :return: HTTP status, transport error type, sub-status, body, and normalized response headers.
    :rtype: tuple[typing.Optional[int], typing.Optional[str], int, bytes, dict[str, str]]
    """
    status_code = rule.get("status_code")
    error_type = rule.get("error_type")
    if error_type is not None and error_type not in (
        "ConnectionError", "ResponseTimeout", "ResponseTimeoutAfterService"
    ):
        raise ValueError(
            "fault rule error_type must be ConnectionError, ResponseTimeout, ResponseTimeoutAfterService, or None."
        )
    if error_type is not None and (status_code is not None or rule.get("sub_status", 0) != 0):
        raise ValueError("fault rule error_type cannot be combined with status_code or sub_status.")
    if error_type is None and (
        isinstance(status_code, bool)
        or not isinstance(status_code, int)
        or not 100 <= status_code <= 599
    ):
        raise ValueError(
            "_fault_injection_rules[{}].status_code must be an integer from 100 to 599.".format(index)
        )

    sub_status = rule.get("sub_status", 0)
    response_body = rule.get("response_body", b"")
    if not isinstance(response_body, bytes):
        raise ValueError("fault rule response_body must be immutable bytes.")
    if error_type is not None and response_body:
        raise ValueError("fault rule response_body requires status_code, not error_type.")
    response_headers = rule.get("response_headers", {})
    if not isinstance(response_headers, Mapping):
        raise ValueError("fault rule response_headers must be a mapping of strings to strings.")
    normalized_headers: dict[str, str] = {}
    for name, value in response_headers.items():
        if (
            # Exact strings exclude subclasses with behavior outside the native protocol.
            type(name) is not str or type(value) is not str or not name  # pylint: disable=unidiomatic-typecheck
            or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&'*+-.^_`|~"
                   for char in name)
            or any(ord(char) < 32 and char != "\t" or ord(char) == 127 for char in value)
        ):
            raise ValueError("fault rule response_headers must contain valid header names and string values.")
        name = name.lower()
        if name == "x-ms-substatus":
            raise ValueError("fault rule response_headers must use sub_status instead of x-ms-substatus.")
        if name in normalized_headers:
            raise ValueError("fault rule response_headers contains duplicate case-insensitive names.")
        normalized_headers[name] = value
    if error_type is not None and normalized_headers:
        raise ValueError("fault rule response_headers requires status_code, not error_type.")
    if (
        isinstance(sub_status, bool)
        or not isinstance(sub_status, int)
        or not 0 <= sub_status <= 65535
    ):
        raise ValueError(
            "_fault_injection_rules[{}].sub_status must be an integer from 0 to 65535.".format(index)
        )
    return status_code, error_type, sub_status, response_body, normalized_headers


def _prepare_fault_injection_rules(
    rules: Optional[Sequence[Mapping[str, Any]]],
) -> tuple[PreparedFaultInjectionRule, ...]:
    """Prepare internal test instructions for simulated request failures or delays.

    For example, a rule can select an order read and specify a failure status
    and a delay in milliseconds. This helper checks and copies that instruction;
    it does not send the read or inject the failure itself.
    ConnectionError and ResponseTimeout instead inject transport failures
    without fabricating an HTTP response or expiring the operation budget.
    ResponseTimeoutAfterService discards a successful service response; a write
    may already have committed. Its optional delay runs after that response.
    response_headers supplies synthetic HTTP headers, such as
    x-ms-retry-after-ms, rather than delaying the response itself. Header names
    are case-insensitive; use sub_status instead of an x-ms-substatus header.

    Reject unknown fields, duplicate rule IDs, unsupported operation types,
    and invalid field values. Operation types use Rust driver test-rule names
    such as "ReadItem", not Python wrapper operation names such as "read_item".
    The explicit "All" selector leaves the driver's operation filter unset.
    Other rule filters still apply. It can affect account initialization, so
    tests can start with enabled=False and enable their owned rule afterward.

    Return a tuple of read-only PreparedFaultInjectionRule records with omitted
    optional fields filled in. None produces no rules without requiring the switch.
    The supplied mappings are not modified or retained as mutable rule data.
    Any non-None input, including an empty sequence, raises TypeError unless
    the test-only COSMOS_ENABLE_FAULT_INJECTION switch is "1".
    A test-probes build is also required for any non-None input.
    With both enabled, an empty sequence produces no rules.

    :param rules: Internal fault-rule mappings, or None to leave fault injection disabled.
    :type rules: typing.Sequence[typing.Mapping[str, typing.Any]] or None
    :return: Validated immutable fault-rule records.
    :rtype: tuple[azure.cosmos._backend.contracts.PreparedFaultInjectionRule, ...]
    """
    if rules is None:
        return ()
    if os.environ.get(FAULT_INJECTION_ENV_VAR) != "1":
        raise TypeError(
            "_fault_injection_rules is a test-only option; set {}=1 to use it.".format(
                FAULT_INJECTION_ENV_VAR
            )
        )
    from .. import _rust

    if not callable(getattr(_rust, "_debug_fault_injection_rule_hit_count", None)):
        raise TypeError("_fault_injection_rules requires a wheel built with --features test-probes.")
    if isinstance(rules, (str, bytes, bytearray)) or not isinstance(rules, Sequence):
        raise ValueError("_fault_injection_rules must be a sequence of rule mappings.")

    prepared = []
    seen_ids = set()
    for index, rule in enumerate(rules):
        if not isinstance(rule, Mapping):
            raise ValueError(
                "_fault_injection_rules[{}] must be a mapping.".format(index)
            )
        unknown_fields = rule.keys() - _RUST_FAULT_RULE_FIELDS
        if unknown_fields:
            raise ValueError(
                "_fault_injection_rules[{}] contains unsupported fields: {}.".format(
                    index, ", ".join(sorted(repr(field) for field in unknown_fields))
                )
            )
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not rule_id:
            raise ValueError(
                "_fault_injection_rules[{}].id must be a non-empty string.".format(index)
            )
        if rule_id in seen_ids:
            raise ValueError("duplicate fault injection rule id: {!r}.".format(rule_id))
        seen_ids.add(rule_id)

        operation_type = rule.get("operation_type")
        if not isinstance(operation_type, str) or operation_type not in _RUST_FAULT_OPERATION_TYPES:
            raise ValueError(
                "_fault_injection_rules[{}].operation_type must be one of {}; got {!r}.".format(
                    index, sorted(_RUST_FAULT_OPERATION_TYPES), operation_type
                )
            )

        status_code, error_type, sub_status, response_body, normalized_headers = _prepare_fault_response(rule, index)

        delay_ms = rule.get("delay_ms", 0)
        if (
            isinstance(delay_ms, bool)
            or not isinstance(delay_ms, int)
            or not 0 <= delay_ms <= 2**64 - 1
        ):
            raise ValueError(
                "_fault_injection_rules[{}].delay_ms must be an integer from 0 to 2**64 - 1.".format(
                    index
                )
            )

        probability = rule.get("probability", 1.0)
        if (
            isinstance(probability, bool)
            or not isinstance(probability, Real)
            or probability < 0.0
            or not probability <= 1.0
            or not math.isfinite(float(probability))
        ):
            raise ValueError(
                "_fault_injection_rules[{}].probability must be between 0.0 and 1.0.".format(
                    index
                )
            )

        hit_limit = rule.get("hit_limit")
        if (
            hit_limit is not None
            and (
                isinstance(hit_limit, bool)
                or not isinstance(hit_limit, int)
                or not 0 <= hit_limit <= 2**32 - 1
            )
        ):
            raise ValueError(
                "_fault_injection_rules[{}].hit_limit must be an integer from 0 to 2**32 - 1 or None.".format(
                    index
                )
            )

        enabled = rule.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError(
                "_fault_injection_rules[{}].enabled must be a bool.".format(index)
            )

        container_id = rule.get("container_id")
        if container_id is not None and (
            not isinstance(container_id, str) or not container_id
        ):
            raise ValueError(
                "_fault_injection_rules[{}].container_id must be a non-empty string or None.".format(
                    index
                )
            )
        region = rule.get("region")
        if region is not None and (not isinstance(region, str) or not region):
            raise ValueError(
                "_fault_injection_rules[{}].region must be a non-empty string or None.".format(
                    index
                )
            )

        prepared.append(
            PreparedFaultInjectionRule(
                id=rule_id,
                operation_type=operation_type,
                status_code=status_code,
                sub_status=sub_status,
                container_id=container_id,
                region=region,
                delay_ms=delay_ms,
                probability=float(probability),
                hit_limit=hit_limit,
                enabled=enabled,
                error_type=error_type,
                response_body=response_body,
                response_headers=normalized_headers,
            )
        )
    return tuple(prepared)


def _resolve_consistency_level(consistency_level: Optional[str]) -> Optional[str]:
    """Validate a Python consistency name for the binding's read strategy.

    The binding maps ConsistentPrefix to Eventual, BoundedStaleness to
    LatestCommitted, and Strong to GlobalStrong. Eventual and Session map
    directly. These read choices do not change account settings or writes.
    An absent or empty value leaves the account default unchanged.

    :param consistency_level: Python consistency name, or None.
    :type consistency_level: str or None
    :return: Validated name, or None for absent or empty input.
    :rtype: str or None
    """
    if not consistency_level:
        return None
    if consistency_level in _ALL_CONSISTENCY_LEVELS:
        return consistency_level
    raise ValueError(
        "consistency_level {!r} is not a recognized Cosmos consistency level; "
        "expected one of {}.".format(
            consistency_level, ", ".join(_ALL_CONSISTENCY_LEVELS)
        )
    )


def _resolve_hedging(availability_strategy: Any) -> Optional[int]:
    """Prepare the initial cross-region hedging delay in milliseconds.

    Sending another request while the first is still pending is called hedging.
    For an eligible order read, a threshold of 20 means another region may be
    tried after 20 milliseconds; it is not a promised completion time.
    This helper returns the threshold, not a running request or a timer.

    True uses DEFAULT_THRESHOLD_MS. A dictionary is checked by the existing
    CrossRegionHedgingStrategy validator and supplies threshold_ms.

    Other values, including None, False and unrecognized inputs, return None.
    When preparing client settings, the binding uses that absence to select a
    disabled client strategy, subject to driver environment overrides.
    Explicit threshold_steps_ms is rejected: the Rust driver does not support
    progressively adding more regions.

    :param availability_strategy: Hedging configuration, enablement flag, or another value.
    :type availability_strategy: typing.Any
    :return: Initial hedging threshold in milliseconds, or None when disabled or unrecognized.
    :rtype: int or None
    """
    reject_rust_threshold_steps(availability_strategy)
    if availability_strategy is True:
        return DEFAULT_THRESHOLD_MS
    if isinstance(availability_strategy, dict):
        # Reuse the existing validator so an invalid threshold_ms raises the same
        # ValueError it would on the legacy path.
        return CrossRegionHedgingStrategy(availability_strategy).threshold_ms
    # None, False, or an unrecognized input supplies no threshold.
    return None
