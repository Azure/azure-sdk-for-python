# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Per-client helper that runs every ``Container.create_item`` /
``Container.read_item`` / ``Container.delete_item`` /
``Container.upsert_item`` call.

``ItemHelper`` is where backend dispatch and the request-prep logic
(previously inlined in the container methods) live. The container
methods just stamp their explicit kwargs into ``kwargs`` and hand off
to one ``ItemHelper.create_item`` / ``ItemHelper.read_item`` /
``ItemHelper.delete_item`` / ``ItemHelper.upsert_item`` call.

Flow (same shape for all three ops):

1. Build the legacy-shape ``request_options`` via the matching
   ``build_*_request_options`` helper.
2. Look up (or refresh) the container's ``_rid`` from the
   container-properties cache.
3. If a backend (today: ``RustBackend``) is wired, build a
   ``PreparedRequest``, call ``backend.execute``, parse the returned
   ``BackendResponse`` into a ``CosmosDict`` (raising the typed
   exception for non-2xx).
4. When no backend is wired, fall through to the legacy
   ``client_connection.CreateItem`` / ``.ReadItem`` / ``.DeleteItem``
   path.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .._backend.base import CosmosBackend
from .._constants import _Constants as Constants
from ..partition_key import _Empty
from ._item_dispatch import (
    build_create_item_request_options,
    build_delete_item_request_options,
    build_read_item_request_options,
    build_upsert_item_request_options,
)
from ._request_prep import (
    build_create_item_prepared,
    build_delete_item_prepared,
    build_read_item_prepared,
    build_replace_item_prepared,
    build_upsert_item_prepared,
)
from ._response_parse import parse_backend_response


