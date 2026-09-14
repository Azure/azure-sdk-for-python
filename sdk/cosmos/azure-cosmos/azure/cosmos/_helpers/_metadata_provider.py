# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Rust-owned container metadata, with reuse only within one item operation."""
from __future__ import annotations

from typing import Any, Dict, Optional

from .._backend.cosmos_backend import CosmosBackend
from .._backend.errors import BackendProtocolError
from ..partition_key import _Empty
from ._pk_extract import extract_partition_key_value
from ._item_context import ResponseHeaderState
from ._response_parse import parse_backend_response


def parse_container_metadata(
    response: Any, response_state: Optional[ResponseHeaderState] = None
) -> Dict[str, Any]:
    """Reject missing/invalid metadata without confusing it with an unpartitioned container."""
    if response is None:
        raise BackendProtocolError("The backend returned no container metadata")
    properties = parse_backend_response(response, response_state=response_state)
    if not isinstance(properties.get("_rid"), str) or not properties["_rid"]:
        raise BackendProtocolError("Container metadata must contain a non-empty _rid")
    definition = properties.get("partitionKey")
    if definition is not None and (
        not isinstance(definition, dict)
        or not isinstance(definition.get("paths"), list)
        or not definition["paths"]
        or any(not isinstance(path, str) for path in definition["paths"])
    ):
        raise BackendProtocolError("Container metadata contains an invalid partitionKey definition")
    return properties


class ContainerMetadataProvider:
    """Resolve through the backend only. The driver owns the shared metadata cache."""

    def __init__(
        self, backend: CosmosBackend, response_state: Optional[ResponseHeaderState] = None
    ) -> None:
        self._backend = backend
        self._response_state = response_state
        self._resolved_properties: Dict[str, Any] = {}

    def _container_properties(self, container_link: str, request_options: Dict[str, Any]) -> Dict[str, Any]:
        if container_link not in self._resolved_properties:
            self._resolved_properties[container_link] = parse_container_metadata(
                self._backend.resolve_container_metadata(container_link), self._response_state
            )
        return self._resolved_properties[container_link]

    def container_rid(self, container_link: str, request_options: Dict[str, Any]) -> str:
        """Return the resolved rid; metadata lookup and protocol errors propagate."""
        return self._container_properties(container_link, request_options)["_rid"]

    def extract_partition_key(
        self, container_link: str, document: Dict[str, Any], request_options: Dict[str, Any]
    ) -> Any:
        """Extract a document key; missing definition on valid metadata means unpartitioned."""
        if "partitionKey" in request_options:
            return request_options["partitionKey"]
        definition = self._container_properties(container_link, request_options).get("partitionKey")
        if definition:
            value = extract_partition_key_value(definition, document)
            request_options["partitionKey"] = value
            return value
        return _Empty()
