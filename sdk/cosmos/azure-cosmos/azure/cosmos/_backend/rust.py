# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Sync Rust backend.

This is the only Python module allowed to import the compiled PyO3
module ``azure.cosmos._rust``. The import-guard test
(``tests/test_backend_wiring_unit.py``) enforces that rule by walking
every ``.py`` file under ``azure/cosmos/`` and failing the build if any
other module reaches across the abstraction.

The compiled PyO3 module may not be present in every checkout (a fresh
clone will not have run ``maturin develop`` yet). The import below is
guarded with ``try / except ImportError`` so this file can still be
loaded; ``RustBackend.create_item`` will then raise
``NotImplementedError`` for any caller that asks for the Rust backend.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from azure.core.utils import CaseInsensitiveDict

from .base import OP_CREATE_ITEM, BackendResponse, CosmosBackend, PreparedRequest
from .constants import BACKEND_NAME_RUST

_LOGGER = logging.getLogger(__name__)

# Module-level reference set once at import time, under the GIL. Read-only
# afterwards, so it is safe to share across threads and across clients.
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

    Construction takes the account endpoint and master key. On the
    first operation the backend calls into the binding's
    ``init_client`` to set up the per-process Tokio runtime + driver,
    and stashes the handle the binding hands back. Subsequent calls
    reuse the cached driver.

    The ``execute`` method dispatches on ``prepared.op`` and forwards
    to the matching method on the binding. Today only
    ``OP_CREATE_ITEM`` is supported; other operations land as the
    binding gains support.

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
            # Transitional contract: caller still owns request prep.
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
        else:
            raise NotImplementedError(
                "RustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )

        return BackendResponse(
            status_code=int(status_code),
            sub_status=int(sub_status),
            headers=CaseInsensitiveDict(headers) if headers else None,
            body=bytes(body) if body else b"",
            diagnostics=None,
        )

