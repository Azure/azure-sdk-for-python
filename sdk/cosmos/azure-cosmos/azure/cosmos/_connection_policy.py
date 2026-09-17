# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Shared connection-policy normalization for the sync and async clients."""
from __future__ import annotations

from copy import copy
from typing import Any, Mapping, Optional

from .documents import ConnectionPolicy


def copy_connection_policy(policy: Optional[ConnectionPolicy]) -> ConnectionPolicy:
    """Copy the mutable settings builders modify, without copying custom transports."""
    if policy is None:
        return ConnectionPolicy()
    if not isinstance(policy, ConnectionPolicy):
        raise TypeError("connection_policy must be a ConnectionPolicy object or None.")
    result = copy(policy)
    result.PreferredLocations = copy(policy.PreferredLocations)
    result.ExcludedLocations = copy(policy.ExcludedLocations)
    result.RetryOptions = copy(policy.RetryOptions)
    result.SSLConfiguration = copy(policy.SSLConfiguration)
    result.ProxyConfiguration = copy(policy.ProxyConfiguration)
    return result


def resolve_retry_option(
    kwargs: Mapping[str, Any], throttle_keyword: str, generic_keyword: str, default: Any
) -> Any:
    """Throttle-specific keywords win over generic keywords; zero is explicit."""
    value = kwargs.get(throttle_keyword)
    if value is None:
        value = kwargs.get(generic_keyword)
    return default if value is None else value


def resolve_connection_policy_kwargs(kwargs: Mapping[str, Any]) -> dict[str, Any]:
    """Expose supported policy settings to both backend and legacy preparation.

    Explicit keywords override grouped values. Unchanged policy defaults are not
    promoted into explicit Rust configuration, especially process-wide timeouts.
    Timeouts continue to use resolve_client_transport_timeouts.
    """
    resolved = dict(kwargs)
    stock = ConnectionPolicy()
    policy = kwargs.get("connection_policy")
    if policy is None:
        policy = stock
    elif not isinstance(policy, ConnectionPolicy):
        raise TypeError("connection_policy must be a ConnectionPolicy object or None.")

    for keyword, attribute in (
        ("preferred_locations", "PreferredLocations"),
        ("excluded_locations", "ExcludedLocations"),
        ("proxy_config", "ProxyConfiguration"),
        ("ssl_config", "SSLConfiguration"),
    ):
        value = getattr(policy, attribute)
        if keyword not in resolved and value != getattr(stock, attribute):
            resolved[keyword] = value

    if resolved.get("connection_verify") is None and policy.DisableSSLVerification:
        resolved["connection_verify"] = False

    for throttle_keyword, generic_keyword, attribute in (
        ("retry_throttle_total", "retry_total", "MaxRetryAttemptCount"),
        ("retry_throttle_backoff_max", "retry_backoff_max", "MaxWaitTimeInSeconds"),
    ):
        policy_value = getattr(policy.RetryOptions, attribute)
        default = None if policy_value == getattr(stock.RetryOptions, attribute) else policy_value
        value = resolve_retry_option(kwargs, throttle_keyword, generic_keyword, default)
        if value is not None:
            resolved[throttle_keyword] = value
    return resolved
