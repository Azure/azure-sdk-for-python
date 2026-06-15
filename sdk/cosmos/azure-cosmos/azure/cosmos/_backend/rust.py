# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Sync backend that sends operations to the compiled Rust module.

This is one of only two modules allowed to import ``azure.cosmos._rust``
(a unit test enforces that). The compiled module is not present until it
has been built, so the import is guarded; until then, operations raise
``NotImplementedError`` pointing at the build step.
"""
from __future__ import annotations

import logging
import threading
from typing import Any, Optional


from .base import (
    OP_CREATE_ITEM,
    OP_DELETE_ITEM,
    OP_PATCH_ITEM,
    OP_READ_ITEM,
    OP_REPLACE_ITEM,
    OP_UPSERT_ITEM,
    BackendResponse,
    CosmosBackend,
    PreparedRequest,
    normalize_response_headers,
)
from .constants import BACKEND_NAME_RUST

_LOGGER = logging.getLogger(__name__)

# Imported once when this module loads; not changed afterwards.
_rust_module: Optional[Any] = None
try:
    from azure.cosmos import _rust  # type: ignore[attr-defined]
    _rust_module = _rust
except ImportError:
    _LOGGER.debug(
        "_rust module not available; RustBackend operations "
        "will raise NotImplementedError until the Rust module is built."
    )


class RustBackend(CosmosBackend):
    """Sends operations to the Rust driver.

    Takes the account endpoint and key. The client handle -- the opaque
    token ``init_client`` returns, which references the live client the
    Rust driver builds from that endpoint and key -- is built once, on the
    first operation, and then reused; every operation passes it back to the
    Rust module. Python never inspects the handle, it just hands it back.
    Each operation is routed by its kind; when the compiled module is
    missing, every operation raises ``NotImplementedError``.
    """

    name = BACKEND_NAME_RUST

    def __init__(self, endpoint: str, master_key: str) -> None:
        self._endpoint = endpoint
        self._master_key = master_key
        # A "handle" is the ID the Rust driver hands back from init_client().
        # It stands for the real Cosmos client that lives *inside* the Rust
        # module -- the object that actually owns the HTTPS connection pool,
        # the signed master-key auth state, and the endpoint/region routing.
        # Python cannot hold that Rust object directly across the language
        # boundary, so it keeps this token instead and passes it back into
        # Rust on every call (read/create/replace/...). It is critical because
        # every operation must run against that *one* already-built client:
        # init_client() does the expensive setup (open connections, prepare
        # auth) once, and handing the same handle back is what lets later calls
        # skip all of that. None means "not built yet" -- _ensure_handle()
        # creates it lazily on the first operation, under a lock so two
        # first-callers don't each build (and then leak) a separate client.
        self._handle: Optional[str] = None
        # Lets only one caller build the handle the first time, so
        # concurrent first calls don't each build and discard one.
        self._handle_lock = threading.Lock()

    def _ensure_handle(self) -> str:
        # If the handle is already built, return it without locking.
        handle = self._handle
        if handle is not None:
            return handle
        if _rust_module is None:
            raise NotImplementedError(
                "RustBackend: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it with "
                "`maturin develop` from the repo root."
            )
        # Build it once. The lock, with a second check inside, keeps
        # concurrent first callers from each building one.
        with self._handle_lock:
            if self._handle is None:
                self._handle = _rust_module.init_client(self._endpoint, self._master_key)
            return self._handle

    def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Entry point every point operation (read/create/upsert/replace/delete/patch) goes through to reach the Rust driver."""
        if prepared is None:
            # Nothing to send.
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
        elif prepared.op == OP_UPSERT_ITEM:
            status_code, sub_status, headers, body = _rust_module.upsert_item(handle, prepared)
        elif prepared.op == OP_REPLACE_ITEM:
            status_code, sub_status, headers, body = _rust_module.replace_item(handle, prepared)
        elif prepared.op == OP_DELETE_ITEM:
            status_code, sub_status, headers, body = _rust_module.delete_item(handle, prepared)
        elif prepared.op == OP_READ_ITEM:
            status_code, sub_status, headers, body = _rust_module.read_item(handle, prepared)
        elif prepared.op == OP_PATCH_ITEM:
            status_code, sub_status, headers, body = _rust_module.patch_item(handle, prepared)
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
