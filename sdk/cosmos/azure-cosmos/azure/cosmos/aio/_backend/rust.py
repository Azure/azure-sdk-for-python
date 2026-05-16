# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async Rust backend.

This is the only async-side module allowed to import the compiled PyO3
module ``azure.cosmos._rust``. The import-guard test
(``tests/test_backend_wiring_unit.py``) enforces that rule by walking
every ``.py`` file under ``azure/cosmos/`` and failing the build if any
other module imports the compiled module's name.

The compiled PyO3 module may not be present in every checkout (a fresh
clone will not have run ``maturin develop`` yet). The import below is
guarded with ``try / except ImportError`` so this file can still be
loaded; ``AsyncRustBackend.create_item`` will then raise
``NotImplementedError`` for any caller that asks for the Rust backend.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import OP_CREATE_ITEM, recover_backend_response_from_driver_error
from azure.cosmos._backend.constants import BACKEND_NAME_RUST

from .base import AsyncCosmosBackend, BackendResponse, PreparedRequest

_LOGGER = logging.getLogger(__name__)

# Module-level reference set once at import time, under the GIL. Read-only
# afterwards, so it is safe to share across event loops and across clients.
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

    The binding is synchronous from Python's perspective — its calls
    block until the driver finishes, even though internally they run
    on a Tokio runtime. To keep that blocking off the asyncio event
    loop, every operation runs in the default thread-pool executor
    via ``loop.run_in_executor``.

    The ``execute`` method dispatches on ``prepared.op``. Today only
    ``OP_CREATE_ITEM`` is supported.

    When the compiled module is *absent* (e.g. fresh clone before
    ``maturin develop`` ran), every operation raises
    ``NotImplementedError`` with a clear message pointing the developer
    at the build step.
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
            try:
                status_code, sub_status, headers, body = await loop.run_in_executor(
                    None, _rust_module.create_item, handle, prepared
                )
            except RuntimeError as exc:
                # See sync sibling for rationale: the binding wraps every
                # driver error as RuntimeError today, including non-2xx
                # HTTP responses. Recover so the helper-layer parser can
                # route the response through the typed-exception mapping.
                recovered = recover_backend_response_from_driver_error(exc)
                if recovered is None:
                    raise
                return recovered
        else:
            raise NotImplementedError(
                "AsyncRustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )

        return BackendResponse(
            status_code=int(status_code),
            sub_status=int(sub_status),
            headers=CaseInsensitiveDict(headers) if headers else None,
            body=bytes(body) if body else b"",
            diagnostics=None,
        )

