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

#: Env var read by the factory. Precedence:
#: constructor kwarg > env var > ``DEFAULT_BACKEND_NAME``.
BACKEND_ENV_VAR = "COSMOS_BACKEND"


def is_rust_backend(backend: Any) -> bool:
    """Return whether ``backend`` is the concrete Rust implementation."""
    return getattr(backend, "name", None) == BACKEND_NAME_RUST


#: Env var that opts into strict per-account engine isolation on the Rust backend.
#: When truthy, building a second ``CosmosClient`` to an account whose
#: client-construction config differs from the first live client's raises
#: ``StrictEngineIsolationError`` instead of silently building a second isolated
#: engine. Off by default (silent isolation). Precedence: factory toggle > env var >
#: off. On/off values are in ``STRICT_ISOLATION_TRUE_VALUES`` /
#: ``STRICT_ISOLATION_FALSE_VALUES``; an unrecognized value raises ``ValueError``
#: rather than silently disabling the toggle.
RUST_STRICT_ISOLATION_ENV_VAR = "COSMOS_RUST_STRICT_ISOLATION"

#: Case-insensitive env-var values (after trimming whitespace) that turn strict
#: isolation on.
STRICT_ISOLATION_TRUE_VALUES = ("1", "true", "yes", "on")

#: Case-insensitive values that turn it off; unset or empty is also off. Any
#: value outside either set is rejected with ``ValueError`` so a typo (e.g.
#: ``treu``) can't silently disable the safety toggle.
STRICT_ISOLATION_FALSE_VALUES = ("0", "false", "no", "off")
