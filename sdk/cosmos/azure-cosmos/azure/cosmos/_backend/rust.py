# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Sync Rust backend.

This is the only Python module allowed to import the compiled PyO3
module ``azure.cosmos._rust``; an import-guard unit test enforces that
rule across the package.

The PyO3 module may not be present in every checkout (a fresh clone has
not run ``maturin develop`` yet). The import is guarded with
``try / except ImportError`` so this file still loads; operations then
raise ``NotImplementedError`` with a message pointing at the build step.
"""
from __future__ import annotations

import logging
from typing import Any, Optional


from .base import (
    OP_CREATE_ITEM,
    OP_DELETE_ITEM,
    BackendResponse,
    CosmosBackend,
    PreparedRequest,
    normalize_response_headers,
)
from .constants import BACKEND_NAME_RUST

_LOGGER = logging.getLogger(__name__)

# Set once at import time under the GIL; read-only afterwards.
_rust_module: Optional[Any] = None
try:
    from azure.cosmos import _rust  # type: ignore[attr-defined]
    _rust_module = _rust
except ImportError:
    _LOGGER.debug(
        "_rust module not available; RustBackend operations "
        "will raise NotImplementedError until the PyO3 wrapper is built."
    )


class RustBackend(CosmosBackend):
    """Routes Cosmos operations through the in-tree Rust driver.

    Construction takes the account endpoint and master key. The
    binding's ``init_client`` is called lazily on the first operation
    (one driver + Tokio runtime per process, cached on the instance).

    ``execute`` dispatches on ``prepared.op``. When the compiled module
    is absent every operation raises ``NotImplementedError``.
    """

    name = BACKEND_NAME_RUST

    def __init__(self, endpoint: str, master_key: str) -> None:
        self._endpoint = endpoint
        self._master_key = master_key
        self._handle: Optional[str] = None

    def _ensure_handle(self) -> str:
        if self._handle is not None:
            return self._handle
        if _rust_module is None:
            raise NotImplementedError(
                "RustBackend: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it with "
                "`maturin develop` from the repo root."
            )
        self._handle = _rust_module.init_client(self._endpoint, self._master_key)
        return self._handle

    def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        if prepared is None:
            # Caller still owns request prep; nothing to do here.
            return None
        if _rust_module is None:
            raise NotImplementedError(
                "RustBackend.execute: the compiled "
                "azure.cosmos._rust module is not present in "
                "this environment. Build it with `maturin develop` from "
                "the repo root."
            )

        handle = self._ensure_handle()
        if prepared.op == OP_CREATE_ITEM:
            status_code, sub_status, headers, body = _rust_module.create_item(handle, prepared)
        elif prepared.op == OP_DELETE_ITEM:
            status_code, sub_status, headers, body = _rust_module.delete_item(handle, prepared)
        else:
            raise NotImplementedError(
                "RustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )

        return BackendResponse(
            status_code=int(status_code),
            sub_status=int(sub_status),
            headers=normalize_response_headers(headers),
            body=bytes(body) if body else b"",
            diagnostics=None,
        )

