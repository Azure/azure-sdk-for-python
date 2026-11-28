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

# Recognize asyncio-marked credential methods, not transport sleeps.
import asyncio  # pylint: disable=do-not-import-asyncio
import inspect
from collections.abc import Mapping
from collections.abc import Sequence as _AbcSequence
from typing import Any, Optional, Tuple

_RESOURCE_TOKEN_ERROR = (
    "CosmosClient does not support resource-token (per-user / permission) credentials. "
    "This capability is intentionally excluded. "
    "Use an account key or a Microsoft Entra token credential."
)


def reject_resource_token_fields(credential: Mapping[str, Any]) -> None:
    """Reject removed authentication fields even alongside a supported credential.

    :param credential: Credential mapping to check for removed resource-token fields.
    :type credential: typing.Mapping[str, typing.Any]
    """
    if "resourceTokens" in credential or "permissionFeed" in credential:
        raise ValueError(_RESOURCE_TOKEN_ERROR)


def _is_coroutine_method(credential: Any, name: str) -> bool:
    """Recognize async methods, including decorated and asyncio-marked wrappers.

    :param credential: Object whose token method is inspected without invoking it.
    :type credential: typing.Any
    :param name: Method name to inspect.
    :type name: str
    :return: Whether the method or its unwrapped implementation is a coroutine function.
    :rtype: bool
    """
    method = getattr(credential, name, None)
    if method is None:
        return False
    if asyncio.iscoroutinefunction(method) or inspect.iscoroutinefunction(method):
        return True
    unwrapped = inspect.unwrap(method) if callable(method) else method
    return asyncio.iscoroutinefunction(unwrapped) or inspect.iscoroutinefunction(unwrapped)


def _is_async_credential(credential: Any) -> bool:
    """Detect credentials routed through their application's event loop.

    Check for async get_token or get_token_info, including methods wrapped by
    decorators that expose __wrapped__. Also recognize credentials supporting
    async context entry as a hint for opaque wrappers returning awaitables.
    That hint does not prove the token result is awaitable; the bridge checks
    the result on first use rather than invoking customer code during validation.

    :param credential: Credential candidate to inspect without obtaining tokens.
    :type credential: typing.Any
    :return: Whether the credential requires asynchronous handling.
    :rtype: bool
    """
    for attr in ("get_token", "get_token_info"):
        if _is_coroutine_method(credential, attr):
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

    :param credential: Credential candidate remaining after supported forms are considered.
    :type credential: typing.Any
    :return: Whether the value has an unsupported resource-token credential shape.
    :rtype: bool
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
    """Check that the credential has a supported form.

    Supported forms are an account key string, a dict with a "masterKey" entry,
    or a Microsoft Entra token credential (sync or async). Raise ValueError for
    anything else, including a blank key and resource tokens. This does not
    contact the service, so it cannot tell whether the key is correct.

    :param credential: Account key, master-key mapping, or token credential to validate.
    :type credential: typing.Any
    :raises ValueError: The credential is blank, a resource token, or an unsupported type.
    """
    if isinstance(credential, Mapping):
        reject_resource_token_fields(credential)
    if isinstance(credential, str):
        if not credential.strip():
            raise ValueError("The account key must be a non-empty string.")
        return
    if isinstance(credential, Mapping) and "masterKey" in credential:
        master_key = credential["masterKey"]
        if not isinstance(master_key, str) or not master_key.strip():
            # Reject a blank or non-string key before any request is sent.
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
    """Retain a supported credential; async adapters bind its loop on first use.

    :param credential: Account key, master-key mapping, or token credential.
    :type credential: typing.Any
    :keyword allow_async: Whether asynchronous token credentials are accepted.
    :paramtype allow_async: bool
    :return: Account key and token credential pair, with exactly one non-None entry.
    :rtype: tuple[typing.Optional[str], typing.Any]
    """
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
