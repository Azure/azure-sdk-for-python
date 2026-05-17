# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async sibling of ``azure.cosmos._helpers.item_helper.ItemHelper``.

The behaviour, parameter contract, dispatch rules, and option-build
sequence are byte-identical to the sync sibling. The option-build is
imported from the shared ``_item_dispatch`` module so the two siblings
cannot drift; what remains here is the per-call I/O wired up with
``await``.

Keeping the two as siblings rather than one mixed class follows the
pattern the rest of the SDK uses (``Container`` vs ``aio.Container``,
``CosmosClient`` vs ``aio.CosmosClient``).
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional

from ..._constants import _Constants as Constants
from ..._helpers._item_dispatch import build_create_item_request_options
from ..._helpers._request_prep import build_create_item_prepared
from ..._helpers._response_parse import parse_backend_response
from ...partition_key import _Empty
from .._backend.base import AsyncCosmosBackend


class AsyncItemHelper:
    """Async per-call orchestrator for ``Container.create_item``.

    See the sync sibling ``azure.cosmos._helpers.item_helper.ItemHelper``
    for the design rationale and the per-parameter docs.
    """

    def __init__(
        self,
        backend: Optional[AsyncCosmosBackend],
        client_connection: Any,
        ensure_container_cached: Optional[Callable[[Dict[str, Any]], Awaitable[Any]]] = None,
    ) -> None:
        """Bind the async helper to the chosen backend and the connection.

        :param backend: The async backend the wiring function picked
            for this client. ``None`` is permitted only for unit tests
            that build the helper without going through the async
            ``CosmosClient``.
        :type backend: Optional[AsyncCosmosBackend]
        :param client_connection: The async ``CosmosClientConnection``
            from ``azure.cosmos.aio``. The helper awaits its
            ``CreateItem`` and ``_refresh_container_properties_cache``.
        :type client_connection: Any
        :param ensure_container_cached: Optional async callable the
            container proxy passes in. See the sync sibling for the
            full rationale.
        :type ensure_container_cached: Optional[Callable]
        """
        self._backend = backend
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
        """Run a single async ``create_item`` call end to end."""

        # Snapshot kwargs before the legacy options build drains them — see
        # the sync sibling for the full rationale. Without this snapshot,
        # ``pre_trigger_include`` / ``no_response`` / ``priority`` / etc.
        # never reach the binding because ``_base.build_options`` pops
        # every recognized key out of the dict.
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_create_item_request_options(
            kwargs,
            enable_automatic_id_generation=enable_automatic_id_generation,
            indexing_directive=indexing_directive,
            populate_query_metrics=None,
        )

        # Container-rid lookup (best-effort; tolerates bare-mock
        # connections in unit tests). See sync sibling for rationale.
        container_rid: Optional[str] = None
        try:
            if self._ensure_container_cached is not None:
                await self._ensure_container_cached(request_options)
            else:
                cache = self.client_connection._container_properties_cache
                if container_link not in cache:
                    await self.client_connection._refresh_container_properties_cache(container_link)
            cached = self.client_connection._container_properties_cache[container_link]
            rid_value = cached.get("_rid") if isinstance(cached, dict) else None
            if isinstance(rid_value, str):
                container_rid = rid_value
                request_options[Constants.ContainerRID] = container_rid
        except Exception:  # pylint: disable=broad-except
            container_rid = None

        if self._backend is not None:
            partition_key_value = await self._extract_partition_key_value(
                container_link, body, request_options
            )
            prepared, _item_id = build_create_item_prepared(
                container_link=container_link,
                body=body,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                enable_automatic_id_generation=enable_automatic_id_generation,
                indexing_directive=indexing_directive,
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = await self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        return await self.client_connection.CreateItem(
            database_or_container_link=container_link,
            document=body,
            options=request_options,
            **kwargs,
        )

    async def _extract_partition_key_value(
        self,
        container_link: str,
        body: Dict[str, Any],
        request_options: Dict[str, Any],
    ) -> Any:
        """Async sibling of the sync helper's PK extraction. See sync docstring."""
        if "partitionKey" in request_options:
            return request_options["partitionKey"]
        try:
            new_options = await self.client_connection._AddPartitionKey(
                container_link, body, request_options
            )
            if isinstance(new_options, dict):
                request_options.update(new_options)
                return new_options.get("partitionKey", _Empty())
        except Exception:  # pylint: disable=broad-except
            pass
        return _Empty()

