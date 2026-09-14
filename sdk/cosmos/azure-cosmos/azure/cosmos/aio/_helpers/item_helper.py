# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async Rust item execution using the same pure request preparation as sync."""
from __future__ import annotations

from typing import Any, Dict, Optional

from ..._backend.contracts import PreparedRequest
from ..._helpers._item_context import ItemClientDefaults, ResponseHeaderState
from ..._helpers.item_helper import (
    prepare_item_arguments, validate_rust_item_options,
    normalize_item_partition_key, execute_item_builder,
)
from ...partition_key import _Empty
from ..._helpers._response_parse import parse_backend_response
from .._backend.cosmos_backend import AsyncCosmosBackend
from ._metadata_provider import AsyncContainerMetadataProvider


class AsyncItemHelper:
    """Connection-free async item operations; option and wire builders are shared."""

    def __init__(
        self, backend: AsyncCosmosBackend, defaults: Optional[ItemClientDefaults] = None,
        response_state: Optional[ResponseHeaderState] = None,
    ) -> None:
        if defaults is not None and not isinstance(defaults, ItemClientDefaults):
            raise TypeError("defaults must be ItemClientDefaults, not a client connection")
        if response_state is not None and not isinstance(response_state, ResponseHeaderState):
            raise TypeError("response_state must be ResponseHeaderState")
        self._backend = backend
        self._defaults = defaults if defaults is not None else ItemClientDefaults()
        self._response_state = response_state

    async def _run(self, op: str, arguments: Dict[str, Any]) -> Any:
        args, options = prepare_item_arguments(op, arguments)
        validate_rust_item_options(op, args, options)
        link = args["container_link"]
        metadata = AsyncContainerMetadataProvider(self._backend, self._response_state)

        async def prepare_request() -> PreparedRequest:
            rid = await metadata.container_rid(link, options)
            if op in ("create_item", "upsert_item", "replace_item"):
                key = await metadata.extract_partition_key(link, args["body"], options)
            else:
                key = options.get("partitionKey", _Empty())
            properties = await metadata._container_properties(link, options)
            key = normalize_item_partition_key(key, properties)
            return execute_item_builder(op, args, options, key, rid, self._defaults)

        def parse_response(response: Any) -> Any:
            parsed = parse_backend_response(
                response, response_state=self._response_state, response_hook=args["kwargs"].get("response_hook")
            )
            return None if op == "delete_item" else parsed

        return await self._backend.run_item_operation(
            prepare_request=prepare_request,
            parse_response=parse_response,
        )

    async def create_item(self, **kwargs: Any) -> Any:
        """Create an item through Rust only."""
        return await self._run("create_item", kwargs)

    async def read_item(self, **kwargs: Any) -> Any:
        """Read an item through Rust only."""
        return await self._run("read_item", kwargs)

    async def delete_item(self, **kwargs: Any) -> Any:
        """Delete an item through Rust only."""
        return await self._run("delete_item", kwargs)

    async def upsert_item(self, **kwargs: Any) -> Any:
        """Upsert an item through Rust only."""
        return await self._run("upsert_item", kwargs)

    async def replace_item(self, **kwargs: Any) -> Any:
        """Replace an item through Rust only."""
        return await self._run("replace_item", kwargs)

    async def patch_item(self, **kwargs: Any) -> Any:
        """Patch through Rust; unsupported guards raise explicitly."""
        return await self._run("patch_item", kwargs)
