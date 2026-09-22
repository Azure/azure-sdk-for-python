# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Prepare the customer's credential in the Python wrapper for the binding.

Accept a master key or an object that obtains access tokens. An async token
credential needs a bridge, an object that runs its token requests on a
background thread and lets the binding wait for their results.

Both client types use this resolver. Unsupported credential forms, including
resource tokens that grant access to particular resources, fail during
construction. Resolving a credential does not fetch a token, validate the key,
or check permissions with the service backend.
"""
from __future__ import annotations

import asyncio
import inspect
from collections.abc import Mapping
from collections.abc import Sequence as _AbcSequence
from contextlib import contextmanager
from typing import Any, Iterator, Optional, Tuple

from ._async_credential_bridge import AsyncTokenCredentialBridge
from ._shared import close_credential_bridge_quietly


def _is_async_credential(credential: Any) -> bool:
    """Detect credentials that need a background event loop for token requests.

    Check for async get_token or get_token_info, including methods wrapped by
    decorators that expose __wrapped__. Also recognize credentials supporting
    async context entry. The resolver then wraps the credential rather than
    passing an async method where a synchronous token result is expected.
    """
    for attr in ("get_token", "get_token_info"):
        method = getattr(credential, attr, None)
        if method is None:
            continue
        if asyncio.iscoroutinefunction(method) or inspect.iscoroutinefunction(method):
            return True
        unwrapped = inspect.unwrap(method) if callable(method) else method
        if asyncio.iscoroutinefunction(unwrapped) or inspect.iscoroutinefunction(unwrapped):
            return True
    # Also recognize async context entry when the method check did not detect it.
    if hasattr(credential, "__aenter__") and (
        hasattr(credential, "get_token") or hasattr(credential, "get_token_info")
    ):
        return True
    return False


def _is_resource_token_credential(credential: Any) -> bool:
    """Identify inputs treated as unsupported resource-token credentials.

    These include dictionaries without masterKey and sequences such as lists
    of permission entries. The resolver checks master keys and token methods
    first, then uses this check to report why the remaining input is rejected.
    """
    if isinstance(credential, str):
        return False
    if isinstance(credential, Mapping):
        # The resolver already handled dictionaries containing masterKey.
        return "masterKey" not in credential
    if isinstance(credential, bytes):
        return False
    # Accept sequences for this check, not every iterable: a custom credential
    # may support iteration without being a list of permission entries.
    return isinstance(credential, _AbcSequence)


def resolve_credential(credential: Any) -> Tuple[Optional[str], Optional[Any]]:
    """Return (master_key, token_credential) with exactly one entry set.

    A nonempty string, or a dictionary with a nonempty masterKey string, selects
    key authentication. An object with a synchronous get_token is passed through.
    Async credentials are wrapped in AsyncTokenCredentialBridge instead.

    Resource-token authentication is intentionally excluded, not pending Rust
    driver support. Those forms and other unrecognized inputs raise ValueError here.
    Getting a token or using it with the service backend can still fail later.
    """
    if isinstance(credential, str):
        if not credential:
            raise ValueError(
                "The account key must be a non-empty string."
            )
        return credential, None
    if isinstance(credential, Mapping) and "masterKey" in credential:
        master_key = credential["masterKey"]
        if not isinstance(master_key, str) or not master_key:
            # Report an invalid key at client construction, before driver creation.
            raise ValueError(
                "The Rust binding requires the 'masterKey' entry to be a non-empty string."
            )
        return master_key, None
    # Async methods are callable too. Wrap them before accepting a plain get_token.
    if _is_async_credential(credential):
        return None, AsyncTokenCredentialBridge.acquire(credential)
    get_token = getattr(credential, "get_token", None)
    if callable(get_token):
        return None, credential
    if _is_resource_token_credential(credential):
        raise ValueError(
            "The Rust binding does not support resource-token (per-user / "
            "permission) credentials. This capability is intentionally excluded. "
            "Use an account key or a Microsoft Entra token credential."
        )
    raise ValueError(
        "The Rust binding requires a master-key credential (a string, or a dict "
        "with a 'masterKey' entry) or a Microsoft Entra token credential "
        "(synchronous or asynchronous). Resource-token authentication is intentionally excluded."
    )


@contextmanager
def resolved_credential(
    credential: Any,
) -> Iterator[Tuple[Optional[str], Optional[Any]]]:
    """Prepare a credential and release its bridge if Python client setup fails.

    An async bridge keeps a reference to the credential even before its thread
    starts. On success, the Python wrapper object must release its use
    of that bridge. On failure, release it here and propagate the original error
    without closing the customer's credential.
    """
    master_key, token_credential = resolve_credential(credential)
    try:
        yield master_key, token_credential
    except BaseException:
        close_credential_bridge_quietly(token_credential)
        raise