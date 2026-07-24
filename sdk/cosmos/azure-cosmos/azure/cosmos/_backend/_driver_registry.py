# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Per-process guard, in the python wrapper, for the Rust backend's per-engine
isolation, where an *engine* is one live rust driver keyed by the triple
``(endpoint, credential, config)`` -- not by account alone.

Three layers are named consistently throughout this module:

* **python wrapper** -- the pure-Python SDK (this guard, ``_shared.py``, ``rust.py``).
  This guard runs here, on the caller's own python-wrapper thread, at client
  open/close.
* **binding layer** -- the Rust extension (``runtime.rs``) the wrapper calls into. It
  owns the real engine cache, the per-engine refcount, and lazy build/teardown.
* **rust driver layer** -- the engine itself: one in-process ``CosmosDriver`` on the
  shared Tokio runtime, holding the connection pools and rust-driver worker threads.
  It is an in-process object, *not* a separate OS process.

Two terms used everywhere below:

* *Engine identity* is the triple ``(endpoint, credential, config)``: two clients
  share one engine only when all three match. The account (endpoint) is just the
  top-level grouping; within it each distinct ``(credential, config)`` pair is its own
  engine.
* *Config* is the ``PreparedClientConfig`` -- the subset of ``CosmosClient`` settings
  carried to the binding (preferred/excluded locations, consistency, throttling,
  hedging, user-agent suffix, and process-wide proxy/transport settings). It compares
  by value; ``None`` means untuned. The binding derives its identity key from its
  ``repr()``.

The high-level view -- this module is a *detector, not a fixer*. It has no effect on
how engines are actually created or freed; that all lives in the binding. So if this
module did not exist:

* **Nothing functional would change.** The binding still shares one engine when
  endpoint+credential+config match and still builds a separate engine when they differ;
  its per-engine refcount, lazy build on first op, and teardown are untouched.
  Connection pools, memory, latency, and correctness in default use are identical --
  default mode never reads this module's data.
* **The only thing lost is strict isolation mode** -- the opt-in early warning. Without
  it there is no way to detect, at construction, that a client is about to make the
  binding build a *second* engine for an account that already has one. Teams that want
  a "one engine per account" guarantee would get no early signal: accidentally building
  many engines (a loop of slightly different clients, or two clients with different
  credentials/configs to one account) proceeds silently and is discovered only later,
  indirectly, via the symptoms it was meant to prevent -- growing connections, file
  descriptors, and memory in production.

In short: without this module nothing breaks and nothing leaks that was not already
possible -- the only thing lost is the opt-in early warning that turns silently
building many engines into an immediate, fail-fast error at construction time.

The problem it guards against: the binding shares one engine between two clients only
when their endpoint, credential, *and* config all match; differ on any one and it
builds a *second* engine for the same account. That is safe (no settings are dropped)
but a loop or service that opens many slightly different clients can quietly
accumulate many engines for one account -- more connections and memory than expected,
usually noticed only later in production.

This guard runs in the real workflow: ``_shared.py`` calls it on every client open and
close. Strict isolation mode is an opt-in that makes the guard act on that
bookkeeping. When on, a later client that would build a new engine for an account that
already has one raises ``StrictEngineIsolationError`` at construction. By default the
second engine is allowed silently and the guard only keeps bookkeeping -- its behavior
matters only when strict mode is enabled (a service or CI that means to reuse one
engine).

To decide correctly the guard copies the binding's cache key. For each account it
tracks the live engines -- one entry per distinct ``(credential, config)`` pair, with
a count of how many clients hold it -- so a later client is allowed when its pair
matches one still live and flagged when it would build a new one. Three details keep
this copy accurate:

* The credential is part of the key, because the binding builds an engine on a
  credential difference too.
* The endpoint is canonicalized, so ``https://acct...com`` and
  ``https://acct...com/`` (and host-case variants) map to the same account key.
* No secret is retained: a master key is reduced to a non-reversible hash
  before it is used as a key, and a token credential is keyed by object identity.

Three independent counts exist: (1) Python's own object refcount
frees Python objects and knows nothing about engines. (2) This module's count is the
opt-in guard -- it runs at client open/close, in the python wrapper, before and
independently of the binding. (3) The binding's per-engine refcount governs the real
engine's lifetime and is built lazily: ``rust.py`` calls the binding's ``init_client``
only on the first item operation, not at client construction.

This module is **not** part of the binding's cache. It is a separate record in the
python wrapper that *copies* the binding's cache key so it can predict, at client
construction, whether the binding would build a new engine -- it never reads or calls
into the binding.

