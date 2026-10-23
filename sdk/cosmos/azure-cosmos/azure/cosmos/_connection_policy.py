# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Share connection-policy preparation between synchronous and async clients.

A customer app can reuse one ConnectionPolicy for several clients. Copy the
settings that client construction changes so creating one client does not
change the policy supplied to another. Resolve supported fields into client
keyword arguments without turning every default into an explicit setting.
"""
from __future__ import annotations

from copy import copy
from typing import Any, Mapping, Optional

from .documents import ConnectionPolicy
from ._backend.capabilities import reject_removed_options


def reject_rust_connection_policy_options(kwargs: Mapping[str, Any]) -> None:
    """Reject client retry and routing controls that Rust cannot honor."""
    for keyword in ("retry_connect", "retry_read"):
        if keyword in kwargs:
            raise TypeError(
                f"{keyword} is not supported by Rust-backed clients; omit this keyword. "
                "The Rust driver does not expose an equivalent connection/read retry-count control."
            )
    policy = kwargs.get("connection_policy")
    if "retry_fixed_interval" in kwargs or (
        policy is not None and policy.RetryOptions.FixedRetryIntervalInMilliseconds is not None
    ):
        raise TypeError(
            "Fixed throttle retry intervals are not supported by Rust-backed clients; "
            "omit retry_fixed_interval and leave "
            "connection_policy.RetryOptions.FixedRetryIntervalInMilliseconds unset."
        )
    for keyword, attribute in (
        ("enable_endpoint_discovery", "EnableEndpointDiscovery"),
        ("multiple_write_locations", "UseMultipleWriteLocations"),
    ):
        if keyword in kwargs:
            raise TypeError(
                f"{keyword} is not supported by Rust-backed clients; "
                "the Rust driver manages endpoint discovery and routing from account settings."
            )
        if policy is not None and (
            attribute in vars(policy)
            or any(
                attribute in cls.__dict__
                for cls in type(policy).__mro__
                if cls is not ConnectionPolicy
            )
        ):
            raise TypeError(
                f"connection_policy.{attribute} is not supported by Rust-backed clients; "
                "leave this field unset and let the Rust driver manage routing."
            )


def copy_connection_policy(policy: Optional[ConnectionPolicy]) -> ConnectionPolicy:
    """Copy the policy and the fields changed during client construction.

    For example, appending a preferred region to the copy does not change the
    original PreferredLocations list. Values nested inside the copied fields
    remain shared.
    None creates a new ConnectionPolicy with default settings.
    """
    if policy is None:
        return ConnectionPolicy()
    if not isinstance(policy, ConnectionPolicy):
        raise TypeError("connection_policy must be a ConnectionPolicy object or None.")
    reject_removed_options({"connection_policy": policy})
    result = copy(policy)
    result.PreferredLocations = copy(policy.PreferredLocations)
    result.ExcludedLocations = copy(policy.ExcludedLocations)
    result.RetryOptions = copy(policy.RetryOptions)
    return result


def resolve_retry_option(
    kwargs: Mapping[str, Any], throttle_keyword: str, generic_keyword: str, default: Any
) -> Any:
    """Choose the throttle setting, then the generic retry setting, then the default.

    Only None means unspecified. For example, retry_throttle_total=0 wins over
    retry_total=9; zero must not be replaced with a default retry count.
    """
    value = kwargs.get(throttle_keyword)
    if value is None:
        value = kwargs.get(generic_keyword)
    return default if value is None else value


def resolve_connection_policy_kwargs(kwargs: Mapping[str, Any]) -> dict[str, Any]:
    """Combine client keywords with supported ConnectionPolicy fields.

    For example, a supplied preferred_locations entry takes precedence over
    policy.PreferredLocations. Retry settings instead
    treat None as unspecified. Unchanged policy defaults are not copied into
    the keyword arguments.

    Connection timeouts are resolved separately by
    resolve_client_connection_timeout, not by this function.
    """
    reject_removed_options(kwargs)
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
    ):
        value = getattr(policy, attribute)
        if keyword not in resolved and value != getattr(stock, attribute):
            resolved[keyword] = value

    for throttle_keyword, generic_keyword, attribute in (
        ("retry_throttle_total", "retry_total", "MaxRetryAttemptCount"),
        ("throttle_retry_wait_threshold_seconds", "retry_backoff_max", "MaxWaitTimeInSeconds"),
    ):
        policy_value = getattr(policy.RetryOptions, attribute)
        default = None if policy_value == getattr(stock.RetryOptions, attribute) else policy_value
        value = resolve_retry_option(kwargs, throttle_keyword, generic_keyword, default)
        if value is not None:
            resolved[throttle_keyword] = value
    return resolved
