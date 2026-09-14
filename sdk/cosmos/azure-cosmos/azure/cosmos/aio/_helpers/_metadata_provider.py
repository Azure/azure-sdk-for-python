# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async metadata resolution exclusively through the Rust backend."""
from __future__ import annotations

from typing import Any, Dict, Optional

from ..._helpers._metadata_provider import parse_container_metadata
from ..._helpers._item_context import ResponseHeaderState
from ..._helpers._pk_extract import extract_partition_key_value
from ...partition_key import _Empty
from .._backend.cosmos_backend import AsyncCosmosBackend


class AsyncContainerMetadataProvider:
    """Per-operation reuse of metadata from the driver's shared cache."""

    def __init__(
        self, backend: AsyncCosmosBackend, response_state: Optional[ResponseHeaderState] = None
    ) -> None:
        self._backend = backend
        self._response_state = response_state
        self._resolved_properties: Dict[str, Any] = {}

    async def _container_properties(self, container_link: str, request_options: Dict[str, Any]) -> Dict[str, Any]:
        if container_link not in self._resolved_properties:
            self._resolved_properties[container_link] = parse_container_metadata(
                await self._backend.resolve_container_metadata(container_link), self._response_state
            )
        return self._resolved_properties[container_link]

    async def container_rid(self, container_link: str, request_options: Dict[str, Any]) -> str:
        """Return the rid, propagating lookup/protocol failures."""
        return (await self._container_properties(container_link, request_options))["_rid"]

    async def extract_partition_key(
        self, container_link: str, document: Dict[str, Any], request_options: Dict[str, Any]
    ) -> Any:
        """Extract using resolved metadata; never consult a Python connection cache."""
        if "partitionKey" in request_options:
            return request_options["partitionKey"]
        definition = (await self._container_properties(container_link, request_options)).get("partitionKey")
        if definition:
            value = extract_partition_key_value(definition, document)
            request_options["partitionKey"] = value
            return value
        return _Empty()
