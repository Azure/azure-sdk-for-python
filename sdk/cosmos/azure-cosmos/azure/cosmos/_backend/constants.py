# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Names retained for migration checks in the Python wrapper.

Rust is the default execution path. The legacy identifier and private selector
remain for migration tests until all methods are migrated. They are not
supported customer choices. Both client types use these same values.
"""
from typing import Any

#: Identifier for the legacy path and its Python HTTP pipeline.
BACKEND_NAME_CORE_PYTHON = "core-python"

#: Identifier for the Rust path. Python backend construction requires the binding
#: to reject retired client-level network settings; driver acquisition waits until use.
BACKEND_NAME_RUST = "rust"

#: Values accepted by the temporary migration/test selector.
VALID_BACKEND_NAMES = (BACKEND_NAME_CORE_PYTHON, BACKEND_NAME_RUST)

#: Default execution path when no private migration/test selection is supplied.
DEFAULT_BACKEND_NAME = BACKEND_NAME_RUST

#: Private test/migration control. A ``_backend=`` argument wins; otherwise this
#: env var decides; otherwise ``DEFAULT_BACKEND_NAME`` is used.
BACKEND_ENV_VAR = "COSMOS_BACKEND"

#: Test-only switch. The release extension contains the driver's fault
#: injection, so ``_fault_injection_rules`` is refused unless this is ``"1"``.
FAULT_INJECTION_ENV_VAR = "COSMOS_ENABLE_FAULT_INJECTION"


def is_rust_backend(backend: Any) -> bool:
    """Identify a Python backend for the Rust path while the legacy path remains.

    :param backend: Backend candidate whose name is inspected.
    :type backend: typing.Any
    :return: Whether the backend advertises the Rust execution path.
    :rtype: bool
    """
    return getattr(backend, "name", None) == BACKEND_NAME_RUST
