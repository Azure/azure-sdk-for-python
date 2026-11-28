# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Construct BindingAdapter or AsyncBindingAdapter with prepared client settings.

Rust is the default execution path. This checkout retains private controls for
comparing it with the legacy path: _backend takes precedence over COSMOS_BACKEND,
and an unset or blank selection uses Rust. These controls remain for migration
tests, not customer configuration.

This Python wrapper validates settings and prepares the credential before
creating BindingAdapter or AsyncBindingAdapter. These are Python classes that call
the binding. On first use, they acquire a driver handle through the binding.
Credential preparation acquires no bridge; the async adapter does that on first use.
"""
from __future__ import annotations

import os
from typing import Any, Callable, Mapping, Optional, Sequence, TypeVar, Union

from .cosmos_backend import CosmosBackend
from .client_config import build_client_config
from .constants import (
    BACKEND_ENV_VAR,
    BACKEND_NAME_RUST,
    DEFAULT_BACKEND_NAME,
    VALID_BACKEND_NAMES,
)
from .credentials import resolve_credential
from .legacy import LEGACY_BACKEND
from .binding_adapter import BindingAdapter
from ..runtime import CosmosRuntime

_BackendT = TypeVar("_BackendT")
_LegacyBackendT = TypeVar("_LegacyBackendT")

def resolve_backend_name(explicit: Optional[str]) -> str:
    """Read the temporary migration/test control and reject unknown values.

    Read the environment only when explicit is None. Strip surrounding spaces
    and ignore case, so " RUST " selects rust. A blank value selects the default,
    even if it was an explicit argument. Other unknown names or non-string
    arguments raise ValueError rather than silently running different code.
    This function does not define a customer-facing execution-path choice.

    :param explicit: Private backend selection, or None to consult the environment.
    :type explicit: str or None
    :return: Validated, normalized backend name.
    :rtype: str
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
    allow_async_credential: bool = False,
    url: Optional[str] = None,
    credential: Any = None,
    runtime: Optional[CosmosRuntime] = None,
    operation_timeout: Optional[float] = None,
    preferred_locations: Optional[Sequence[str]] = None,
    excluded_locations: Optional[Sequence[str]] = None,
    throttling_max_retry_count: Optional[int] = None,
    throttling_max_retry_wait_time_seconds: Optional[float] = None,
    availability_strategy: Any = None,
    user_agent_suffix: Optional[str] = None,
    consistency_level: Optional[str] = None,
    utf8_decoding_mode: Optional[str] = None,
    fault_injection_rules: Any = None,
    headers: Optional[Mapping[str, str]] = None,
) -> Union[_BackendT, _LegacyBackendT]:
    """Construct a Python backend without acquiring a credential bridge.

    The retained legacy test branch skips Rust validation. The Rust branch
    requires a nonempty endpoint before
    preparing credentials. The binding checks URL syntax later, when a driver
    handle is acquired.

    :param explicit: Private backend selection, or None to consult the environment.
    :type explicit: str or None
    :keyword rust_backend_type: Constructor for the synchronous or asynchronous Rust adapter.
    :paramtype rust_backend_type: typing.Callable
    :keyword legacy_backend: Existing backend returned for the legacy migration selection.
    :paramtype legacy_backend: typing.Any
    :keyword allow_async_credential: Whether the selected adapter supports asynchronous credentials.
    :paramtype allow_async_credential: bool
    :keyword url: Account endpoint, required for the Rust adapter.
    :paramtype url: str or None
    :keyword credential: Account key, master-key mapping, or token credential.
    :paramtype credential: typing.Any
    :keyword runtime: Explicit runtime, or None to use the default upon driver acquisition.
    :paramtype runtime: ~azure.cosmos.runtime.CosmosRuntime or None
    :keyword operation_timeout: Default overall operation budget in seconds, or None.
    :paramtype operation_timeout: float or None
    :keyword preferred_locations: Ordered preferred region names, or None.
    :paramtype preferred_locations: typing.Sequence[str] or None
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
    :keyword fault_injection_rules: Internal test-only fault rule mappings, or None.
    :paramtype fault_injection_rules: typing.Any
    :keyword headers: Default application request headers, or None.
    :paramtype headers: typing.Mapping[str, str] or None
    :return: Constructed Rust adapter or the supplied legacy backend.
    :rtype: typing.Any
    """
    name = resolve_backend_name(explicit)
    if name == BACKEND_NAME_RUST:
        if not url:
            raise ValueError(
                "The Rust binding requires the account endpoint URL."
            )
        # Async adapters bind caller-owned credentials to their loop on first use.
        master_key, token_credential = resolve_credential(credential, allow_async=allow_async_credential)
        return rust_backend_type(
            endpoint=url,
            master_key=master_key,
            token_credential=token_credential,
            runtime=runtime,
            client_config=build_client_config(
                preferred_locations,
                excluded_locations=excluded_locations,
                throttling_max_retry_count=throttling_max_retry_count,
                throttling_max_retry_wait_time_seconds=throttling_max_retry_wait_time_seconds,
                availability_strategy=availability_strategy,
                user_agent_suffix=user_agent_suffix,
                consistency_level=consistency_level,
                utf8_decoding_mode=utf8_decoding_mode,

                fault_injection_rules=fault_injection_rules,
                headers=headers,
                operation_timeout_seconds=operation_timeout,
            ),
        )
    if runtime is not None:
        raise ValueError("runtime is supported only by the Rust backend.")
    if utf8_decoding_mode is not None:
        raise ValueError("utf8_decoding_mode is supported only by the Rust backend.")
    return legacy_backend


