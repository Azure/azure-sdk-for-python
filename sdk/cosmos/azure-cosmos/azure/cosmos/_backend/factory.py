# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The single entry point for backend selection.

Consistent terms used throughout this file:

* **client** -- the ``CosmosClient`` object a customer creates in their code.
* **backend** -- which engine runs the database calls: ``core-python`` (the
  original all-Python one) or ``rust`` (the new one that hands the work to a
  rust driver).
* **rust driver** -- the engine itself; it owns the network connection pool, the
  auth (request signing), and region routing. The **binding** is the compiled
  ``azure.cosmos._rust`` layer Python calls into to reach it (the compiled file
  holds both). The binding keeps one rust driver per distinct ``(endpoint,
  credential, config)`` and reference-counts it, so same-settings clients share
  one; the **driver handle** is the string that names which rust driver a client
  uses.
* **credential** -- how the customer proves who they are (a master key, or a
  token from ``azure-identity``).

High-level view -- what this file does
--------------------------------------

When a customer writes ``CosmosClient(url, credential, _backend="rust")``,
something has to (1) decide which engine that client will use, and (2) if it is
the Rust engine, check that everything the customer passed is something the Rust
engine can actually handle, and repackage it into the shape the driver expects.
That is this file's whole job. The client calls :func:`make_backend` once, at
construction, and stores what it returns: a :class:`RustBackend` object if Rust
was chosen, or ``None`` if core-python was chosen (the rest of the SDK reads
"no backend object" as "use the original Python path").

If this file didn't exist: that decide-and-check-and-repackage logic would have
to live inside ``CosmosClient`` itself -- and be duplicated in both the sync and
async clients. The moment those two copies diverged, bugs would appear on one
side only. Worse, without the up-front checks, a customer who passed something Rust
can't do yet (say, a custom proxy, or Bounded Staleness consistency) wouldn't
find out at ``CosmosClient(...)``. It would appear to work, then fail on their
first database call with a confusing low-level error far from the real cause.
This file's core value is failing early and clearly, at construction, with a
message that says exactly what to do instead.

Selection precedence (highest wins): the ``_backend=`` kwarg, then the
``COSMOS_BACKEND`` environment variable, then the ``core-python`` default. An
invalid value raises ``ValueError`` at construction time.

The three checking steps :func:`make_backend` combines each live in their own
module, so the async factory can reuse them without importing this one:

* :mod:`~azure.cosmos._backend.credentials` -- sorting the credential.
* :mod:`~azure.cosmos._backend.transport_settings` -- rejecting network and TLS
  settings the driver cannot honor.
