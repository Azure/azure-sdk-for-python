# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Collect client options in one object for the Rust binding.

For example, a customer app may prefer West US and limit retries after the
service asks it to slow down. build_client_config checks those options and
returns a PreparedClientConfig shared by the sync and async setup code.
It returns None when no settings need to be passed.

Python validates the fields handled below; the binding performs further
checks when acquiring a driver. Those checks include the User-Agent label
and agreement with network settings already chosen for the process.
"""
from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import fields
from numbers import Real
from typing import Any, Optional, Sequence, Tuple

from .._availability_strategy_config import CrossRegionHedgingStrategy, DEFAULT_THRESHOLD_MS
from ..documents import ConsistencyLevel
from .contracts import PreparedClientConfig, PreparedFaultInjectionRule

# Levels this binding supports. Strong maps to the driver's GlobalStrong;
# other recognized Cosmos levels are rejected rather than ignored.
_RUST_SUPPORTED_CONSISTENCY_LEVELS = (
    ConsistencyLevel.Eventual,
    ConsistencyLevel.Session,
    ConsistencyLevel.Strong,
)

# Distinguish an unsupported Cosmos level from an unrecognized name.
_ALL_CONSISTENCY_LEVELS = (
    ConsistencyLevel.Strong,
    ConsistencyLevel.BoundedStaleness,
    ConsistencyLevel.Session,
    ConsistencyLevel.Eventual,
    ConsistencyLevel.ConsistentPrefix,
)

_RUST_FAULT_OPERATION_TYPES = frozenset(
    (
        "ReadItem",
        "QueryItem",
        "CreateItem",
        "UpsertItem",
        "ReplaceItem",
        "DeleteItem",
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
    """
    if value is None:
        return ()
    if isinstance(value, (str, bytes)):
        raise ValueError(
            "{name} must be a sequence of region-name strings (e.g. ['West US']), "
            "not a bare string; got {val!r}. A bare string is read one character "
            "at a time, which is never what you want here.".format(
                name=arg_name, val=value
            )
        )
    if not isinstance(value, Sequence):
        raise ValueError("{} must be a sequence of region-name strings.".format(arg_name))
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
    proxy_allowed: Optional[bool] = None,
    connection_timeout_seconds: Optional[float] = None,
    read_timeout_seconds: Optional[float] = None,
    fault_injection_rules: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Optional[PreparedClientConfig]:
    """Validate and collect client settings, or return None if none are needed.

    Preserve the difference between an explicit value and None. For example,
    proxy_allowed=False requires a direct connection; None requests no override.
    Region names become tuples, and an empty User-Agent suffix becomes None.

    Network settings apply to the shared Rust runtime. In particular, Rust
    uses read_timeout to limit a whole HTTP attempt, not just pauses while
    reading a response. This builder does not create that runtime or reserve
    its settings.

    Without an availability_strategy threshold, the binding disables sending
    additional requests to other regions while a request is still pending.
    Other unspecified options keep their driver or account defaults.
    """
    if proxy_allowed is not None and not isinstance(proxy_allowed, bool):
        raise ValueError(
            "proxy_allowed must be a bool when provided; got {!r}.".format(
                type(proxy_allowed).__name__
            )
        )
    preferred = _normalize_locations(preferred_locations, "preferred_locations")
    excluded = _normalize_locations(excluded_locations, "excluded_locations")
    if throttling_max_retry_count is not None and (
        isinstance(throttling_max_retry_count, bool)
        or not isinstance(throttling_max_retry_count, int)
        or not 0 <= throttling_max_retry_count <= 2**32 - 1
    ):
        raise ValueError("retry_throttle_total must be an integer between 0 and 2**32 - 1.")
    if throttling_max_retry_wait_time_seconds is not None and (
        isinstance(throttling_max_retry_wait_time_seconds, bool)
        or not isinstance(throttling_max_retry_wait_time_seconds, Real)
        or not 0 <= throttling_max_retry_wait_time_seconds < 2**64
        # Converting an integer to the binding's float can round it up to 2**64.
        or float(throttling_max_retry_wait_time_seconds) >= 2**64
    ):
        raise ValueError("retry_throttle_backoff_max must be finite nonnegative seconds below 2**64.")
    hedging_threshold_ms = _resolve_hedging(availability_strategy)
    # An empty label should not add anything to the User-Agent header.
    suffix = user_agent_suffix or None
    consistency = _resolve_consistency_level(consistency_level)
    connection_timeout = _normalize_transport_timeout(
        connection_timeout_seconds,
        "connection_timeout",
        maximum=6.0,
    )
    read_timeout = _normalize_transport_timeout(
        read_timeout_seconds,
        "read_timeout",
    )
    prepared_fault_rules = _prepare_fault_injection_rules(fault_injection_rules)
    if (
        not preferred
        and not excluded
        and throttling_max_retry_count is None
        and throttling_max_retry_wait_time_seconds is None
        and hedging_threshold_ms is None
        and suffix is None
        and consistency is None
        and proxy_allowed is None
        and connection_timeout is None
        and read_timeout is None
        and not prepared_fault_rules
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
        proxy_allowed=proxy_allowed,
        connection_timeout_seconds=connection_timeout,
        read_timeout_seconds=read_timeout,
        fault_injection_rules=prepared_fault_rules,
    )


