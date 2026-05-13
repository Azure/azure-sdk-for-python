# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async Rust backend.

This is the only async-side module allowed to import the compiled PyO3
module ``azure.cosmos._azure_cosmos_pyo3``. The import-guard test
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

import logging
from typing import Any, Optional

from azure.cosmos._backend.constants import BACKEND_NAME_RUST

from .base import AsyncCosmosBackend, BackendResponse, PreparedRequest

_LOGGER = logging.getLogger(__name__)

# Module-level reference set once at import time, under the GIL. Read-only
# afterwards, so it is safe to share across event loops and across clients.
_pyo3_driver: Optional[Any] = None
try:
    from azure.cosmos import _azure_cosmos_pyo3  # type: ignore[attr-defined]
    _pyo3_driver = _azure_cosmos_pyo3
except ImportError:
    _LOGGER.debug(
        "_azure_cosmos_pyo3 module not available; AsyncRustBackend operations "
        "will raise NotImplementedError until the PyO3 wrapper is built."
    )


class AsyncRustBackend(AsyncCosmosBackend):
    """Routes async ``create_item`` calls through the in-tree Rust driver.

    Today this class's ``create_item`` raises ``NotImplementedError`` on
    every call. That is the expected behavior for the dispatch-only
    slice — a developer who runs the existing async test suite with
    ``COSMOS_BACKEND=rust`` should see every async create_item test fail
    loudly, which proves the async dispatch wiring works end-to-end.
    The real implementation — calling into the compiled PyO3 module and
    converting its return value into a ``BackendResponse`` — lands once
    the Rust-side gaps are closed and the helper layer exists.
    """

    name = BACKEND_NAME_RUST

    def __init__(self) -> None:
        # Hold the module reference set at import time. None when the
        # compiled module is not yet built for this checkout.
        self._driver = _pyo3_driver

    async def create_item(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        raise NotImplementedError("AsyncRustBackend.create_item not implemented yet")

