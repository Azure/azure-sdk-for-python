# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Provide the two container facts the backend's request prep needs.

The backend needs two facts about a container that are not in the document or
the call's kwargs: its internal resource id (the
``x-ms-cosmos-intended-collection-rid`` header that guards against a
dropped-and-recreated container) and its partition-key definition (to read the
partition-key value out of a document on a save).

Both come from the container's properties, which are fetched by one container
read and cached. This class does that read once and reads both facts off the
result, in one place, so the backend's request prep reads both facts from here
instead of calling the connection's ``_container_properties_cache`` and
``_AddPartitionKey`` directly.

The core-python (legacy) path does not use this provider; it reads the same two
facts from the connection directly.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from ..partition_key import _Empty
from ._pk_extract import extract_partition_key_value
from ._response_parse import parse_backend_response


class ContainerMetadataProvider:
    """Reads a container's rid and partition-key definition from one container
    read.

    Holds the client connection (and the optional cache-priming callable the
    container passes). It only reads the facts; the caller keeps the
    best-effort policy (logging a miss, the ``_Empty`` fallback) so the
    item-helper behaviour is unchanged.
    """

    def __init__(
        self,
        client_connection: Any,
        ensure_container_cached: Optional[Callable[[Dict[str, Any]], Any]] = None,
        resolve_through_backend: Optional[Callable[[str], Any]] = None,
    ) -> None:
        """Store the connection and optional cache-priming callable.

        :param client_connection: The connection that owns the container
            properties cache and the container read.
        :type client_connection: Any
        :param ensure_container_cached: Optional callable from the container
            that fills the cache under the container's lock.
        :type ensure_container_cached: Optional[Callable]
        """
        self._client_connection = client_connection
        self._ensure_container_cached = ensure_container_cached
        self._resolve_through_backend = resolve_through_backend
        self._resolved_properties: Dict[str, Any] = {}

    def _container_properties(
        self,
        container_link: str,
        request_options: Dict[str, Any],
    ) -> Any:
        """Return the container's cached properties, doing the container read
        first if they are not cached yet.

        Lookup errors (only the stub connections in unit tests raise them) are
        left to propagate so the caller keeps its best-effort policy.
        """
        if container_link in self._resolved_properties:
            return self._resolved_properties[container_link]
        if self._resolve_through_backend is not None:
            response = self._resolve_through_backend(container_link)
            if response is not None:
                properties = parse_backend_response(
                    response,
                    client_connection=self._client_connection,
                    response_hook=None,
                )
                self._resolved_properties[container_link] = properties
                return properties
        if self._ensure_container_cached is not None:
            self._ensure_container_cached(request_options)
        else:
            cache = self._client_connection._container_properties_cache
            if container_link not in cache:
                self._client_connection._refresh_container_properties_cache(container_link)
        properties = self._client_connection._container_properties_cache[container_link]
        self._resolved_properties[container_link] = properties
        return properties

    def container_rid(
        self,
        container_link: str,
        request_options: Dict[str, Any],
    ) -> Optional[str]:
        """Return the container's resource id, or ``None`` if it is absent.

        It does not stamp the options or swallow lookup errors; the caller
        keeps that best-effort policy.
        """
        cached = self._container_properties(container_link, request_options)
        rid_value = cached.get("_rid") if isinstance(cached, dict) else None
        return rid_value if isinstance(rid_value, str) else None

    def extract_partition_key(
        self,
        container_link: str,
        document: Dict[str, Any],
        request_options: Dict[str, Any],
    ) -> Any:
        """Return the partition-key value for ``document``.

        Returns the value the caller already placed in the options when present
        (read / delete / patch). Otherwise it reads the container's
        partition-key definition off the same container read and extracts the
        value, the same way the connection's ``_AddPartitionKey`` does. The
        value is written back into the options (matching the legacy behaviour)
        and returned; a container with no partition-key definition yields
        ``_Empty()``.
        """
        if "partitionKey" in request_options:
            return request_options["partitionKey"]
        cached = self._container_properties(container_link, request_options)
        partition_key_definition = cached.get("partitionKey") if isinstance(cached, dict) else None
        if partition_key_definition:
            value = extract_partition_key_value(partition_key_definition, document)
            request_options["partitionKey"] = value
            return value
        return _Empty()