def make_backend(
    explicit: Optional[str],
    *,
    url: Optional[str] = None,
    credential: Any = None,
    runtime: Optional[CosmosRuntime] = None,
    operation_timeout: Optional[float] = None,
    preferred_locations: Optional[Sequence[str]] = None,
    excluded_locations: Optional[Sequence[str]] = None,
    throttling_max_retry_count: Optional[int] = None,
    throttling_max_retry_wait_time_seconds: Optional[float] = None,
    availability_strategy: Any = None,
    user_agent_suffix: Optional[str] = None,
    consistency_level: Optional[str] = None,
    utf8_decoding_mode: Optional[str] = None,
    fault_injection_rules: Any = None,
    headers: Optional[Mapping[str, str]] = None,
) -> CosmosBackend:
    """Build the synchronous Python wrapper object using shared preparation rules.

    :param explicit: Private backend selection, or None to consult the environment.
    :type explicit: str or None
    :keyword url: Account endpoint, required for the Rust adapter.
    :paramtype url: str or None
    :keyword credential: Account key, master-key mapping, or synchronous token credential.
    :paramtype credential: typing.Any
    :keyword runtime: Explicit runtime, or None to use the default upon driver acquisition.
    :paramtype runtime: ~azure.cosmos.runtime.CosmosRuntime or None
    :keyword operation_timeout: Default overall operation budget in seconds, or None.
    :paramtype operation_timeout: float or None
    :keyword preferred_locations: Ordered preferred region names, or None.
    :paramtype preferred_locations: typing.Sequence[str] or None
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
    :keyword fault_injection_rules: Internal test-only fault rule mappings, or None.
    :paramtype fault_injection_rules: typing.Any
    :keyword headers: Default application request headers, or None.
    :paramtype headers: typing.Mapping[str, str] or None
    :return: Selected synchronous backend without acquiring a driver.
    :rtype: ~azure.cosmos._backend.cosmos_backend.CosmosBackend
    """
    return _make_backend(
        explicit,
        rust_backend_type=BindingAdapter,
        legacy_backend=LEGACY_BACKEND,
        url=url,
        credential=credential,
        runtime=runtime,
        operation_timeout=operation_timeout,
        preferred_locations=preferred_locations,
        excluded_locations=excluded_locations,
        throttling_max_retry_count=throttling_max_retry_count,
        throttling_max_retry_wait_time_seconds=throttling_max_retry_wait_time_seconds,
        availability_strategy=availability_strategy,
        user_agent_suffix=user_agent_suffix,
        consistency_level=consistency_level,
        utf8_decoding_mode=utf8_decoding_mode,

        fault_injection_rules=fault_injection_rules,
        headers=headers,
    )
