# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Prepare item requests and await the selected Python backend.

Preparation uses the same functions as azure.cosmos._helpers._item_operations:
normalize arguments, reject unsupported options, and build a prepared request.
For example, an order read becomes PreparedRequest before this helper awaits
AsyncRustBackend.execute and parses the returned BackendResponse.

Patch also completes the customer result here. With a supplied deadline,
run_with_deadline runs that work in a Python task and waits for the task to
finish handling cancellation on timeout. It cannot interrupt a running
synchronous response hook or undo work already performed by the service backend.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from ..._helpers._item_context import ItemClientDefaults, ClientLastResponseHeaders
from ..._helpers._item_operations import (
    normalize_item_arguments, validate_rust_item_options,
    build_item_request,
)
from ..._helpers._response_parse import process_backend_response, complete_item_response
from ..._operation_deadline import remaining_timeout, run_with_deadline
from .._backend.cosmos_backend import AsyncCosmosBackend


class AsyncItemHelper:
    """Runs one awaited item operation, from caller arguments to result.

    Holds the same inputs as ItemHelper: the selected Python backend,
    client defaults, and optional state for the latest response headers. It does not retain
    the legacy connection or fall back to the legacy path.
    """

    def __init__(
        self, backend: AsyncCosmosBackend, defaults: Optional[ItemClientDefaults] = None,
        response_state: Optional[ClientLastResponseHeaders] = None,
    ) -> None:
        if defaults is not None and not isinstance(defaults, ItemClientDefaults):
            raise TypeError("defaults must be ItemClientDefaults, not a client connection")
        if response_state is not None and not isinstance(response_state, ClientLastResponseHeaders):
            raise TypeError("response_state must be ClientLastResponseHeaders")
        self._backend = backend
        self._defaults = defaults if defaults is not None else ItemClientDefaults()
        self._response_state = response_state

    async def _run(
        self, op: str, arguments: Dict[str, Any], *, deadline: Optional[float] = None
    ) -> Any:
        """Build a prepared request, await execution, and process the backend response.

        Patch uses run_with_deadline around execution, parsing, and result
        completion. complete_item_response checks the remaining time before
        calling the synchronous response hook. Without a deadline, that work
        is awaited directly rather than placed in a separate task.

        The other five operations await execution and parse the response here;
        their public methods retain the remaining result-completion work.
        """
        args, options = normalize_item_arguments(
            op, arguments, compact_utf8=self._defaults.enable_compact_utf8_item_writes,
            deadline=deadline,
        )
        validate_rust_item_options(args, options)
        self._defaults.apply_to_options(options)
        prepared = build_item_request(op, args, options, self._defaults)
        if op == "patch_item":
            # With a deadline, track execution and response completion together.
            # Synchronous parsing and hooks cannot be interrupted by the timer.
            async def execute_patch() -> Any:
                response = await self._backend.execute(prepared, deadline=args["deadline"])
                parsed = process_backend_response(response, response_state=self._response_state)
                return complete_item_response(parsed, args["kwargs"].get("response_hook"), args["deadline"])

            return await run_with_deadline(execute_patch, args["deadline"])
        response = await self._backend.execute(prepared, deadline=args["deadline"])
        if op == "replace_item":
            remaining_timeout(args["deadline"])
        parsed = process_backend_response(
            response, response_state=self._response_state, response_hook=args["kwargs"].get("response_hook")
        )
        return None if op == "delete_item" else parsed

    async def create_item(self, *, deadline: Optional[float], **kwargs: Any) -> Any:
        """Create an item, failing if that id and partition key already exist.

        The time limit arrives as its own argument because the public method
        started the clock before calling in.
        """
        return await self._run("create_item", kwargs, deadline=deadline)

    async def read_item(self, **kwargs: Any) -> Any:
        """Read one item by its id and partition key."""
        return await self._run("read_item", kwargs)

    async def delete_item(self, **kwargs: Any) -> Any:
        """Delete an item; parse its backend response for headers and return None."""
        return await self._run("delete_item", kwargs)

    async def upsert_item(self, **kwargs: Any) -> Any:
        """Create an item, or replace the item with the same id and partition key."""
        return await self._run("upsert_item", kwargs)

    async def replace_item(self, **kwargs: Any) -> Any:
        """Replace the item with this id and partition key, failing if it is absent."""
        return await self._run("replace_item", kwargs)

    async def patch_item(self, **kwargs: Any) -> Any:
        """Apply a list of changes to one item.

        This helper also completes the patch result. A supplied deadline uses
        the cancellation handling described by _run.
        """
        return await self._run("patch_item", kwargs)
