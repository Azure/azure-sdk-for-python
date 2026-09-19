# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async version of the item helper in azure/cosmos/_helpers/_item_operations.py.

The steps and their order are the same, and the first three of them are
imported from that file rather than copied. Read it for what the steps are
and why the flow is shaped this way.

Two things differ here:

- The backend call is awaited.
- Patch runs inside a task that a timeout can cancel. The other five
  operations do not need that; AsyncItemHelper._run explains why.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from ..._helpers._item_context import ItemClientDefaults, ClientLastResponseHeaders
from ..._helpers._item_operations import (
    normalize_item_arguments, validate_rust_item_options,
    build_item_request,
)
from ..._helpers._response_parse import process_backend_response, complete_item_response
from ..._operation_deadline import run_with_deadline
from .._backend.cosmos_backend import AsyncCosmosBackend


class AsyncItemHelper:
    """Runs one awaited item operation, from caller arguments to result.

    Holds the same three things as the sync ItemHelper and nothing more: a
    backend, the client-wide defaults, and somewhere to record the headers
    from the most recent reply.
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
        """Prepare, send, and interpret one operation.

        Five of the six await the backend, parse the reply, and leave the
        finishing to the public method that called in.

        Patch is handled differently, and the difference exists only on this
        path. Patch finishes its own result, so after the reply arrives there
        is still a time check and the caller's response hook left to run.
        Awaiting those straight through would put them outside the time
        limit. Running all three inside one task means a timeout cancels the
        whole sequence and waits for that cancellation to land, so nothing is
        left running once this call returns.
        """
        args, options = normalize_item_arguments(
            op, arguments, compact_utf8=self._defaults.enable_compact_utf8_item_writes,
            deadline=deadline,
        )
        validate_rust_item_options(args, options)
        self._defaults.apply_to_options(options)
        prepared = build_item_request(op, args, options, self._defaults)
        if op == "patch_item":
            # Execute, parse, and finish inside one task, so a timeout cancels
            # all three together rather than only the send.
            async def execute_patch() -> Any:
                response = await self._backend.execute(prepared, deadline=args["deadline"])
                parsed = process_backend_response(response, response_state=self._response_state)
                return complete_item_response(parsed, args["kwargs"].get("response_hook"), args["deadline"])

            return await run_with_deadline(execute_patch, args["deadline"])
        response = await self._backend.execute(prepared, deadline=args["deadline"])
        parsed = process_backend_response(
            response, response_state=self._response_state, response_hook=args["kwargs"].get("response_hook")
        )
        return None if op == "delete_item" else parsed

    async def create_item(self, *, deadline: Optional[float], **kwargs: Any) -> Any:
        """Create an item, failing if the id already exists.

        The time limit arrives as its own argument because the public method
        started the clock before calling in.
        """
        return await self._run("create_item", kwargs, deadline=deadline)

    async def read_item(self, **kwargs: Any) -> Any:
        """Read one item by its id and partition key."""
        return await self._run("read_item", kwargs)

    async def delete_item(self, **kwargs: Any) -> Any:
        """Delete an item. Returns nothing; the reply is read for its headers."""
        return await self._run("delete_item", kwargs)

    async def upsert_item(self, **kwargs: Any) -> Any:
        """Create an item, or replace it if one with that id is already there."""
        return await self._run("upsert_item", kwargs)

    async def replace_item(self, **kwargs: Any) -> Any:
        """Replace the item with this id, failing if it is not there."""
        return await self._run("replace_item", kwargs)

    async def patch_item(self, **kwargs: Any) -> Any:
        """Apply a list of changes to one item.

        The only operation here that finishes its own result, inside a task a
        timeout can cancel.
        """
        return await self._run("patch_item", kwargs)
