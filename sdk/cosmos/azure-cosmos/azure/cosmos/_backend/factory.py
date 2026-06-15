# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Factory that picks which backend a single client will use.

``CosmosClient`` calls ``make_backend(...)`` exactly once at
construction time and stores the returned object.

Selection precedence (highest wins):

1. ``_backend=`` kwarg passed to the client constructor.
2. ``COSMOS_BACKEND`` environment variable.
3. Default: ``core-python``.

An invalid value raises ``ValueError`` at construction time.

When ``rust`` is selected the factory needs the account endpoint and a
master-key credential; other auth shapes are rejected upfront for now.
This is a temporary limitation -- once the Rust driver supports the other
auth shapes (TokenCredential, AAD, resource token), they will be accepted
too.

When ``core-python`` is selected the factory returns ``None``; the
helper layer treats absence-of-backend as the signal to use the legacy
``client_connection.CreateItem`` path.
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
from .rust import RustBackend


def resolve_backend_name(explicit: Optional[str]) -> str:
    """Apply the precedence rules above and return a name in ``VALID_BACKEND_NAMES``.

    Shared between the sync and async factories so the rules, valid
    values, and error message live in one place.
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
    """Pull a master-key string out of the credential, or raise ``ValueError``.

    The Rust binding's ``init_client`` only accepts master-key auth
    today. Other shapes (TokenCredential, resource token, AAD) need
    driver support that doesn't exist yet, so reject them at
    construction time rather than at first request.
    """
    if isinstance(credential, str):
        return credential
    if isinstance(credential, dict) and "masterKey" in credential:
        return credential["masterKey"]
    # TODO: Accept TokenCredential / AAD / resource-token auth here once the
    # Rust driver's init_client supports them; until then, reject upfront.
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
) -> Optional[CosmosBackend]:
    """Build the backend instance a sync ``CosmosClient`` will hold.

    Returns a :class:`RustBackend` when Rust is selected, or ``None``
    when core-python is selected. ``url`` and ``credential`` are only
    consulted for the Rust branch.
    """
    name = resolve_backend_name(explicit)
    if name == BACKEND_NAME_RUST:
        if not url:
            raise ValueError(
                "_backend='rust' requires the account endpoint URL."
            )
        return RustBackend(endpoint=url, master_key=_master_key_or_raise(credential))
    return None


