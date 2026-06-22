# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Make the Rust backend's per-account engine sharing visible.

The Rust driver builds one engine per account endpoint and reuses it: the first
``CosmosClient`` to an endpoint wins, and a later client to the same endpoint
inherits that engine and its configuration, so the later client's own settings
(preferred/excluded locations, consistency, throttling, hedging, user-agent
suffix) are silently dropped.

That sharing is intentional, but the silent drop can mislead -- for example a
failover test that builds a second client pinned to another region is really
reusing the first client's region. This module keeps a small per-process count
of live clients per endpoint, and when a second live client targets an endpoint
with a different configuration, it warns. The sharing still happens; it is just
no longer invisible. The registry is plain Python and never calls the binding,
so it can be tested without a network.
"""
from __future__ import annotations

import threading
import warnings
from typing import Dict, Optional, Tuple

from .base import PreparedClientConfig


class SharedDriverConfigWarning(UserWarning):
    """A later ``CosmosClient`` targets an account another client already targets,
    with a different configuration, so the shared per-account engine ignores the
    later client's settings.

    This is a warning, not an error: building two clients to one account is fine,
    and same-configuration clients share the engine harmlessly. It fires only when
    the configurations differ.
    """


# endpoint -> (configuration the first live client registered, number of live
# clients for this endpoint). Guarded by _LOCK. The count reaches zero only when
# every client to the endpoint has been released, after which a fresh client
# builds a new engine with its own config and must not warn.
_LOCK = threading.Lock()
_REGISTRY: Dict[str, Tuple[Optional[PreparedClientConfig], int]] = {}


def register_client_config(
    endpoint: str, config: Optional[PreparedClientConfig]
) -> None:
    """Record one live client against ``endpoint``; warn if its config differs
    from the one already in effect.

    The first client records its config and a count of 1. A later client adds to
    the count and, if its ``config`` differs from the recorded one, warns -- the
    recorded config is what the shared engine uses, so the later client's settings
    are the ones dropped. ``PreparedClientConfig`` compares by value, and ``None``
    (an untuned client) compares cleanly against a tuned config.
    """
    with _LOCK:
        existing = _REGISTRY.get(endpoint)
        if existing is None:
            _REGISTRY[endpoint] = (config, 1)
            return
        first_config, count = existing
        _REGISTRY[endpoint] = (first_config, count + 1)
        differs = config != first_config
    if differs:
        warnings.warn(
            "Another CosmosClient is already active against {endpoint!r}. The "
            "Rust backend (_backend='rust') builds one shared engine per account, "
            "so whichever client issues its first request first wins and the "
            "other's client-construction settings (preferred/excluded locations, "
            "consistency level, throttling, hedging, user-agent suffix) are "
            "ignored. To use distinct per-client settings against the same "
            "account, use separate processes, or the core-python backend.".format(
                endpoint=endpoint
            ),
            SharedDriverConfigWarning,
            stacklevel=2,
        )


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

