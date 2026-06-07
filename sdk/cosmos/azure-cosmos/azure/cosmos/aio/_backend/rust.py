# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async Rust backend.

This is the only async-side module allowed to import the compiled PyO3
module ``azure.cosmos._rust``; an import-guard unit test enforces that
rule across the package.

The PyO3 module may not be present in every checkout. The import is
guarded with ``try / except ImportError`` so this file still loads;
operations then raise ``NotImplementedError`` pointing at the build
step.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from azure.cosmos._backend.base import (
    OP_CREATE_ITEM,
    OP_DELETE_ITEM,
    normalize_response_headers,
)
from azure.cosmos._backend.constants import BACKEND_NAME_RUST

from .base import AsyncCosmosBackend, BackendResponse, PreparedRequest

_LOGGER = logging.getLogger(__name__)

# Set once at import time under the GIL; read-only afterwards.
_rust_module: Optional[Any] = None
try:
    from azure.cosmos import _rust  # type: ignore[attr-defined]
    _rust_module = _rust
except ImportError:
    _LOGGER.debug(
        "_rust module not available; AsyncRustBackend operations "
        "will raise NotImplementedError until the PyO3 wrapper is built."
    )


class AsyncRustBackend(AsyncCosmosBackend):
    """Routes async Cosmos operations through the in-tree Rust driver.

    The binding is synchronous from Python's perspective (it blocks
    until the driver finishes, even though internally it runs on a
    Tokio runtime). To keep that blocking off the asyncio event loop,
    every operation runs via ``loop.run_in_executor`` on the default
    thread-pool.

    ``execute`` dispatches on ``prepared.op``. When the compiled module
    is absent, operations raise ``NotImplementedError``.
    """

    name = BACKEND_NAME_RUST

    def __init__(self, endpoint: str, master_key: str) -> None:
        self._endpoint = endpoint
        self._master_key = master_key
        self._handle: Optional[str] = None

    async def _ensure_handle(self) -> str:
        if self._handle is not None:
            return self._handle
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBackend: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it "
                "with `maturin develop` from the repo root."
            )
        loop = asyncio.get_running_loop()
        self._handle = await loop.run_in_executor(
            None, _rust_module.init_client, self._endpoint, self._master_key
        )
        return self._handle

    async def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        if prepared is None:
            return None
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBackend.execute: the compiled "
                "azure.cosmos._rust module is not present in this "
                "environment. Build it with `maturin develop` from "
                "the repo root."
            )

        handle = await self._ensure_handle()
        loop = asyncio.get_running_loop()
        if prepared.op == OP_CREATE_ITEM:
            status_code, sub_status, headers, body = await loop.run_in_executor(
                None, _rust_module.create_item, handle, prepared
            )
        elif prepared.op == OP_DELETE_ITEM:
            status_code, sub_status, headers, body = await loop.run_in_executor(
                None, _rust_module.delete_item, handle, prepared
            )
        else:
            raise NotImplementedError(
                "AsyncRustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )

        return BackendResponse(
            status_code=int(status_code),
            sub_status=int(sub_status),
            headers=normalize_response_headers(headers),
            body=bytes(body) if body else b"",
            diagnostics=None,
        )

