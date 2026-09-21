# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Constants for selecting the backend.

Keep names and selection defaults here so both client types use the same
values. Operation names live in operations.py; request and response objects
live in contracts.py.
"""
from typing import Any

#: Default backend; routes through the existing azure-core pipeline.
BACKEND_NAME_CORE_PYTHON = "core-python"

#: Rust implementation. Constructing it requires the compiled extension for
#: checking shared runtime settings, even though driver creation waits until use.
BACKEND_NAME_RUST = "rust"

#: Every accepted backend name. The factory validates against this.
VALID_BACKEND_NAMES = (BACKEND_NAME_CORE_PYTHON, BACKEND_NAME_RUST)

#: Backend used when the caller passed neither ``_backend=`` nor the env var.
DEFAULT_BACKEND_NAME = BACKEND_NAME_CORE_PYTHON

#: Env var read by the factory. A ``_backend=`` argument wins; otherwise this
#: env var decides; otherwise ``DEFAULT_BACKEND_NAME`` is used.
BACKEND_ENV_VAR = "COSMOS_BACKEND"


def is_rust_backend(backend: Any) -> bool:
    """Return whether the backend identifies itself as the Rust implementation."""
    return getattr(backend, "name", None) == BACKEND_NAME_RUST
