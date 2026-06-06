# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Factory that picks which async backend a single async client will use.

Same precedence and validation as the sync factory (constructor kwarg
> ``COSMOS_BACKEND`` env var > default ``core-python``). The precedence
and validation logic itself is in
``azure.cosmos._backend.factory.resolve_backend_name`` so the sync and
async factories cannot drift apart.

When ``core-python`` is selected the factory returns ``None``; the async
helper treats absence of a backend as the signal to use the legacy
``client_connection.CreateItem`` path.
"""
from __future__ import annotations

from typing import Any, Optional

from azure.cosmos._backend.constants import BACKEND_NAME_RUST
from azure.cosmos._backend.factory import _master_key_or_raise, resolve_backend_name

from .base import AsyncCosmosBackend
from .rust import AsyncRustBackend


def make_async_backend(
    explicit: Optional[str],
    *,
    url: Optional[str] = None,
    credential: Any = None,
) -> Optional[AsyncCosmosBackend]:
    """Build the backend instance an async ``CosmosClient`` will hold.

    Returns an :class:`AsyncRustBackend` when Rust is selected, or
    ``None`` when core-python is selected. ``url`` and ``credential``
    are only consulted for the Rust branch.
    """
    name = resolve_backend_name(explicit)
    if name == BACKEND_NAME_RUST:
        if not url:
            raise ValueError(
                "_backend='rust' requires the account endpoint URL."
            )
        return AsyncRustBackend(endpoint=url, master_key=_master_key_or_raise(credential))
    return None