class ItemHelper:
    """Per-call request-prep + dispatch for ``create_item``,
    ``read_item``, and ``delete_item``.

    Cheap to construct (only holds references). One instance per
    container-method invocation today.
    """

    def __init__(
        self,
        backend: Optional[CosmosBackend],
        client_connection: Any,
        ensure_container_cached: Optional[Callable[[Dict[str, Any]], Any]] = None,
    ) -> None:
        """Bind the helper to the chosen backend and the client connection.

        :param backend: The backend wired for this client, or ``None``
            for the legacy / bare-mock case.
        :type backend: Optional[CosmosBackend]
        :param client_connection: The ``CosmosClientConnection`` (or
            async sibling) used for the cache, PK extraction, and
            legacy fall-through.
        :type client_connection: Any
        :param ensure_container_cached: Optional callable supplied by
            the container proxy to perform the cache-populate step
            under the container's lock with proper option forwarding.
        :type ensure_container_cached: Optional[Callable]
        """
        self._backend = backend
        self.client_connection = client_connection
        self._ensure_container_cached = ensure_container_cached

    def _resolve_container_rid(
        self,
        container_link: str,
        request_options: Dict[str, Any],
    ) -> Optional[str]:
        """Look up the container ``_rid`` and stamp it into request_options.

        Shared by all five ops. Best-effort: bare-mock connections in unit
        tests may not produce a real rid, so on any failure we return
        ``None`` and let the backend run without the
        intended-collection-rid header. On success the rid is written to
        ``request_options`` (under ``Constants.ContainerRID``) and returned
        for the prepared-request build.
        """
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
                request_options[Constants.ContainerRID] = rid_value
                return rid_value
        except Exception:  # pylint: disable=broad-except
            pass
        return None

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

        # Snapshot kwargs before the legacy options build pops them.
        # The rust prep still needs the originals to populate the
        # PreparedRequest.headers map.
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_create_item_request_options(
            kwargs,
            enable_automatic_id_generation=enable_automatic_id_generation,
            indexing_directive=indexing_directive,
            populate_query_metrics=populate_query_metrics,
        )

        container_rid = self._resolve_container_rid(container_link, request_options)

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
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        # Fall-through: legacy path.
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
        """Pull the partition-key value to put on the wire.

        Precedence (matches the legacy private path):

        1. ``request_options["partitionKey"]`` if the caller set it.
        2. Extracted from ``body`` using the container's PK definition.
        3. ``_Empty()`` fallback for bare-mock connections that have
           no PK-extraction method.
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

    def delete_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        **kwargs: Any,
    ) -> Any:
        """Run a single ``delete_item`` call end to end.

        :param container_link: Container self-link.
        :param document_link: The ``dbs/.../docs/<id-or-rid>`` link the
            legacy ``DeleteItem`` consumes. Built by the caller.
        :param item_id: The document id the binding writes onto
            ``PreparedRequest.item_id``.
        :param kwargs: Caller's remaining kwargs. The caller has
            already stamped ``partitionKey`` into ``request_options``.
        """
        # Snapshot kwargs before the legacy options build pops them.
        # The rust prep still needs the originals to populate the
        # PreparedRequest.headers map.
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_delete_item_request_options(kwargs)

        # The caller stamped the PK into request_options before
        # getting here, so the rust prep can use it directly.
        partition_key_value = request_options.get("partitionKey", _Empty())

        container_rid = self._resolve_container_rid(container_link, request_options)

        if self._backend is not None:
            prepared = build_delete_item_prepared(
                container_link=container_link,
                item_id=item_id,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = self._backend.execute(prepared)
            if backend_response is not None:
                # Delete returns 204 with an empty body. Invoke the
                # response_hook so callers can observe response
                # headers; return None because the public delete_item
                # is typed -> None.
                parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )
                return None

        # Fall-through: legacy path.
        return self.client_connection.DeleteItem(
            document_link=document_link,
            options=request_options,
            **kwargs,
        )

    def read_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        **kwargs: Any,
    ) -> Any:
        """Run a single ``read_item`` call end to end.

        Same shape as ``delete_item`` (kwarg snapshot, legacy options
        build, container-rid cache lookup, backend dispatch with legacy
        fall-through). Returns the ``CosmosDict`` the response parser
        produces: a body for 200, an empty dict for 304 (a conditional
        ``If-None-Match`` read whose etag matched).

        :param container_link: Container self-link.
        :param document_link: The ``dbs/.../docs/<id-or-rid>`` link the
            legacy ``ReadItem`` consumes. Built by the caller.
        :param item_id: The document id the binding writes onto
            ``PreparedRequest.item_id``.
        :param kwargs: Caller's remaining kwargs. The caller has
            already stamped ``partitionKey`` into ``request_options``.
        """
        # Snapshot kwargs before the legacy options build pops them.
        # The rust prep still needs the originals to populate the
        # PreparedRequest.headers map.
        kwargs_for_rust_prep = dict(kwargs)

        # build_read_item_request_options runs the legacy match-headers
        # check; that is where ValueError("'etag' specified without
        # 'match_condition'.") (and the inverse) fires, on the
        # caller's frame, before any network call.
        request_options = build_read_item_request_options(kwargs)

        # The caller stamped the PK into request_options before
        # getting here.
        partition_key_value = request_options.get("partitionKey", _Empty())

        container_rid = self._resolve_container_rid(container_link, request_options)

        if self._backend is not None:
            prepared = build_read_item_prepared(
                container_link=container_link,
                item_id=item_id,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = self._backend.execute(prepared)
            if backend_response is not None:
                # 200 returns the parsed body; 304 returns an empty
                # CosmosDict with response headers carrying the current
                # etag. The parser fires response_hook once on either.
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        # Fall-through: legacy path.
        return self.client_connection.ReadItem(
            document_link=document_link,
            options=request_options,
            **kwargs,
        )

    def upsert_item(
        self,
        *,
        container_link: str,
        body: Dict[str, Any],
        populate_query_metrics: Optional[bool] = None,
        **kwargs: Any,
    ) -> Any:
        """Run a single ``upsert_item`` call end to end.

        Write-with-body like ``create_item`` -- the partition key is
        extracted from the body and the body is serialised to JSON --
        but with two upsert differences: it honours ``etag`` /
        ``match_condition`` (passed through to the prep as an access
        condition, the same wire headers ``delete_item`` emits) and it
        never mints an id. The legacy build sets
        ``disableAutomaticIdGeneration`` so the fall-through path matches.

        The rust backend dispatches this op to the binding's
        ``upsert_item`` entry point (an existing item is replaced rather
        than rejected as a duplicate), so a wired backend returns a
        ``BackendResponse`` that is parsed into a ``CosmosDict``. When no
        backend is wired (the core-python client) ``execute`` returns
        ``None`` and the call falls through to the legacy ``UpsertItem``
        below.
        """
        # Snapshot kwargs before the legacy options build pops them. The
        # rust prep still needs the originals to populate the
        # PreparedRequest.headers map.
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_upsert_item_request_options(
            kwargs,
            populate_query_metrics=populate_query_metrics,
        )

        container_rid = self._resolve_container_rid(container_link, request_options)

        if self._backend is not None:
            partition_key_value = self._extract_partition_key_value(
                container_link, body, request_options
            )
            prepared = build_upsert_item_prepared(
                container_link=container_link,
                body=body,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                access_condition=request_options.get("accessCondition"),
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        # Fall-through: legacy path.
        return self.client_connection.UpsertItem(
            database_or_container_link=container_link,
            document=body,
            options=request_options,
            **kwargs,
        )

    def replace_item(
        self,
        *,
        container_link: str,
        document_link: str,
        item_id: str,
        body: Dict[str, Any],
        populate_query_metrics: Optional[bool] = None,
        **kwargs: Any,
    ) -> Any:
        """Run a single ``replace_item`` call end to end.

        Overwrite-only write-with-body. Like ``upsert_item`` the partition
        key is extracted from the body, the body is serialised to JSON, no
        id is minted, and ``etag`` / ``match_condition`` become an
        ``If-Match`` / ``If-None-Match`` precondition (the version-guarded
        replace is the dominant case). The options build is byte-identical
        to upsert's, so ``build_upsert_item_request_options`` is reused
        rather than duplicated -- it sets ``disableAutomaticIdGeneration``
        and threads the deprecated ``populate_query_metrics`` flag, so the
        fall-through path matches the legacy ``replace_item`` exactly.

        Unlike upsert, replace names an existing document. ``item_id`` (the
        id resolved from the ``item`` argument) is what the binding puts in
        the wire URL -- not the body's own id -- matching the legacy
        ``ReplaceItem``. The rust backend dispatches this op to the binding's
        ``replace_item`` entry point (driver ``OperationType::Replace``, an
        overwrite-only PUT). When no backend is wired (the core-python
        client) ``execute`` returns ``None`` and the call falls through to
        the legacy ``ReplaceItem`` below.

        :param container_link: Container self-link.
        :param document_link: The ``dbs/.../docs/<id-or-rid>`` link the
            legacy ``ReplaceItem`` consumes. Built by the caller from the
            ``item`` argument (an id string or a document dict).
        :param item_id: The id of the document to overwrite, resolved from
            ``item``. Carried on the prepared request for the binding's URL.
        :param body: The replacement document.
        :param populate_query_metrics: Deprecated sync-only flag; the
            reused options build warns and writes it. The async sibling
            passes ``None``.
        """
        # Snapshot kwargs before the legacy options build pops them. The
        # rust prep still needs the originals to populate the
        # PreparedRequest.headers map.
        kwargs_for_rust_prep = dict(kwargs)

        request_options = build_upsert_item_request_options(
            kwargs,
            populate_query_metrics=populate_query_metrics,
        )

        container_rid = self._resolve_container_rid(container_link, request_options)

        if self._backend is not None:
            partition_key_value = self._extract_partition_key_value(
                container_link, body, request_options
            )
            prepared = build_replace_item_prepared(
                container_link=container_link,
                body=body,
                item_id=item_id,
                partition_key_value=partition_key_value,
                container_rid=container_rid,
                access_condition=request_options.get("accessCondition"),
                kwargs=kwargs_for_rust_prep,
            )
            backend_response = self._backend.execute(prepared)
            if backend_response is not None:
                return parse_backend_response(
                    backend_response,
                    client_connection=self.client_connection,
                    response_hook=kwargs.get("response_hook"),
                )

        # Fall-through: legacy path.
        return self.client_connection.ReplaceItem(
            document_link=document_link,
            new_document=body,
            options=request_options,
            **kwargs,
        )