* :mod:`~azure.cosmos._backend.client_config` -- gathering the tuning options.
"""
from __future__ import annotations

import os
from typing import Any, Optional, Sequence

from .base import CosmosBackend
from .client_config import build_client_config
from .constants import (
    BACKEND_ENV_VAR,
    BACKEND_NAME_RUST,
    DEFAULT_BACKEND_NAME,
    RUST_STRICT_ISOLATION_ENV_VAR,
    STRICT_ISOLATION_FALSE_VALUES,
    STRICT_ISOLATION_TRUE_VALUES,
    VALID_BACKEND_NAMES,
)
from .credentials import resolved_credential
from .rust import RustBackend
from .transport_settings import reject_unsupported_transport_settings

def resolve_backend_name(explicit: Optional[str]) -> str:
    """Decide the engine name from the ``_backend=`` argument, else the
    ``COSMOS_BACKEND`` environment variable, else the ``core-python`` default,
    and return a name in ``VALID_BACKEND_NAMES``.

    Without it: a stray trailing newline or ``"RUST"`` in caps from a
    copy-pasted env var would be treated as a typo and rejected; and a real typo
    would silently fall back to the wrong engine instead of telling the customer.
    So surrounding whitespace and case are tolerated (``RUST``, `` rust`` all
    work), an empty or whitespace-only value counts as "not specified" and uses
    ``DEFAULT_BACKEND_NAME``, but a non-empty value that is not a known backend
    (a genuine typo) raises ``ValueError`` loudly. There are no aliases: one
    canonical spelling per backend.

    Shared between the sync and async factories so the rules, valid
    values, and error message live in one place.
    """
    raw = explicit if explicit is not None else os.environ.get(BACKEND_ENV_VAR)
    if raw is not None and not isinstance(raw, str):
        # The env var is always a string; only the constructor kwarg can be a
        # non-string. Raise the same clear ValueError the typo path raises, rather
        # than letting .strip() throw an opaque AttributeError.
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


def resolve_strict_isolation(explicit: Optional[bool]) -> bool:
    """Read an on/off safety switch that controls whether the Rust backend uses
    strict per-account engine isolation.

    Precedence (highest wins): an explicit factory toggle, then the
    ``COSMOS_RUST_STRICT_ISOLATION`` environment variable, then off. Without it:
    an unrecognized value like ``"treu"`` would quietly leave the safety switch
    off, which is exactly the outcome a safety switch must never have -- so it
    raises instead. The env var is matched case-insensitively after trimming
    whitespace: ``STRICT_ISOLATION_TRUE_VALUES`` turn it on,
    ``STRICT_ISOLATION_FALSE_VALUES`` (and unset or empty) turn it off, and any
    other value raises ``ValueError``. Shared by the sync and async factories so
    the rule lives in one place.

    When on, a second ``CosmosClient`` to an account whose config differs from the
    first live client's raises
    :class:`~azure.cosmos._backend._driver_registry.StrictEngineIsolationError` at
    construction instead of silently building a second isolated engine.
    """
    if explicit is not None:
        if not isinstance(explicit, bool):
            # A safety toggle must never be driven by an ambiguous truthy value
            # (a non-empty string like "false" is truthy and would turn the guard
            # ON). Require a real bool, matching how the env-var path rejects
            # unrecognized values below.
            raise ValueError(
                "strict_isolation must be a bool when provided; got {!r}. A safety "
                "toggle is never driven by an ambiguous truthy value.".format(
                    type(explicit).__name__
                )
            )
        return explicit
    value = os.environ.get(RUST_STRICT_ISOLATION_ENV_VAR)
    if value is None:
        return False
    normalized = value.strip().lower()
    if normalized in STRICT_ISOLATION_TRUE_VALUES:
        return True
    if normalized == "" or normalized in STRICT_ISOLATION_FALSE_VALUES:
        return False
    raise ValueError(
        "Invalid {} value {!r}. Expected one of {} (on) or {} (off), or leave it "
        "unset. A safety toggle is never silently disabled by an unrecognized "
        "value.".format(
            RUST_STRICT_ISOLATION_ENV_VAR,
            value,
            STRICT_ISOLATION_TRUE_VALUES,
            STRICT_ISOLATION_FALSE_VALUES,
        )
    )


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
    strict_isolation: Optional[bool] = None,
    proxy_config: Any = None,
    proxies: Any = None,
    connection_verify: Any = None,
    connection_cert: Any = None,
    ssl_config: Any = None,
    transport: Any = None,
) -> Optional[CosmosBackend]:
    """The one public entry point that combines the rest of this file: build
    the backend instance a sync ``CosmosClient`` will hold.

    Without it: the client constructor would have to do all of the below itself,
    in two places (sync and async), which invites one-sided bugs when the two
    copies diverge. So this resolves the name; if Rust, requires the endpoint URL,
    rejects unsupported transport settings, sorts the credential, combines the
    tuning into a config, resolves the isolation switch, and returns a
    :class:`RustBackend`. If core-python, it returns ``None``.

    The keyword settings are only consulted for the Rust branch, where they are
    combined into the client config the backend carries to the driver.
    ``strict_isolation`` (kwarg > the ``COSMOS_RUST_STRICT_ISOLATION`` env var >
    off) controls whether a second client to an account with a different config
    raises instead of silently getting its own isolated engine. The transport/TLS
    settings (``proxy_config`` / ``proxies`` / ``connection_verify`` /
    ``connection_cert`` / ``ssl_config`` / ``transport``) are not combined into the
    config -- the Rust path still can't honor explicit proxy/transport objects, so
    they are rejected here; they are ignored entirely on the core-python branch,
    which honors them as before. ``proxy_allowed`` is the Rust-path proxy switch
    carried into the driver runtime.
    """
    name = resolve_backend_name(explicit)
    if name == BACKEND_NAME_RUST:
        if not url:
            raise ValueError(
                "_backend='rust' requires the account endpoint URL."
            )
        reject_unsupported_transport_settings(
            proxy_config=proxy_config,
            proxies=proxies,
            connection_verify=connection_verify,
            connection_cert=connection_cert,
            ssl_config=ssl_config,
            transport=transport,
        )
        # Sort the credential inside the guard: an async credential becomes a
        # bridge holding a background thread, and everything below can still raise
        # (config validation, process-wide policy conflicts, strict isolation), which
        # would otherwise strand that thread with no owner left to close it.
        with resolved_credential(credential) as (master_key, token_credential):
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
                    user_agent_suffix=user_agent_suffix,
                    consistency_level=consistency_level,
                    proxy_allowed=proxy_allowed,
                    connection_timeout_seconds=connection_timeout_seconds,
                    read_timeout_seconds=read_timeout_seconds,
                ),
                strict_isolation=resolve_strict_isolation(strict_isolation),
            )
    return None