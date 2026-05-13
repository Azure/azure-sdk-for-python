# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Per-client helper that runs every ``Container.create_item`` call.

``ItemHelper`` is the place where the backend dispatch and the
legacy request-prep logic used to live inside ``Container.create_item``
now both run. The container method is reduced to deprecation-warning
massaging plus moving its explicit kwargs into the ``kwargs`` dict, then
hands off to one ``ItemHelper.create_item`` call.

The dispatch decision and the request-options build are pure logic
shared with the async sibling via ``_item_dispatch``; this class only
adds the per-call I/O (call into the chosen backend, populate the
container cache, call legacy ``CreateItem``). The async sibling
``aio._helpers.item_helper.AsyncItemHelper`` mirrors this class with
``await`` in those three places.

Today the helper does not parse the response: it returns whatever the
legacy ``CreateItem`` returns. Once ``CorePythonBackend.create_item``
becomes a real adapter that takes a ``PreparedRequest`` and produces
a ``BackendResponse``, the response-parse helper takes over and the
``CreateItem`` fall-through goes away.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .._constants import _Constants as Constants
from ._item_dispatch import (
    build_create_item_request_options,
    choose_backend,
)


class ItemHelper:
    """Owns the per-call request-prep + dispatch for ``create_item``.

    One instance is constructed per ``Container.create_item`` invocation
    today (cheap; the only state is a reference to the
    ``CosmosClientConnection`` plus an optional cache-populate
    callback). Holding state on the helper buys nothing at this stage,
    but the class shape is the right home for future per-container
    caches once response parsing moves into the helper.
    """

    def __init__(
        self,
        client_connection: Any,
        ensure_container_cached: Optional[Callable[[Dict[str, Any]], Any]] = None,
    ) -> None:
        """Bind the helper to a specific client connection.

        :param client_connection: The
            ``CosmosClientConnection`` (or async sibling) the helper
            should use for backend dispatch lookups, the container-
            properties cache, and the legacy ``CreateItem`` call.
        :type client_connection: Any
        :param ensure_container_cached: Optional callable the
            container proxy passes in to perform the cache-populate
            step under the container's own lock and with proper
            forwarding of ``excluded_locations`` / timeout options
            from ``request_options`` into the cache-fetch call. When
            ``None`` (e.g. unit tests that build the helper without
            going through the container), the helper falls back to a
            best-effort direct call into
            ``client_connection._refresh_container_properties_cache``
            which does *not* forward those options.
        :type ensure_container_cached: Optional[Callable]
        """
        self.client_connection = client_connection
        self._ensure_container_cached = ensure_container_cached

    def create_item(
        self,
        *,
        container_link: str,
        body: Dict[str, Any],
        populate_query_metrics: Optional[bool] = None,
        indexing_directive: Optional[int] = None,
        enable_automatic_id_generation: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Run a single ``create_item`` call end to end.

        :param container_link: Self-link of the container, e.g.
            ``"dbs/{db}/colls/{coll}"``.
        :type container_link: str
        :param body: The Cosmos document to create. Forwarded to
            ``CreateItem`` as the ``document`` parameter; not mutated.
        :type body: Dict[str, Any]
        :param populate_query_metrics: Mirrors the legacy explicit arg.
            When truthy, emits the existing deprecation warning and
            still writes the option key.
        :type populate_query_metrics: Optional[bool]
        :param indexing_directive: Mirrors the legacy explicit arg.
        :type indexing_directive: Optional[int]
        :param enable_automatic_id_generation: Mirrors the legacy
            explicit arg.
        :type enable_automatic_id_generation: bool
        :param kwargs: Every other customer kwarg the container
            received. Used for the dispatch decision and forwarded to
            ``CreateItem`` after option extraction.
        :returns: Whatever the chosen backend / legacy ``CreateItem``
            call returned.
        :rtype: Any
        """
        # Backend dispatch — shared logic, sync side.
        backend = choose_backend(self.client_connection, kwargs)
        if backend is not None:
            backend_response = backend.create_item(prepared=None)
            if backend_response is not None:
                # Real BackendResponse from a wired adapter — return it
                # directly. Today only happens if a test mocks
                # core-python to return non-None.
                return backend_response  # pragma: no cover

        request_options = build_create_item_request_options(
            kwargs,
            enable_automatic_id_generation=enable_automatic_id_generation,
            indexing_directive=indexing_directive,
            populate_query_metrics=populate_query_metrics,
        )

        # Container-rid stamping. The container proxy supplies a
        # callback (``_get_properties_with_options``) that takes the
        # container's lock and forwards excluded_locations / timeout
        # options into the cache fetch. The fallback path exists
        # only for test seams that build the helper without a proxy
        # and is not safe under concurrent use.
        if self._ensure_container_cached is not None:
            self._ensure_container_cached(request_options)
        else:
            cache = self.client_connection._container_properties_cache
            if container_link not in cache:
                self.client_connection._refresh_container_properties_cache(container_link)
        request_options[Constants.ContainerRID] = (
            self.client_connection._container_properties_cache[container_link]["_rid"]
        )

        return self.client_connection.CreateItem(
            database_or_container_link=container_link,
            document=body,
            options=request_options,
            **kwargs,
        )

