# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Stamp the ``x-ms-cosmos-intended-collection-rid`` value into request options.

The rid is the internal id Cosmos assigns when a container is created.
The service uses the ``x-ms-cosmos-intended-collection-rid`` header to
detect a container that was dropped and recreated with the same name:
when the SDK's cached rid does not match the live rid the service
returns a typed error so the SDK can refresh and retry, rather than
silently writing to the wrong container.

This helper centralises stamping ``Constants.ContainerRID`` so both
backends produce the same value.
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

    Idempotent: if the caller has already set ``Constants.ContainerRID``,
    the existing value is preserved.

    :param options: The internal options dict. Mutated in place.
    :type options: Dict[str, Any]
    :param container_link: Container self-link, e.g.
        ``"dbs/{db}/colls/{coll}"``. Passed through to ``get_rid``.
    :type container_link: str
    :param get_rid: Callable that returns the rid for ``container_link``.
        Inversion of control so this helper does not depend on the
        container-properties cache or the client connection. Any
        exception it raises propagates.
    :type get_rid: Callable[[str], str]
    :rtype: None
    """
    if Constants.ContainerRID in options:
        return
    options[Constants.ContainerRID] = get_rid(container_link)
