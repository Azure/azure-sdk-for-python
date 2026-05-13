# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async sibling of ``azure.cosmos._helpers.item_helper.ItemHelper``.

The behaviour, parameter contract, dispatch rules, and option-build
sequence are byte-identical to the sync sibling. The dispatch
decision and the option-build are imported from the shared
``_item_dispatch`` module so the two siblings cannot drift; what
remains here is the per-call I/O wired up with ``await``.

Keeping the two as siblings rather than one mixed class follows the
pattern the rest of the SDK uses (``Container`` vs ``aio.Container``,
``CosmosClient`` vs ``aio.CosmosClient``).
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional

from ..._constants import _Constants as Constants
from ..._helpers._item_dispatch import (
    build_create_item_request_options,
    choose_backend,
)


class AsyncItemHelper:
    """Async per-call orchestrator for ``Container.create_item``.

    See the sync sibling ``azure.cosmos._helpers.item_helper.ItemHelper``
    for the design rationale and the per-parameter docs. Only the
    async-specific I/O lives here; everything else is delegated to the
    shared ``_item_dispatch`` helpers.
    """

    def __init__(
        self,
        client_connection: Any,
        ensure_container_cached: Optional[Callable[[Dict[str, Any]], Awaitable[Any]]] = None,
    ) -> None:
        """Bind the async helper to a specific async client connection.

        :param client_connection: The async
            ``CosmosClientConnection`` from ``azure.cosmos.aio``. The
            helper awaits its ``CreateItem`` and
            ``_refresh_container_properties_cache``.
        :type client_connection: Any
        :param ensure_container_cached: Optional async callable the
            container proxy passes in. See the sync sibling for the
            full rationale. When ``None`` the helper falls back to
            calling ``_refresh_container_properties_cache`` directly,
            which does not forward per-call options into the cache
            fetch and is not safe under concurrent use.
        :type ensure_container_cached: Optional[Callable]
        """
        self.client_connection = client_connection
        self._ensure_container_cached = ensure_container_cached

    async def create_item(
        self,
        *,
        container_link: str,
        body: Dict[str, Any],
        indexing_directive: Optional[int] = None,
        enable_automatic_id_generation: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Run a single async ``create_item`` call end to end.

        Parameter semantics match the sync sibling. The async
        container method does not expose ``populate_query_metrics``,
        so this helper does not accept it either.
        """
        # Backend dispatch — shared logic, async side just awaits.
        backend = choose_backend(self.client_connection, kwargs)
        if backend is not None:
            backend_response = await backend.create_item(prepared=None)
            if backend_response is not None:
                return backend_response  # pragma: no cover

        request_options = build_create_item_request_options(
            kwargs,
            enable_automatic_id_generation=enable_automatic_id_generation,
            indexing_directive=indexing_directive,
            populate_query_metrics=None,
        )

        # Container-rid stamping. See sync sibling for the rationale
        # behind the callback indirection.
        if self._ensure_container_cached is not None:
            await self._ensure_container_cached(request_options)
        else:
            cache = self.client_connection._container_properties_cache
            if container_link not in cache:
                await self.client_connection._refresh_container_properties_cache(container_link)
        request_options[Constants.ContainerRID] = (
            self.client_connection._container_properties_cache[container_link]["_rid"]
        )

        return await self.client_connection.CreateItem(
            database_or_container_link=container_link,
            document=body,
            options=request_options,
            **kwargs,
        )