def _prepare_fault_injection_rules(
    rules: Optional[Sequence[Mapping[str, Any]]],
) -> tuple[PreparedFaultInjectionRule, ...]:
    """Check internal test rules that make selected requests fail or wait."""
    if rules is None:
        return ()
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

        status_code = rule.get("status_code")
        if (
            isinstance(status_code, bool)
            or not isinstance(status_code, int)
            or not 100 <= status_code <= 599
        ):
            raise ValueError(
                "_fault_injection_rules[{}].status_code must be an integer from 100 to 599.".format(
                    index
                )
            )

        sub_status = rule.get("sub_status", 0)
        if (
            isinstance(sub_status, bool)
            or not isinstance(sub_status, int)
            or not 0 <= sub_status <= 65535
        ):
            raise ValueError(
                "_fault_injection_rules[{}].sub_status must be an integer from 0 to 65535.".format(
                    index
                )
            )

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
            or not 0.0 <= probability <= 1.0
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
            )
        )
    return tuple(prepared)


def _normalize_transport_timeout(
    value: Optional[float],
    name: str,
    *,
    maximum: Optional[float] = None,
) -> Optional[float]:
    """Check that a timeout is finite and within the allowed range of seconds."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError("{} must be a number of seconds; got {!r}.".format(name, value))
    timeout = float(value)
    if not math.isfinite(timeout):
        raise ValueError("{} must be finite; got {!r}.".format(name, value))
    if timeout < 0.1:
        raise ValueError(
            "{} must be at least 0.1 seconds on the Rust backend; got {!r}.".format(
                name, value
            )
        )
    if maximum is not None and timeout > maximum:
        raise ValueError(
            "{} must be at most {} seconds on the Rust backend; got {!r}.".format(
                name, maximum, value
            )
        )
    return timeout


def _resolve_consistency_level(consistency_level: Optional[str]) -> Optional[str]:
    """Reject consistency choices the binding cannot honor rather than ignore them.

    Eventual, Session, and Strong are passed to the binding; Strong maps to the
    driver's GlobalStrong. BoundedStaleness and ConsistentPrefix are rejected,
    as are unrecognized nonempty names. An absent or empty value leaves the
    account default unchanged.
    """
    if not consistency_level:
        return None
    if consistency_level in _RUST_SUPPORTED_CONSISTENCY_LEVELS:
        return consistency_level
    if consistency_level in _ALL_CONSISTENCY_LEVELS:
        raise ValueError(
            "consistency_level {!r} is not yet supported by the Rust binding; "
            "supported levels are {}. Use the core-python "
            "backend if you need {!r}.".format(
                consistency_level,
                ", ".join(_RUST_SUPPORTED_CONSISTENCY_LEVELS),
                consistency_level,
            )
        )
    raise ValueError(
        "consistency_level {!r} is not a recognized Cosmos consistency level; "
        "expected one of {}.".format(
            consistency_level, ", ".join(_ALL_CONSISTENCY_LEVELS)
        )
    )


def _resolve_hedging(availability_strategy: Any) -> Optional[int]:
    """Return the delay before another region may receive a pending request.

    Sending another request while the first is still pending is called hedging.
    True uses DEFAULT_THRESHOLD_MS. A dictionary is checked by the existing
    CrossRegionHedgingStrategy validator and supplies threshold_ms.

    Other values return None, which the binding uses to disable hedging.
    threshold_steps_ms is not passed: the driver uses only one threshold.
    """
    if availability_strategy is True:
        return DEFAULT_THRESHOLD_MS
    if isinstance(availability_strategy, dict):
        # Reuse the existing validator so an invalid threshold_ms raises the same
        # ValueError it would on the legacy path.
        return CrossRegionHedgingStrategy(availability_strategy).threshold_ms
    # None, False, or an unrecognized input supplies no threshold.
    return None
