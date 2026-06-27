# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Per-process guard for the Rust backend's per-account engine isolation.

The Rust binding keys its driver cache by ``(endpoint, credential, config)``: two
clients to one account share a driver only when their credential and config both
match. A client whose credential or config differs gets its own driver that honors
its settings, so a later client's settings are never silently dropped.

That isolation is safe but builds more drivers. Some callers would rather be told,
at construction, when their clients are about to build a second driver against one
account (for example a test that creates many slightly different clients). Strict
isolation mode is the opt-in for that: when on, a second live client to an account
whose config differs from the first client's raises
:class:`StrictEngineIsolationError`. Default mode allows it silently.

This module keeps a per-process count of live clients per endpoint plus the first
client's config, so the strict check can compare. It is plain Python and never calls
the binding, so it can be tested without a network.
"""
from __future__ import annotations

import threading
from typing import Dict, Optional, Tuple

from .base import PreparedClientConfig


class StrictEngineIsolationError(ValueError):
    """Raised under strict isolation mode when a later ``CosmosClient`` targets an
    account another live client already targets, with a *different* configuration,
    so honoring both would build a second per-account engine.

    This is opt-in: it fires only when strict isolation is enabled (the
    ``COSMOS_RUST_STRICT_ISOLATION`` environment variable or the factory toggle).
    In the default mode the second client is allowed and simply gets its own
    isolated engine, no error.
    """


# endpoint -> (configuration the first live client registered, number of live
# clients for this endpoint). Guarded by _LOCK. The count reaches zero only when
# every client to the endpoint has been released, after which a fresh client
# records its own config as the new "first".
_LOCK = threading.Lock()
_REGISTRY: Dict[str, Tuple[Optional[PreparedClientConfig], int]] = {}


def register_client_config(
    endpoint: str,
    config: Optional[PreparedClientConfig],
    strict: bool = False,
) -> None:
    """Record one live client against ``endpoint``.

    The first client to an account records its config and a count of 1 and fixes the
    config the strict check compares against. A later client adds to the count. If
    that later client's ``config`` differs from the first one's:

    * **strict** -- raise :class:`StrictEngineIsolationError` *without* recording, so
      the failed client never enters the count (it is not built, so it must not be
      released later) and the existing clients' count stays correct.
    * **default** -- record it and return; the binding gives it its own isolated
      engine, so nothing is dropped and there is nothing to warn about.

    ``PreparedClientConfig`` compares by value, and ``None`` (an untuned client)
    compares cleanly against a tuned config, so two untuned clients -- or two with
    equal settings -- never trip the strict check.

    :param endpoint: The account endpoint the client targets.
    :param config: The client's prepared config, or ``None`` when untuned.
    :param strict: When ``True``, a differing config raises instead of isolating.
    :raises StrictEngineIsolationError: In strict mode, when ``config`` differs from
        the first live client's config for this endpoint.
    """
    with _LOCK:
        existing = _REGISTRY.get(endpoint)
        if existing is None:
            _REGISTRY[endpoint] = (config, 1)
            return
        first_config, count = existing
        if strict and config != first_config:
            # Do NOT record: the client construction is about to fail, so it must not
            # count against the endpoint (it will never call release_client_config).
            raise StrictEngineIsolationError(
                "Strict engine isolation is enabled and another CosmosClient is "
                "already active against {endpoint!r} with a different configuration. "
                "The Rust backend (_backend='rust') would build a second, separate "
                "per-account engine to honor this client's settings (preferred/"
                "excluded locations, consistency level, throttling, hedging, "
                "user-agent suffix). To proceed, give this client the same "
                "configuration as the first, disable strict isolation "
                "(COSMOS_RUST_STRICT_ISOLATION), or build it in a separate "
                "process.".format(endpoint=endpoint)
            )
        _REGISTRY[endpoint] = (first_config, count + 1)


def release_client_config(endpoint: str) -> None:
    """Drop one live client from ``endpoint``; forget the endpoint when the last
    one is released.

    Once every client to an endpoint has closed, a new client to it starts fresh
    (records its own config, no warning). An unknown endpoint, or an extra
    release, is a harmless no-op.
    """
    with _LOCK:
        existing = _REGISTRY.get(endpoint)
        if existing is None:
            return
        first_config, count = existing
        count -= 1
        if count <= 0:
            del _REGISTRY[endpoint]
        else:
            _REGISTRY[endpoint] = (first_config, count)


def _reset_for_tests() -> None:
    """Clear the registry. Tests use this to stay isolated from each other, since
    the registry lives for the whole process.
    """
    with _LOCK:
        _REGISTRY.clear()

