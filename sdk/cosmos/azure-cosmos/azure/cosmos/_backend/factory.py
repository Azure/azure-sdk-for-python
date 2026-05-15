# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Factory that picks which backend a single client will use.

A ``CosmosClient`` calls ``make_backend(...)`` exactly once at
construction time and stores the returned object. Every subsequent
``create_item`` call on every container created by that client dispatches
through the same instance.

Selection precedence (highest wins):

  1. The value the caller passed to the client constructor as the
     private kwarg ``_backend=``.
  2. The value of the ``COSMOS_BACKEND`` environment variable.
  3. The default, ``core-python``.

If a value comes in that is not ``"core-python"`` or ``"rust"``, the
factory raises ``ValueError`` immediately at client construction time.
Failing loud is intentional — a typo'd value silently falling back to
the default would mask configuration drift in production.

When ``rust`` is the chosen backend, the factory also needs the account
endpoint and a master key — the binding's ``init_client`` requires both
to construct the underlying ``CosmosDriver``. The factory accepts them
as keyword arguments and surfaces a clear ``ValueError`` if Rust was
requested without a master-key credential.
"""
from __future__ import annotations

import os
from typing import Any, Optional

from .base import CosmosBackend
from .constants import (
    BACKEND_ENV_VAR,
    BACKEND_NAME_RUST,
    DEFAULT_BACKEND_NAME,
    VALID_BACKEND_NAMES,
)
from .core_python import CorePythonBackend
from .rust import RustBackend


def resolve_backend_name(explicit: Optional[str]) -> str:
    """Return one of the values in ``VALID_BACKEND_NAMES`` after applying
    the precedence rules above.

    Shared between the sync and async factories so the precedence rules,
    valid values, and error message live in one place.
    """
    if explicit is not None:
        choice = explicit
    else:
        choice = os.environ.get(BACKEND_ENV_VAR, DEFAULT_BACKEND_NAME)
    if choice not in VALID_BACKEND_NAMES:
        raise ValueError(
            "Invalid backend {!r}. Expected one of {}. "
            "Set the constructor kwarg _backend=, or the {} environment variable.".format(
                choice, VALID_BACKEND_NAMES, BACKEND_ENV_VAR
            )
        )
    return choice


def _master_key_or_raise(credential: Any) -> str:
    """Pull a master-key string out of the credential, or fail loud.

    The Rust binding's ``init_client`` only accepts master-key auth
    today. Other credential shapes (Entra TokenCredential, resource
    token, AAD) need driver-side support that doesn't exist yet, so we
    refuse them at construction time rather than letting the failure
    surface on the first request.
    """
    if isinstance(credential, str):
        return credential
    if isinstance(credential, dict) and "masterKey" in credential:
        return credential["masterKey"]
    raise ValueError(
        "_backend='rust' requires a master-key credential (a string, or "
        "a dict with a 'masterKey' entry). The Rust backend does not "
        "yet support TokenCredential / AAD / resource-token auth."
    )


def make_backend(
    explicit: Optional[str],
    *,
    url: Optional[str] = None,
    credential: Any = None,
) -> CosmosBackend:
    """Build the single backend instance a sync ``CosmosClient`` will hold.

    ``explicit`` is what the caller passed as ``_backend=`` (or ``None`` if
    they passed nothing — in which case the env var, then the default, are
    consulted). ``url`` and ``credential`` come from the same client
    constructor and are only used when the chosen backend is ``rust``.
    """
    name = resolve_backend_name(explicit)
    if name == BACKEND_NAME_RUST:
        if not url:
            raise ValueError(
                "_backend='rust' requires the account endpoint URL."
            )
        return RustBackend(endpoint=url, master_key=_master_key_or_raise(credential))
    return CorePythonBackend()

