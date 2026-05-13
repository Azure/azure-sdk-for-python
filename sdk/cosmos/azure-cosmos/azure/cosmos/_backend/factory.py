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
"""
from __future__ import annotations

import os
from typing import Optional

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


def make_backend(explicit: Optional[str]) -> CosmosBackend:
    """Build the single backend instance a sync ``CosmosClient`` will hold.

    ``explicit`` is what the caller passed as ``_backend=`` (or ``None`` if
    they passed nothing — in which case the env var, then the default, are
    consulted). The returned object is either a ``CorePythonBackend`` or a
    ``RustBackend``.
    """
    name = resolve_backend_name(explicit)
    if name == BACKEND_NAME_RUST:
        return RustBackend()
    return CorePythonBackend()

