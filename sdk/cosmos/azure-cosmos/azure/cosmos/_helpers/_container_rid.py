# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Stamp the ``x-ms-cosmos-intended-collection-rid`` value into request options.

The rid (resource id) is the immutable internal identifier Cosmos
assigns when a container is created. The Cosmos service uses the
``x-ms-cosmos-intended-collection-rid`` header to detect a specific
failure mode:

* The customer's deploy pipeline drops and recreates a container with
  the same name (e.g. ``orders2026``). Same name, *different* rid.
* The SDK still has the old rid cached.
* The next request lands at the recreated (empty) container without the
  SDK noticing.
* The next read for an item the customer wrote moments ago returns 404.

When the SDK sends the rid it knew on the request, the service notices
the mismatch, the SDK quietly refreshes its caches, and retries. Drop
the header and that retry never fires; the request silently goes to the
wrong container and an item appears to "vanish."

This helper is the one place that stamps the option-dict key
``Constants.ContainerRID`` (which maps to the
``x-ms-cosmos-intended-collection-rid`` HTTP header inside
``_base.GetHeaders``). Putting it in one helper guarantees the
core-python and rust paths produce the same wire header for the same
container.
"""
from __future__ import annotations

from typing import Any, Callable, Dict

from .._constants import _Constants as Constants


def stamp_container_rid(
    options: Dict[str, Any],
    container_link: str,
    *,
    get_rid: Callable[[str], str],
) -> None:
    """Write ``x-ms-cosmos-intended-collection-rid`` into ``options`` if absent.

    The function is idempotent: if a caller has already set
    ``Constants.ContainerRID`` (test fixture, replay scenario, manual
    pre-build), the existing value is preserved. The legacy
    ``Container.create_item`` always overwrote — which is a small
    inconsistency with ``scripts._ensure_container_rid`` (which skips
    if set). This helper picks the defensive form. Callers that want
    the old "always overwrite" behaviour should set the option key
    themselves after calling this helper, but no current call site
    actually relies on overwriting.

    :param options: The internal options dict the request will use.
        Mutated in place — the only side effect.
    :type options: Dict[str, Any]
    :param container_link: Self-link of the container, e.g.
        ``"dbs/{db}/colls/{coll}"``. Passed straight to ``get_rid``;
        the helper does not interpret it.
    :type container_link: str
    :param get_rid: Callable invoked with ``container_link`` to retrieve
        the rid string. Inversion of control so the helper has zero
        knowledge of the container-properties cache, the
        ``CosmosClientConnection``, or how a cache miss is handled.
        The caller composes the closure with whatever cache /
        refresh policy applies (see the legacy
        ``scripts._ensure_container_rid`` for the typical shape).
    :type get_rid: Callable[[str], str]
    :returns: ``None``. The function mutates ``options`` and returns
        nothing.
    :rtype: None
    """
    # Idempotent: a pre-set rid is the caller's call to keep.
    if Constants.ContainerRID in options:
        return

    # ``get_rid`` may raise (cache miss + refresh failure, network
    # blip, etc.). Letting it propagate is intentional — the request
    # cannot proceed without a rid, and a half-stamped options dict
    # would be worse than a clean failure. We deliberately do not
    # write a sentinel value on failure.
    options[Constants.ContainerRID] = get_rid(container_link)
