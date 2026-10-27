# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Names retained for migration checks in the Python wrapper.

The Rust path is the only release execution path. The legacy identifier, private selector,
and current legacy default below are temporary implementation details to
remove, not supported customer choices. Both client types use these same
values while migration checks still need them.
"""
from typing import Any

#: Identifier for the legacy path and its Python HTTP pipeline.
BACKEND_NAME_CORE_PYTHON = "core-python"

#: Identifier for the Rust path. Python backend construction requires the binding
#: to check CosmosDriverRuntime settings; driver acquisition waits until use.
BACKEND_NAME_RUST = "rust"

#: Values accepted by the temporary migration/test selector.
VALID_BACKEND_NAMES = (BACKEND_NAME_CORE_PYTHON, BACKEND_NAME_RUST)

#: Current migration-checkout default, not the Rust-only release contract.
DEFAULT_BACKEND_NAME = BACKEND_NAME_CORE_PYTHON

#: Private test/migration control. A ``_backend=`` argument wins; otherwise this
#: env var decides; otherwise ``DEFAULT_BACKEND_NAME`` is used.
BACKEND_ENV_VAR = "COSMOS_BACKEND"


def is_rust_backend(backend: Any) -> bool:
    """Identify a Python backend for the Rust path while the legacy path remains."""
    return getattr(backend, "name", None) == BACKEND_NAME_RUST
