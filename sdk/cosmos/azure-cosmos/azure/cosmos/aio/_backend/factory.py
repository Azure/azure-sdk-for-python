# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Factory that picks which async backend a single async client will use.

An async ``CosmosClient`` calls ``make_async_backend(...)`` exactly
once at construction time and stores the returned object. Every
subsequent ``create_item`` call on every container created by that
client awaits through the same instance.

Selection precedence (highest wins):

  1. The value the caller passed to the async client constructor as
     the private kwarg ``_backend=``.
  2. The value of the ``COSMOS_BACKEND`` environment variable.
  3. The default, ``core-python``.

If a value comes in that is not ``"core-python"`` or ``"rust"``, the
factory raises ``ValueError`` immediately at client construction time.
Failing loud is intentional — a typo'd value silently falling back to
the default would mask configuration drift in production.

The precedence and validation logic itself lives in
``azure.cosmos._backend.factory.resolve_backend_name`` so the sync and
async factories cannot drift apart. This module only owns the mapping
from a resolved name to the corresponding async backend class.
"""
from __future__ import annotations

from typing import Optional

from azure.cosmos._backend.constants import BACKEND_NAME_RUST
from azure.cosmos._backend.factory import resolve_backend_name

from .base import AsyncCosmosBackend
from .core_python import AsyncCorePythonBackend
from .rust import AsyncRustBackend


def make_async_backend(explicit: Optional[str]) -> AsyncCosmosBackend:
    """Build the single backend instance an async ``CosmosClient`` will hold.

    ``explicit`` is what the caller passed as ``_backend=`` (or
    ``None`` if they passed nothing — in which case the env var, then
    the default, are consulted). The returned object is either an
    ``AsyncCorePythonBackend`` or an ``AsyncRustBackend``.
    """
    name = resolve_backend_name(explicit)
    if name == BACKEND_NAME_RUST:
        return AsyncRustBackend()
    return AsyncCorePythonBackend()

