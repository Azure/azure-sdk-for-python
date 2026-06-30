# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Per-process guard, in the python wrapper, for the Rust backend's per-account
engine isolation.


The 50,000-foot view -- this module is a *detector, not a fixer*. It has no effect on
how engines are actually created or freed; that all lives in the binding. So if this
module did not exist:

* **Nothing functional would change.** The binding still shares one engine when
  endpoint+credential+config match and still forks a separate engine when they differ;
  its per-engine refcount, lazy build on first op, and teardown are untouched.
  Connection pools, memory, latency, and correctness in default use are identical --
  default mode never reads this module's data.
* **The only thing lost is strict isolation mode** -- the opt-in early warning. Without
  it there is no way to detect, at construction, that a client is about to make the
  binding build a *second* engine for an account that already has one. Teams that want
  a "one engine per account" guarantee would get no early signal: accidental engine
  fan-out (a loop of slightly different clients, or two clients with different
  credentials/configs to one account) proceeds silently and is discovered only later,
  indirectly, via the symptoms it was meant to pre-empt -- climbing connections, file
  descriptors, and memory in production.

In one line: without this module nothing breaks and nothing leaks that was not already
possible -- you only lose the opt-in early warning that turns silent engine fan-out
into a loud, fail-fast error at construction time.

The problem it guards against: the binding shares one engine between two clients only
when their endpoint, credential, *and* config all match; differ on any one and it
builds a *second* engine for the same account. That is safe (no settings are dropped)
but a loop or service that opens many slightly different clients can quietly
accumulate many engines for one account -- more connections and memory than expected,
usually noticed only later in production.

This guard runs in the real workflow: ``_shared.py`` calls it on every client open and
close. Strict isolation mode is an opt-in that puts it to work. When on, a later client
that would build a new engine for an account that already has one raises
``StrictEngineIsolationError`` at construction. By default the second engine is allowed
silently and the guard only keeps bookkeeping -- its behavior matters only when strict
mode is enabled (a service or CI that means to reuse one engine).

To decide correctly the guard mirrors the binding's cache key. For each account it
tracks the live engines -- one entry per distinct ``(credential, config)`` pair, with
a count of how many clients hold it -- so a later client is allowed when its pair
matches one still live and flagged when it would build a new one. Three details keep
the mirror faithful:

* The credential is part of the key, because the binding forks an engine on a
  credential difference too.
* The endpoint is canonicalized, so ``https://acct...com`` and
  ``https://acct...com/`` (and host-case variants) land in the same bucket.
* No secret is retained: a master key is reduced to a non-reversible fingerprint
  before it is used as a key, and a token credential is keyed by object identity.

Three independent counts exist; (1) Python's own object refcount
frees Python objects and knows nothing about engines. (2) This module's count is the
opt-in guard -- it runs at client open/close, in the python wrapper, before and
independently of the binding. (3) The binding's per-engine refcount governs the real
engine's lifetime and is built lazily: ``rust.py`` calls the binding's ``init_client``
only on the first item operation, not at client construction.

This module is **not** part of the binding's cache. It is a separate ledger in the
python wrapper that *mirrors* the binding's cache key so it can predict, at client
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


# Canonical endpoint -> the live engines for that account. Each key is a
# ``(credential_key, config)`` pair -- one engine (a rust driver the binding would
# build and cache) -- mapped to the number of live clients holding it. An account drops
# out only when its last engine's last client is released. Guarded by _LOCK. This is the
# python wrapper's own count, separate from the binding's per-engine refcount.
_LOCK = threading.Lock()
_REGISTRY: Dict[str, Dict[Tuple[Any, Optional[PreparedClientConfig]], int]] = {}


def _canonicalize_endpoint(endpoint: str) -> str:
    """Normalize an account endpoint so trivial URL variants of the same account
    share one registry bucket.

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
    object identity (``id``), which equals the raw pointer the binding fingerprints
    (``as_ptr``); the client holds a strong reference for its whole life, so that
    identity is stable while it is registered. A master key is reduced to a
    non-reversible fingerprint, so this module never keeps the plaintext secret --
    equal keys fingerprint equal, different keys do not. Both ``None`` keys as ``None``.
    """
    if token_credential is not None:
        return id(token_credential)
    if master_key is not None:
        return "mk:" + hashlib.sha256(master_key.encode("utf-8")).hexdigest()
    return None


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
    same credential -- share one engine and never trip the strict check.

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
    with _LOCK:
        _REGISTRY.clear()
