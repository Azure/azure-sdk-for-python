# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Constants for selecting the backend.

The backend names, the set of valid names, the default, and the
``COSMOS_BACKEND`` environment variable live here and are imported by every
module that needs them so the strings cannot drift. (The operation-kind
constants and the dispatch types live with the contract in ``base``.)
"""
from typing import Any

#: Default backend; routes through the existing azure-core pipeline.
BACKEND_NAME_CORE_PYTHON = "core-python"

#: Opt-in Rust-driver path. Selecting it before the compiled binding is built
#: does not fail at construction -- the first operation is what raises
#: ``NotImplementedError``.
BACKEND_NAME_RUST = "rust"

#: Every accepted backend name. The factory validates against this.
VALID_BACKEND_NAMES = (BACKEND_NAME_CORE_PYTHON, BACKEND_NAME_RUST)

#: Backend used when the caller passed neither ``_backend=`` nor the env var.
DEFAULT_BACKEND_NAME = BACKEND_NAME_CORE_PYTHON

#: Env var read by the factory. A ``_backend=`` argument wins; otherwise this
#: env var decides; otherwise ``DEFAULT_BACKEND_NAME`` is used.
BACKEND_ENV_VAR = "COSMOS_BACKEND"


def is_rust_backend(backend: Any) -> bool:
    """Return whether ``backend`` is the concrete Rust implementation."""
    return getattr(backend, "name", None) == BACKEND_NAME_RUST
