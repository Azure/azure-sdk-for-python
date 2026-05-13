# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Sync Rust backend.

This is the only Python module allowed to import the compiled PyO3
module ``azure.cosmos._azure_cosmos_pyo3``. The import-guard test
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

from .base import BackendResponse, CosmosBackend, PreparedRequest
from .constants import BACKEND_NAME_RUST

_LOGGER = logging.getLogger(__name__)

# Module-level reference set once at import time, under the GIL. Read-only
# afterwards, so it is safe to share across threads and across clients.
_pyo3_driver: Optional[Any] = None
try:
    from azure.cosmos import _azure_cosmos_pyo3  # type: ignore[attr-defined]
    _pyo3_driver = _azure_cosmos_pyo3
except ImportError:
    _LOGGER.debug(
        "_azure_cosmos_pyo3 module not available; RustBackend operations "
        "will raise NotImplementedError until the PyO3 wrapper is built."
    )


class RustBackend(CosmosBackend):
    """Routes ``create_item`` calls through the in-tree Rust driver.

    Today this class's ``create_item`` raises ``NotImplementedError`` on
    every call. That is the expected behavior for the dispatch-only
    slice — a developer who runs the existing test suite with
    ``COSMOS_BACKEND=rust`` should see every create_item test fail
    loudly, which proves the dispatch wiring works end-to-end. The real
    implementation lands once the Rust-side gaps are closed and the
    helper layer exists.
    """

    name = BACKEND_NAME_RUST

    def __init__(self) -> None:
        self._driver = _pyo3_driver

    def create_item(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        # Two failure modes for the rust path today, ordered by which
        # one a developer is more likely to hit. The shared
        # "not implemented yet" prefix is part of the contract the
        # dispatch tests assert against.
        if self._driver is None:
            raise NotImplementedError(
                "RustBackend.create_item not implemented yet "
                "(also: compiled azure.cosmos._azure_cosmos_pyo3 module "
                "is not present in this environment; build it with "
                "`maturin develop` from azure_data_cosmos_driver/, or "
                "install the package built with the rust extension "
                "enabled). The adapter that calls into the binary will "
                "land in a later change."
            )
        raise NotImplementedError("RustBackend.create_item not implemented yet")

