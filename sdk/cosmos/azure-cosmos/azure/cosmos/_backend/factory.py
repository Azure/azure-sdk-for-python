# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Construct RustBackend or AsyncRustBackend with prepared client settings.

The Rust path is the only release execution path. This checkout retains private
controls for comparing it with the legacy path: _backend takes precedence over
COSMOS_BACKEND, and the current unset value still uses core-python. That
temporary default and those controls must be removed before release; they
are not customer configuration.

This Python wrapper validates settings and prepares the credential before
creating RustBackend or AsyncRustBackend. These are Python classes that call
the binding. On first use, they acquire a driver handle through the binding.
If construction fails, release any async credential bridge acquired here.
"""
from __future__ import annotations

import os
from typing import Any, Callable, Optional, Sequence, TypeVar, Union

from .cosmos_backend import CosmosBackend
from .client_config import build_client_config
from .constants import (
    BACKEND_ENV_VAR,
    BACKEND_NAME_RUST,
    DEFAULT_BACKEND_NAME,
    VALID_BACKEND_NAMES,
)
from .credentials import resolved_credential
from .legacy import LEGACY_BACKEND
from .rust_backend import RustBackend
from .transport_settings import reject_unsupported_transport_settings

_BackendT = TypeVar("_BackendT")
_LegacyBackendT = TypeVar("_LegacyBackendT")

def resolve_backend_name(explicit: Optional[str]) -> str:
    """Read the temporary migration/test control and reject unknown values.

    Read the environment only when explicit is None. Strip surrounding spaces
    and ignore case, so " RUST " selects rust. A blank value selects the default,
    even if it was an explicit argument. Other unknown names or non-string
    arguments raise ValueError rather than silently running different code.
    This function does not define a customer-facing execution-path choice.
    """
    raw = explicit if explicit is not None else os.environ.get(BACKEND_ENV_VAR)
    if raw is not None and not isinstance(raw, str):
        # Reject a non-string argument before strip() raises an unrelated error.
        raise ValueError(
            "Invalid backend {!r}. Expected one of {} as a string. "
            "Set the constructor kwarg _backend=, or the {} environment variable.".format(
                raw, VALID_BACKEND_NAMES, BACKEND_ENV_VAR
            )
        )
    choice = raw.strip().lower() if raw is not None else ""
    if not choice:
        return DEFAULT_BACKEND_NAME
    if choice not in VALID_BACKEND_NAMES:
        raise ValueError(
            "Invalid backend {!r}. Expected one of {}. "
            "Set the constructor kwarg _backend=, or the {} environment variable.".format(
                raw, VALID_BACKEND_NAMES, BACKEND_ENV_VAR
            )
        )
    return choice


def _make_backend(
    explicit: Optional[str],
    *,
    rust_backend_type: Callable[..., _BackendT],
    legacy_backend: _LegacyBackendT,
    url: Optional[str] = None,
    credential: Any = None,
    preferred_locations: Optional[Sequence[str]] = None,
    excluded_locations: Optional[Sequence[str]] = None,
    throttling_max_retry_count: Optional[int] = None,
    throttling_max_retry_wait_time_seconds: Optional[float] = None,
    availability_strategy: Any = None,
    user_agent_suffix: Optional[str] = None,
    consistency_level: Optional[str] = None,
    proxy_allowed: Optional[bool] = None,
    connection_timeout_seconds: Optional[float] = None,
    read_timeout_seconds: Optional[float] = None,
    fault_injection_rules: Any = None,
    proxy_config: Any = None,
    proxies: Any = None,
    connection_verify: Any = None,
    connection_cert: Any = None,
    ssl_config: Any = None,
    transport: Any = None,
) -> Union[_BackendT, _LegacyBackendT]:
    """Construct a Python backend and release its async credential bridge on failure.

    The retained legacy test branch skips Rust validation. The Rust branch
    requires a nonempty endpoint and supported network settings before
    preparing credentials. The binding checks URL syntax later, when a driver
    handle is acquired.
    """
    name = resolve_backend_name(explicit)
    if name == BACKEND_NAME_RUST:
        if not url:
            raise ValueError(
                "The Rust binding requires the account endpoint URL."
            )
        reject_unsupported_transport_settings(
            proxy_config=proxy_config,
            proxies=proxies,
            connection_verify=connection_verify,
            connection_cert=connection_cert,
            ssl_config=ssl_config,
            transport=transport,
        )
        # Release the async credential bridge if later validation or construction
        # fails. Its thread may not have started, but it already holds the credential.
        with resolved_credential(credential) as (master_key, token_credential):
            return rust_backend_type(
                endpoint=url,
                master_key=master_key,
                token_credential=token_credential,
                client_config=build_client_config(
                    preferred_locations,
                    excluded_locations=excluded_locations,
                    throttling_max_retry_count=throttling_max_retry_count,
                    throttling_max_retry_wait_time_seconds=throttling_max_retry_wait_time_seconds,
                    availability_strategy=availability_strategy,
                    user_agent_suffix=user_agent_suffix,
                    consistency_level=consistency_level,
                    proxy_allowed=proxy_allowed,
                    connection_timeout_seconds=connection_timeout_seconds,
                    read_timeout_seconds=read_timeout_seconds,
                    fault_injection_rules=fault_injection_rules,
                ),
            )
    return legacy_backend


def make_backend(
    explicit: Optional[str],
    *,
    url: Optional[str] = None,
    credential: Any = None,
    preferred_locations: Optional[Sequence[str]] = None,
    excluded_locations: Optional[Sequence[str]] = None,
    throttling_max_retry_count: Optional[int] = None,
    throttling_max_retry_wait_time_seconds: Optional[float] = None,
    availability_strategy: Any = None,
    user_agent_suffix: Optional[str] = None,
    consistency_level: Optional[str] = None,
    proxy_allowed: Optional[bool] = None,
    connection_timeout_seconds: Optional[float] = None,
    read_timeout_seconds: Optional[float] = None,
    fault_injection_rules: Any = None,
    proxy_config: Any = None,
    proxies: Any = None,
    connection_verify: Any = None,
    connection_cert: Any = None,
    ssl_config: Any = None,
    transport: Any = None,
) -> CosmosBackend:
    """Build the synchronous Python wrapper object using shared preparation rules."""
    return _make_backend(
        explicit,
        rust_backend_type=RustBackend,
        legacy_backend=LEGACY_BACKEND,
        url=url,
        credential=credential,
        preferred_locations=preferred_locations,
        excluded_locations=excluded_locations,
        throttling_max_retry_count=throttling_max_retry_count,
        throttling_max_retry_wait_time_seconds=throttling_max_retry_wait_time_seconds,
        availability_strategy=availability_strategy,
        user_agent_suffix=user_agent_suffix,
        consistency_level=consistency_level,
        proxy_allowed=proxy_allowed,
        connection_timeout_seconds=connection_timeout_seconds,
        read_timeout_seconds=read_timeout_seconds,
        fault_injection_rules=fault_injection_rules,
        proxy_config=proxy_config,
        proxies=proxies,
        connection_verify=connection_verify,
        connection_cert=connection_cert,
        ssl_config=ssl_config,
        transport=transport,
    )