# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Per-client helper that runs every ``Container.create_item`` call.

``ItemHelper`` is the place where the backend dispatch and the request-prep
logic that used to live inline in ``Container.create_item`` now both run.
The container method is reduced to deprecation-warning massaging plus
moving its explicit kwargs into the ``kwargs`` dict, then hands off to one
``ItemHelper.create_item`` call.

Flow per call:

  1. Stamp the chosen backend's name into ``kwargs`` so the user-agent
     policy can append ``backend=<name>`` to the outgoing request.
  2. Look up (or refresh) the container-properties cache so we have the
     container's ``_rid`` for stamping into headers.
  3. Build a ``PreparedRequest`` via ``build_create_item_prepared``
     (id minted, partition-key serialized, body bytes, headers).
  4. Hand the ``PreparedRequest`` to the backend's ``execute``.
     - ``RustBackend.execute(prepared)`` calls the PyO3 binding and
       returns a real ``BackendResponse``.
     - ``CorePythonBackend.execute(prepared)`` returns ``None`` today
       — signal to fall through to the legacy ``CreateItem`` path.
  5. When a real ``BackendResponse`` comes back, parse it via
     ``parse_backend_response`` into a ``CosmosDict`` and raise typed
     exceptions for non-2xx replies — same shape customer code has
     always seen.
  6. When the backend signals fall-through, run the legacy
     ``client_connection.CreateItem`` path verbatim.

The container constructs the helper with the backend it wants used for
this call (which the wiring function picked once at client construction
and stored on the connection). The helper itself never has to know which
backend it has — it just calls ``execute`` on it.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .._backend.base import CosmosBackend
from .._backend.constants import REQUEST_OPTION_BACKEND_KEY
from .._constants import _Constants as Constants
from ..partition_key import _Empty
from ._item_dispatch import build_create_item_request_options
from ._request_prep import build_create_item_prepared
from ._response_parse import parse_backend_response


class ItemHelper:
    """Owns the per-call request-prep + dispatch for ``create_item``.

    One instance is constructed per ``Container.create_item`` invocation
    today (cheap; the only state is the chosen backend, a reference to
    the ``CosmosClientConnection``, and an optional cache-populate
    callback).
    """

    def __init__(
        self,
        backend: Optional[CosmosBackend],
        client_connection: Any,
        ensure_container_cached: Optional[Callable[[Dict[str, Any]], Any]] = None,
    ) -> None:
        """Bind the helper to the chosen backend and the client connection.

        :param backend: The backend the wiring function picked for this
            client. ``None`` is permitted only for unit tests that
            build the helper without going through ``CosmosClient``;
            in that case dispatch is skipped and the legacy path runs
            directly.
        :type backend: Optional[CosmosBackend]
        :param client_connection: The ``CosmosClientConnection`` (or
            async sibling) the helper uses for the container-properties
            cache, partition-key extraction, and the legacy
            ``CreateItem`` fall-through.
        :type client_connection: Any
        :param ensure_container_cached: Optional callable the
            container proxy passes in to perform the cache-populate
            step under the container's own lock and with proper
            forwarding of ``excluded_locations`` / timeout options
            from ``request_options`` into the cache-fetch call.
        :type ensure_container_cached: Optional[Callable]
        """
        self._backend = backend
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
        """Run a single ``create_item`` call end to end."""
        if self._backend is not None:
            # Stamp the chosen backend's name so the user-agent policy
            # can append ``backend=<name>`` to the outgoing request.
            kwargs[REQUEST_OPTION_BACKEND_KEY] = self._backend.name

        # Build legacy-shape request_options (used by the fall-through
        # legacy path AND consumed for partition-key extraction below).
        request_options = build_create_item_request_options(
            kwargs,
            enable_automatic_id_generation=enable_automatic_id_generation,
            indexing_directive=indexing_directive,
            populate_query_metrics=populate_query_metrics,
        )

        # Container-rid lookup. Best effort: when the connection is a
        # bare mock (some unit tests), the cache lookup may not produce
        # a real string. We catch and continue with rid=None so that
        # ``backend.execute`` still gets called — the dispatch contract
        # is "stamp the rid when we have one, fall through gracefully
        # when we don't."
        container_rid: Optional[str] = None
        try:
            if self._ensure_container_cached is not None:
                self._ensure_container_cached(request_options)
            else:
                cache = self.client_connection._container_properties_cache
                if container_link not in cache:
                    self.client_connection._refresh_container_properties_cache(container_link)
            cached = self.client_connection._container_properties_cache[container_link]
            rid_value = cached.get("_rid") if isinstance(cached, dict) else None
            if isinstance(rid_value, str):
                container_rid = rid_value
                request_options[Constants.ContainerRID] = container_rid
        except Exception:  # pylint: disable=broad-except
            container_rid = None

        # Backend dispatch path. Build the PreparedRequest, hand it to
        # ``backend.execute``. The CorePythonBackend's execute returns
        # ``None`` today (placeholder); the RustBackend returns a real
        # BackendResponse.
        if self._backend is not None:
            partition_key_value = self._extract_partition_key_value(
                container_link, body, request_options
            )
            prepared, _item_id = build_create_item_prepared(
                container_link=container_link,
                body=body,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                enable_automatic_id_generation=enable_automatic_id_generation,
                indexing_directive=indexing_directive,
                kwargs=dict(kwargs),
            )
            backend_response = self._backend.execute(prepared)
            if backend_response is not None:
                # Real BackendResponse from a wired adapter (today: Rust).
                # Parse into v4-shaped CosmosDict, raise typed exceptions
                # for non-2xx, fire response_hook on success.
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        # Fall through: core-python backend (or no backend at all in
        # bare-mock unit tests) → run the legacy in-place CreateItem.
        return self.client_connection.CreateItem(
            database_or_container_link=container_link,
            document=body,
            options=request_options,
            **kwargs,
        )

    def _extract_partition_key_value(
        self,
        container_link: str,
        body: Dict[str, Any],
        request_options: Dict[str, Any],
    ) -> Any:
        """Pull the partition-key value the helper should put on the wire.

        Precedence (matches legacy ``_AddPartitionKey``):
          1. ``request_options["partitionKey"]`` if the caller already set it.
          2. Extracted from ``body`` using the container's PK definition.
          3. ``_Empty()`` fallback when neither path is reachable (bare
             mock connections in unit tests). The fallback never reaches
             production because real connections always have an
             ``_AddPartitionKey`` method.
        """
        if "partitionKey" in request_options:
            return request_options["partitionKey"]
        try:
            new_options = self.client_connection._AddPartitionKey(
                container_link, body, request_options
            )
            if isinstance(new_options, dict):
                request_options.update(new_options)
                return new_options.get("partitionKey", _Empty())
        except Exception:  # pylint: disable=broad-except
            pass
        return _Empty()

