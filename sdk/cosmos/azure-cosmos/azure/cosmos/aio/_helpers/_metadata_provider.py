# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async version of the container metadata provider.

Same role as the sync ``ContainerMetadataProvider``: it reads the container's
resource id and partition-key definition off one container read. Only the read
is awaited here; the partition-key extraction is plain and shared with the sync
side via ``_pk_extract``.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional

from ..._helpers._pk_extract import extract_partition_key_value
from ...partition_key import _Empty


class AsyncContainerMetadataProvider:
    """Async version of ``ContainerMetadataProvider``.

    See the sync class for the full notes; this awaits the container read and
    otherwise behaves identically.
    """

    def __init__(
        self,
        client_connection: Any,
        ensure_container_cached: Optional[Callable[[Dict[str, Any]], Awaitable[Any]]] = None,
    ) -> None:
        self._client_connection = client_connection
        self._ensure_container_cached = ensure_container_cached

    async def _container_properties(
        self,
        container_link: str,
        request_options: Dict[str, Any],
    ) -> Any:
        """Return the cached container properties, awaiting the one container
        read if they are not cached yet.
        """
        if self._ensure_container_cached is not None:
            await self._ensure_container_cached(request_options)
        else:
            cache = self._client_connection._container_properties_cache
            if container_link not in cache:
                await self._client_connection._refresh_container_properties_cache(container_link)
        return self._client_connection._container_properties_cache[container_link]

    async def container_rid(
        self,
        container_link: str,
        request_options: Dict[str, Any],
    ) -> Optional[str]:
        """Return the container's resource id, or ``None`` if it is absent."""
        cached = await self._container_properties(container_link, request_options)
        rid_value = cached.get("_rid") if isinstance(cached, dict) else None
        return rid_value if isinstance(rid_value, str) else None

    async def extract_partition_key(
        self,
        container_link: str,
        document: Dict[str, Any],
        request_options: Dict[str, Any],
    ) -> Any:
        """Return the partition-key value for ``document``.

        Returns the value already in the options when present; otherwise reads
        the partition-key definition off the same container read and extracts
        the value, the same way the connection's ``_AddPartitionKey`` does. The
        extraction itself is plain and synchronous.
        """
        if "partitionKey" in request_options:
            return request_options["partitionKey"]
        cached = await self._container_properties(container_link, request_options)
        partition_key_definition = cached.get("partitionKey") if isinstance(cached, dict) else None
        if partition_key_definition:
            value = extract_partition_key_value(partition_key_definition, document)
            request_options["partitionKey"] = value
            return value
        return _Empty()

