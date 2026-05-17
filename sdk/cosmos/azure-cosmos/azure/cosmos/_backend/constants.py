# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Constants for the backend dispatch layer.

Why this file exists:

    The same strings — the two backend names, the env var, the per-request
    kwarg key — show up in the factory, the two backend classes, the
    user-agent policy, the container dispatch site, and the tests. If any
    one of those copies drifts (for example, somebody types "corepython"
    instead of "core-python"), the bug only shows up at runtime and is
    annoying to track down.

    Putting the strings in one place fixes that. Every other module that
    needs one of these names imports it from here. Tests assert against
    the same constants the production code uses, so renaming a value in
    this file is a one-line change that the type checker and test suite
    immediately tell you about.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Backend names
# ---------------------------------------------------------------------------
#
# The two values that the user can set on the constructor kwarg ``_backend``
# or in the ``COSMOS_BACKEND`` environment variable.

#: The default backend. Routes through the existing in-tree azure-core
#: pipeline plus the ``CosmosClientConnection`` helpers. This is *not*
#: deprecated; it is the production path today and stays that way until
#: a future release decides the Rust path is ready to be the default.
BACKEND_NAME_CORE_PYTHON = "core-python"

#: The Rust-driver-backed path. Opt-in only today; the implementation
#: itself lands incrementally in later changes. Selecting this today
#: causes ``RustBackend.create_item`` to raise ``NotImplementedError``
#: so the developer gets a loud signal that they are running against a
#: stub.
BACKEND_NAME_RUST = "rust"

#: Tuple of every accepted backend name. The factory validates against
#: this; an unknown value raises ``ValueError`` at client construction.
VALID_BACKEND_NAMES = (BACKEND_NAME_CORE_PYTHON, BACKEND_NAME_RUST)

#: The backend the factory picks when the caller did not pass ``_backend=``
#: and the env var is unset. Stays ``core-python`` until a future release
#: explicitly flips it.
DEFAULT_BACKEND_NAME = BACKEND_NAME_CORE_PYTHON


# ---------------------------------------------------------------------------
# Selection knob
# ---------------------------------------------------------------------------

#: Environment variable read by the factory when no explicit ``_backend=``
#: was passed to the client constructor. Lets a developer or operator
#: switch backends without a code change. Precedence:
#: constructor kwarg  >  this env var  >  ``DEFAULT_BACKEND_NAME``.
BACKEND_ENV_VAR = "COSMOS_BACKEND"


