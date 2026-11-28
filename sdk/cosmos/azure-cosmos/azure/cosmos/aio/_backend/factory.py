# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Construct the asynchronous Python backend using shared preparation rules.

``azure.cosmos._backend.factory._make_backend`` decides which Python backend to
use and checks its startup inputs without acquiring a credential bridge.
This module supplies AsyncBindingAdapter and the shared AsyncLegacyBackend instance.
Legacy-path selection is a migration control, not a release execution choice.

Construction itself is synchronous: make_async_backend(...) returns a Python
object without acquiring a driver handle. Operations on AsyncBindingAdapter later
call the binding and await its results.
"""
from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

from azure.cosmos._backend.factory import _make_backend
from azure.cosmos.runtime import CosmosRuntime

from .cosmos_backend import AsyncCosmosBackend
from .legacy import ASYNC_LEGACY_BACKEND
from .binding_adapter import AsyncBindingAdapter


def make_async_backend(
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
) -> AsyncCosmosBackend:
    """Return a Python backend for async operations; this factory is not awaited.

    For example, endpoint and preferred-region inputs become the stored settings
    of AsyncBindingAdapter. Construction retains the selected runtime and
    rejects retired network settings, without initializing the default runtime.

    :param explicit: Private backend selection, or None to consult the environment.
    :type explicit: str or None
    :keyword url: Account endpoint, required for the Rust adapter.
    :paramtype url: str or None
    :keyword credential: Account key, master-key mapping, or synchronous or asynchronous token credential.
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
    :return: Selected asynchronous backend without acquiring a driver.
    :rtype: ~azure.cosmos.aio._backend.cosmos_backend.AsyncCosmosBackend
    """
    return _make_backend(
        explicit,
        rust_backend_type=AsyncBindingAdapter,
        legacy_backend=ASYNC_LEGACY_BACKEND,
        allow_async_credential=True,
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
