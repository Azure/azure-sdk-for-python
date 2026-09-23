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


def copy_connection_policy(policy: Optional[ConnectionPolicy]) -> ConnectionPolicy:
    """Copy the policy and the fields changed during client construction.

    For example, appending a preferred region to the copy does not change the
    original PreferredLocations list. Values nested inside the copied fields
    remain shared, as do unrelated objects such as custom transports.
    None creates a new ConnectionPolicy with default settings.
    """
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
    policy.PreferredLocations. Retry settings and connection_verify instead
    treat None as unspecified. Unchanged policy defaults are not copied into
    the keyword arguments.

    Connection timeouts are resolved separately by
    resolve_client_transport_timeouts, not by this function.
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
