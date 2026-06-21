# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Factory that picks which backend a single client will use.

``CosmosClient`` calls ``make_backend(...)`` exactly once at
construction time and stores the returned object.

Selection precedence (highest wins):

1. ``_backend=`` kwarg passed to the client constructor.
2. ``COSMOS_BACKEND`` environment variable.
3. Default: ``core-python``.

An invalid value raises ``ValueError`` at construction time.

When ``rust`` is selected the factory needs the account endpoint and either a
master-key credential or a *synchronous* token credential (Entra/AAD via
``azure-identity``). Async token credentials and resource-token auth are
rejected upfront for now -- a temporary limitation until the Rust driver
supports them.

When ``core-python`` is selected the factory returns ``None``; the
helper layer treats absence-of-backend as the signal to use the legacy
``client_connection.CreateItem`` path.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any, Optional, Sequence, Tuple

from .._availability_strategy_config import CrossRegionHedgingStrategy, DEFAULT_THRESHOLD_MS
from .base import CosmosBackend, PreparedClientConfig
from .constants import (
    BACKEND_ENV_VAR,
    BACKEND_NAME_RUST,
    DEFAULT_BACKEND_NAME,
    VALID_BACKEND_NAMES,
)
from .rust import RustBackend


def resolve_backend_name(explicit: Optional[str]) -> str:
    """Apply the precedence rules above and return a name in ``VALID_BACKEND_NAMES``.

    Shared between the sync and async factories so the rules, valid
    values, and error message live in one place.
    """
    if explicit is not None:
        choice = explicit
    else:
        choice = os.environ.get(BACKEND_ENV_VAR, DEFAULT_BACKEND_NAME)
    if choice not in VALID_BACKEND_NAMES:
        raise ValueError(
            "Invalid backend {!r}. Expected one of {}. "
            "Set the constructor kwarg _backend=, or the {} environment variable.".format(
                choice, VALID_BACKEND_NAMES, BACKEND_ENV_VAR
            )
        )
    return choice


def _resolve_credential(credential: Any) -> Tuple[Optional[str], Optional[Any]]:
    """Classify the credential for the Rust backend into either a master key or a
    synchronous token credential, or raise ``ValueError``.

    Returns ``(master_key, token_credential)`` with exactly one entry set:

    * a ``str`` or a dict with a ``'masterKey'`` entry -> master key;
    * an object with a synchronous ``get_token`` (e.g. an ``azure-identity``
      credential) -> token credential, forwarded to the driver, which calls
      ``get_token`` during request signing;
    * an *async* token credential (``get_token`` is a coroutine function) is
      rejected: the binding calls ``get_token`` synchronously and has no event
      loop to drive a coroutine on the driver's worker thread;
    * anything else (resource-token dicts, ``None``) is rejected.

    Rejecting upfront -- at client construction -- means an unsupported auth
    shape fails loudly and immediately rather than on the first request.
    """
    if isinstance(credential, str):
        return credential, None
    if isinstance(credential, dict) and "masterKey" in credential:
        return credential["masterKey"], None
    get_token = getattr(credential, "get_token", None)
    if callable(get_token):
        if asyncio.iscoroutinefunction(get_token):
            raise ValueError(
                "_backend='rust' does not support async token credentials yet "
                "(get_token is a coroutine). Use a synchronous token credential, "
                "or the core-python backend."
            )
        return None, credential
    # Falls through for resource-token dicts, None, and any other shape.
    raise ValueError(
        "_backend='rust' requires a master-key credential (a string, or a dict "
        "with a 'masterKey' entry) or a synchronous token credential. The Rust "
        "backend does not support resource-token auth."
    )


def build_client_config(
    preferred_locations: Optional[Sequence[str]] = None,
    *,
    excluded_locations: Optional[Sequence[str]] = None,
    throttling_max_retry_count: Optional[int] = None,
    throttling_max_retry_wait_time_seconds: Optional[float] = None,
    availability_strategy: Any = None,
) -> Optional[PreparedClientConfig]:
    """Collect the client-construction settings the Rust backend can carry into
    a :class:`PreparedClientConfig`, or ``None`` when there is nothing to carry.

    Returning ``None`` keeps the no-config path identical to the original
    two-argument ``init_client`` call (the binding then builds the driver with
    its defaults). Shared by the sync and async factories so the
    kwarg-to-config mapping lives in exactly one place.

    Each setting is carried only when the customer actually expressed it, so an
    untuned client behaves exactly as before:

    * ``preferred_locations`` / ``excluded_locations`` -- empty means "no
      preference / no exclusion".
    * throttling caps -- ``None`` means "untuned"; the driver keeps its own
      defaults (9 retries / 30 s), which match Python-core's.
    * ``availability_strategy`` -- ``None`` (absent) carries nothing, so the
      driver keeps its default; ``False`` carries an explicit disable; ``True``
      or a dict carries the hedging threshold.
    """
    preferred = tuple(preferred_locations) if preferred_locations else ()
    excluded = tuple(excluded_locations) if excluded_locations else ()
    hedging_threshold_ms = _resolve_hedging(availability_strategy)
    if (
        not preferred
        and not excluded
        and throttling_max_retry_count is None
        and throttling_max_retry_wait_time_seconds is None
        and hedging_threshold_ms is None
    ):
        return None
    return PreparedClientConfig(
        preferred_locations=preferred,
        excluded_locations=excluded,
        throttling_max_retry_count=throttling_max_retry_count,
        throttling_max_retry_wait_time_seconds=throttling_max_retry_wait_time_seconds,
        hedging_threshold_ms=hedging_threshold_ms,
    )


def _resolve_hedging(availability_strategy: Any) -> Optional[int]:
    """Map the ``availability_strategy`` kwarg to a hedge threshold in ms, or
    ``None`` to carry nothing.

    Carries a threshold only when the customer *enabled* hedging: ``True`` uses
    the default threshold and a dict uses its ``threshold_ms`` (validated ``> 0``
    by reusing :class:`CrossRegionHedgingStrategy`). ``None`` (absent) and
    ``False`` carry nothing -- matching Python-core, where the client default is
    "no strategy" -- so sync (kwarg) and async (an explicit ``False``-default
    parameter) behave identically. Python's ``threshold_steps_ms`` has no driver
    equivalent and is intentionally dropped.
    """
    if availability_strategy is True:
        return DEFAULT_THRESHOLD_MS
    if isinstance(availability_strategy, dict):
        # Reuse the existing validator so an invalid threshold_ms raises the same
        # ValueError it would on the legacy path.
        return CrossRegionHedgingStrategy(availability_strategy).threshold_ms
    # None, False, or an unrecognized shape: carry nothing.
    return None


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
) -> Optional[CosmosBackend]:
    """Build the backend instance a sync ``CosmosClient`` will hold.

    Returns a :class:`RustBackend` when Rust is selected, or ``None``
    when core-python is selected. The keyword settings are only consulted
    for the Rust branch, where they are folded into the client config the
    backend carries to the driver.
    """
    name = resolve_backend_name(explicit)
    if name == BACKEND_NAME_RUST:
        if not url:
            raise ValueError(
                "_backend='rust' requires the account endpoint URL."
            )
        master_key, token_credential = _resolve_credential(credential)
        return RustBackend(
            endpoint=url,
            master_key=master_key,
            token_credential=token_credential,
            client_config=build_client_config(
                preferred_locations,
                excluded_locations=excluded_locations,
                throttling_max_retry_count=throttling_max_retry_count,
                throttling_max_retry_wait_time_seconds=throttling_max_retry_wait_time_seconds,
                availability_strategy=availability_strategy,
            ),
        )
    return None