"""
from __future__ import annotations

import hashlib
import threading
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlsplit, urlunsplit

from .base import PreparedClientConfig


class StrictEngineIsolationError(ValueError):
    """Raised by this guard (in the python wrapper) when, under strict isolation, a
    later ``CosmosClient`` would make the binding build a *second* engine (rust driver)
    for an account: it targets an account another live client already targets, but
    with a credential or config that matches no engine live for that account.

    Opt-in: it fires only when strict isolation is enabled (the
    ``COSMOS_RUST_STRICT_ISOLATION`` env var or the factory toggle), and it fires at
    client construction -- before the binding lazily builds any engine. By default the
    second client is allowed and gets its own isolated engine.
    """


class ProxyPolicyConflictError(ValueError):
    """Raised at client construction when a ``CosmosClient`` requests an explicit
    ``proxy_allowed`` that differs from the value already established for this process.

    Why this is separate from the engine-isolation guard above: ``proxy_allowed`` is
    not a per-account setting. It configures the Rust runtime (the Tokio reactor +
    ``CosmosDriverRuntime``), which is a process-global singleton built once -- by
    whichever client triggers the first operation -- and frozen for the life of the
    process (``runtime.rs`` ``OnceLock``). So every Rust-backed client in the process
    that sets ``proxy_allowed`` must agree on one value. The binding does enforce this,
    but only lazily at the first operation and with a race-determined winner under
    concurrent construction; this guard makes the conflict deterministic and fail-fast
    at construction, in both default and strict mode (the engine-isolation registry
    cannot catch it because it treats ``proxy_allowed`` as just another per-account
    config field). Clients that leave ``proxy_allowed`` unset (``None``) never set or
    conflict with the policy, matching the binding's ``proxy_allowed_conflicts``.

    To avoid this error, establish the policy deterministically: construct one client
    with the desired ``proxy_allowed`` before any others (and before any concurrent
    client construction), and set the same value -- or leave it unset -- on the rest.
    """


class TransportTimeoutPolicyConflictError(ValueError):
    """Raised when Rust clients request different process-wide transport timeouts."""


# Process-global ``proxy_allowed`` policy. Unlike the per-account ``_REGISTRY`` above,
# this is a single value for the whole process because the Rust runtime it configures is
# a process singleton. ``_PROXY_POLICY_SET`` distinguishes "no explicit value seen yet"
# from "explicitly set to None" (the binding treats ``proxy_allowed=None`` as "no
# opinion", so a None-setting client never establishes the policy). Guarded by _LOCK.
_PROXY_POLICY: Optional[bool] = None
_PROXY_POLICY_SET: bool = False
_CONNECTION_TIMEOUT_POLICY: Optional[float] = None
_CONNECTION_TIMEOUT_POLICY_SET: bool = False
_READ_TIMEOUT_POLICY: Optional[float] = None
_READ_TIMEOUT_POLICY_SET: bool = False


# Canonical endpoint -> the live engines for that account. Each key is a
# ``(credential_key, config)`` pair -- one engine (a rust driver the binding would
# build and cache) -- mapped to the number of live clients holding it. An account drops
# out only when its last engine's last client is released. Guarded by _LOCK. This is the
# python wrapper's own count, separate from the binding's per-engine refcount.
_LOCK = threading.Lock()
_REGISTRY: Dict[str, Dict[Tuple[Any, Optional[PreparedClientConfig]], int]] = {}


def _canonicalize_endpoint(endpoint: str) -> str:
    """Normalize an account endpoint so trivial URL variants of the same account
    share one registry entry.

    Lowercases scheme and host (DNS is case-insensitive), drops a default port and
    a trailing slash, and discards any query or fragment. Conservative on purpose:
    so two different accounts never collapse, anything that does not parse as a
    scheme+host URL is returned unchanged.
    """
    if not endpoint:
        return endpoint
    try:
        parts = urlsplit(endpoint)
        if not parts.scheme or not parts.netloc:
            return endpoint
        scheme = parts.scheme.lower()
        host = (parts.hostname or "").lower()
        if not host:
            return endpoint
        default_port = {"https": 443, "http": 80}.get(scheme)
        port = parts.port
        netloc = host if port is None or port == default_port else "{0}:{1}".format(host, port)
        path = parts.path.rstrip("/")
        return urlunsplit((scheme, netloc, path, "", ""))
    except ValueError:
        # Malformed URL (e.g. a bad port): fall back to the raw string rather than
        # guessing, so the guard never coalesces things it cannot parse.
        return endpoint


def make_credential_key(master_key: Optional[str], token_credential: Optional[Any]) -> Any:
    """Reduce a client's credential to a hashable identity matching the binding's.

    The factory supplies exactly one of the two. A token credential is keyed by its
    object identity (``id``), which equals the raw pointer the binding uses as its key
    (``as_ptr``); the client holds a strong reference for its whole life, so that
    identity is stable while it is registered. A master key is reduced to a
    non-reversible hash, so this module never keeps the plaintext secret --
    equal keys hash equal, different keys do not. Both ``None`` keys as ``None``.
    """
    if token_credential is not None:
        return id(token_credential)
    if master_key is not None:
        return "mk:" + hashlib.sha256(master_key.encode("utf-8")).hexdigest()
    return None


def register_proxy_policy(config: Optional[PreparedClientConfig]) -> None:
    """Enforce a single process-wide ``proxy_allowed`` policy, fail-fast at construction.

    The Rust runtime's proxy setting is process-global (one ``OnceLock``-backed runtime
    per process), so every Rust-backed client that sets ``proxy_allowed`` must agree on
    one value. This makes that agreement deterministic at construction instead of leaving
    it to the binding's lazy, race-determined check at the first operation.

    Rules (matching the binding's ``proxy_allowed_conflicts``):

    * A client that does not set ``proxy_allowed`` (``None``) is always compatible and
      never establishes the policy -- it accepts whatever value wins.
    * The first client with an explicit value establishes the process policy.
    * A later client with a *different* explicit value raises
      ``ProxyPolicyConflictError``. An equal value is accepted (idempotent).

    Called from ``_shared`` at client construction, before ``register_client_config``,
    so a proxy conflict fails before the client records any engine registration to
    release. The Rust ``OnceLock`` conflict check remains the fallback -- this guard
    only turns the late, nondeterministic failure into an early, deterministic one. It
    does not eliminate the case where a ``None``-setting client operates first and
    lazily fixes the runtime to its default before an explicit-value client is built;
    that requires the practice of constructing the proxy-setting client first.
    """
    if config is None or config.proxy_allowed is None:
        return
    requested = config.proxy_allowed
    global _PROXY_POLICY, _PROXY_POLICY_SET  # pylint: disable=global-statement
    with _LOCK:
        if not _PROXY_POLICY_SET:
            _PROXY_POLICY = requested
            _PROXY_POLICY_SET = True
            return
        if _PROXY_POLICY != requested:
            raise ProxyPolicyConflictError(
                "proxy_allowed is process-global for the Rust backend and was already "
                "established as proxy_allowed={established!r} by an earlier CosmosClient; "
                "this client requests proxy_allowed={requested!r}. Set the same "
                "proxy_allowed value on every Rust-backed CosmosClient in the process "
                "(or leave it unset), and construct the client that sets it first, "
                "before any others.".format(established=_PROXY_POLICY, requested=requested)
            )


def register_transport_timeout_policy(config: Optional[PreparedClientConfig]) -> None:
    """Fail fast when Rust clients disagree on process-wide transport timeouts."""
    if config is None:
        return
    requested_connection = config.connection_timeout_seconds
    requested_read = config.read_timeout_seconds
    if requested_connection is None and requested_read is None:
        return

    global _CONNECTION_TIMEOUT_POLICY  # pylint: disable=global-statement
    global _CONNECTION_TIMEOUT_POLICY_SET  # pylint: disable=global-statement
    global _READ_TIMEOUT_POLICY  # pylint: disable=global-statement
    global _READ_TIMEOUT_POLICY_SET  # pylint: disable=global-statement
    with _LOCK:
        conflicts = []
        if (
            requested_connection is not None
            and _CONNECTION_TIMEOUT_POLICY_SET
            and _CONNECTION_TIMEOUT_POLICY != requested_connection
        ):
            conflicts.append(
                "connection_timeout={requested!r} (already {established!r})".format(
                    requested=requested_connection,
                    established=_CONNECTION_TIMEOUT_POLICY,
                )
            )
        if (
            requested_read is not None
            and _READ_TIMEOUT_POLICY_SET
            and _READ_TIMEOUT_POLICY != requested_read
        ):
            conflicts.append(
                "read_timeout={requested!r} (already {established!r})".format(
                    requested=requested_read,
                    established=_READ_TIMEOUT_POLICY,
                )
            )
        if conflicts:
            raise TransportTimeoutPolicyConflictError(
                "Rust transport timeouts are process-global; this CosmosClient "
                "conflicts with an earlier client: {}. Set the same constructor "
                "timeouts on every Rust-backed CosmosClient in the process.".format(
                    ", ".join(conflicts)
                )
            )

        if requested_connection is not None and not _CONNECTION_TIMEOUT_POLICY_SET:
            _CONNECTION_TIMEOUT_POLICY = requested_connection
            _CONNECTION_TIMEOUT_POLICY_SET = True
        if requested_read is not None and not _READ_TIMEOUT_POLICY_SET:
            _READ_TIMEOUT_POLICY = requested_read
            _READ_TIMEOUT_POLICY_SET = True


def register_client_config(
    endpoint: str,
    config: Optional[PreparedClientConfig] = None,
    credential_key: Any = None,
    strict: bool = False,
) -> None:
    """Record one live client against ``endpoint``. Called by the python wrapper when a
    client is opened, before and independently of the binding building any engine.

    The client's engine identity is its ``(credential_key, config)`` pair -- the
    same key (with the endpoint) the binding keys its rust-driver cache by. A
    client that matches an engine already live for the account shares it: its count
    goes up and strict mode never fires. A client whose pair matches no live engine
    would make the binding build a new one:

    * strict -- raise ``StrictEngineIsolationError`` without recording, so the
      failed client never enters a count (it is not built, so it must not be
      released later) and the existing counts stay correct.
    * default -- record the new engine and return; the binding gives it its own
      isolated driver, so nothing is dropped.

    The first client to an account always records, whatever its strict flag.
    ``PreparedClientConfig`` compares by value and ``None`` (an untuned client)
    compares cleanly, so two untuned clients -- or two with equal settings and the
    same credential -- share one engine and never trigger the strict check.

    :param endpoint: The account endpoint the client targets (canonicalized here).
    :param config: The client's prepared config, or ``None`` when untuned.
    :param credential_key: The client's credential identity from
        ``make_credential_key``; ``None`` keys an unspecified credential.
    :param strict: When ``True``, building a new engine raises instead of isolating.
    :raises StrictEngineIsolationError: In strict mode, when this client's pair
        matches no engine already live for the account.
    """
    key = _canonicalize_endpoint(endpoint)
    engine = (credential_key, config)
    with _LOCK:
        live = _REGISTRY.get(key)
        if live is None:
            _REGISTRY[key] = {engine: 1}
            return
        if engine in live:
            live[engine] += 1
            return
        if strict:
            # Do NOT record: the client construction is about to fail, so it must not
            # count against the account (it will never call release_client_config).
            raise StrictEngineIsolationError(
                "Strict engine isolation is enabled and another CosmosClient is "
                "already active against {endpoint!r} with a different configuration "
                "or credential. The Rust backend (_backend='rust') would build a "
                "second, separate per-account engine to honor this client's settings "
                "(credential, preferred/excluded locations, consistency level, "
                "throttling, hedging, user-agent suffix). To proceed, give this client "
                "the same credential and configuration as an existing one, disable "
                "strict isolation (COSMOS_RUST_STRICT_ISOLATION), or build it in a "
                "separate process.".format(endpoint=endpoint)
            )
        live[engine] = 1


def release_client_config(
    endpoint: str,
    config: Optional[PreparedClientConfig] = None,
    credential_key: Any = None,
) -> None:
    """Drop one live client from its engine on ``endpoint``; forget the engine when
    its last client is released, and the account when its last engine is gone. Called
    by the python wrapper when a client is closed -- deterministically at ``close()``,
    not whenever the garbage collector runs.

    Releasing with the same ``config`` and ``credential_key`` the client registered
    keeps the counts accurate, so a later strict check sees only the engines still
    live. An unknown endpoint or engine, or an extra release, is a harmless no-op.
    """
    key = _canonicalize_endpoint(endpoint)
    engine = (credential_key, config)
    with _LOCK:
        live = _REGISTRY.get(key)
        if live is None:
            return
        count = live.get(engine)
        if count is None:
            return
        count -= 1
        if count <= 0:
            del live[engine]
            if not live:
                del _REGISTRY[key]
        else:
            live[engine] = count


def _live_client_count(endpoint: str) -> int:
    """Total live clients across every engine for ``endpoint`` (0 if none). Test- and
    diagnostics-facing; the strict decision uses the per-engine structure directly."""
    key = _canonicalize_endpoint(endpoint)
    with _LOCK:
        return sum(_REGISTRY.get(key, {}).values())


def _reset_for_tests() -> None:
    """Clear the registry. Tests use this to stay isolated from each other, since
    the registry lives for the whole process.
    """
    global _PROXY_POLICY, _PROXY_POLICY_SET  # pylint: disable=global-statement
    global _CONNECTION_TIMEOUT_POLICY  # pylint: disable=global-statement
    global _CONNECTION_TIMEOUT_POLICY_SET  # pylint: disable=global-statement
    global _READ_TIMEOUT_POLICY  # pylint: disable=global-statement
    global _READ_TIMEOUT_POLICY_SET  # pylint: disable=global-statement
    with _LOCK:
        _REGISTRY.clear()
        _PROXY_POLICY = None
        _PROXY_POLICY_SET = False
        _CONNECTION_TIMEOUT_POLICY = None
        _CONNECTION_TIMEOUT_POLICY_SET = False
        _READ_TIMEOUT_POLICY = None
        _READ_TIMEOUT_POLICY_SET = False
