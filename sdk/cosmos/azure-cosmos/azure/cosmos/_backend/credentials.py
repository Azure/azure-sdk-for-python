# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Prepare the customer's credential in the Python wrapper for the binding.

Accept an account key or an object that obtains access tokens. An asynchronous
token credential is accepted only by the async client. Its adapter acquires a
bridge on first use, using the customer app's running event loop.

Both client types use this resolver. Unsupported credential forms, including
resource tokens that grant access to particular resources, fail during
construction. Resolving a credential does not fetch an access token or contact
the service backend to check whether the supplied credential grants access.
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Mapping
from collections.abc import Sequence as _AbcSequence
from contextlib import contextmanager
from typing import Any, Iterator, Optional, Tuple

from ._binding_adapter_shared import close_credential_bridge_quietly

_RESOURCE_TOKEN_ERROR = (
    "CosmosClient does not support resource-token (per-user / permission) credentials. "
    "This capability is intentionally excluded. "
    "Use an account key or a Microsoft Entra token credential."
)


def reject_resource_token_fields(credential: Mapping[str, Any]) -> None:
    """Reject removed authentication fields even alongside a supported credential."""
    if "resourceTokens" in credential or "permissionFeed" in credential:
        raise ValueError(_RESOURCE_TOKEN_ERROR)


def _is_async_credential(credential: Any) -> bool:
    """Detect credentials that need their application's event loop for token requests.

    Check for async get_token or get_token_info, including methods wrapped by
    decorators that expose __wrapped__. Also recognize credentials supporting
    async context entry. The async adapter wraps the retained credential on
    first use rather than passing an async method as a synchronous token method.
    """
    for attr in ("get_token", "get_token_info"):
        method = getattr(credential, attr, None)
        if method is None:
            continue
        if asyncio.iscoroutinefunction(method) or inspect.iscoroutinefunction(method):
            return True
        unwrapped = inspect.unwrap(method) if callable(method) else method
        if asyncio.iscoroutinefunction(unwrapped) or inspect.iscoroutinefunction(
            unwrapped
        ):
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


def validate_credential(credential: Any) -> None:
    """Validate supported credentials without acquiring a bridge or contacting the service."""
    if isinstance(credential, Mapping):
        reject_resource_token_fields(credential)
    if isinstance(credential, str):
        if not credential:
            raise ValueError("The account key must be a non-empty string.")
        return
    if isinstance(credential, Mapping) and "masterKey" in credential:
        master_key = credential["masterKey"]
        if not isinstance(master_key, str) or not master_key:
            # Report an invalid key at client construction, before driver creation.
            raise ValueError(
                "CosmosClient requires the 'masterKey' entry to be a non-empty string."
            )
        return
    if _is_async_credential(credential):
        return
    get_token = getattr(credential, "get_token", None)
    if callable(get_token):
        return
    if _is_resource_token_credential(credential):
        raise ValueError(_RESOURCE_TOKEN_ERROR)
    raise ValueError(
        "CosmosClient requires a master-key credential (a string, or a dict "
        "with a 'masterKey' entry) or a Microsoft Entra token credential "
        "(synchronous or asynchronous). Resource-token authentication is intentionally excluded."
    )


def resolve_credential(
    credential: Any,
    *,
    allow_async: bool = False,
) -> Tuple[Optional[str], Optional[Any]]:
    """Retain a supported credential; async adapters bind its loop on first use."""
    validate_credential(credential)
    if isinstance(credential, str):
        return credential, None
    if isinstance(credential, Mapping) and "masterKey" in credential:
        return credential["masterKey"], None
    if _is_async_credential(credential):
        if not allow_async:
            raise TypeError(
                "Synchronous CosmosClient requires a synchronous token credential. "
                "Use azure.cosmos.aio.CosmosClient with an async credential."
            )
        return None, credential
    return None, credential


@contextmanager
def resolved_credential(
    credential: Any,
    *,
    allow_async: bool = False,
) -> Iterator[Tuple[Optional[str], Optional[Any]]]:
    """Validate factory inputs without acquiring a loop or fetching a token.

    Async credentials remain caller-owned. If an internal bridge was supplied
    directly, release that acquired use on failure, never the customer's credential.
    """
    master_key, token_credential = resolve_credential(credential, allow_async=allow_async)
    try:
        yield master_key, token_credential
    except BaseException:
        close_credential_bridge_quietly(token_credential)
        raise
