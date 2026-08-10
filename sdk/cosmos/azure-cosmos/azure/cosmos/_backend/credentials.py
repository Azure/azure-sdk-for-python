# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Sorting the customer's credential into something the Rust driver can use.

A customer proves who they are in one of several ways: a master key string, a
dict holding one, an ``azure-identity`` token credential (sync or async), or a
set of per-user resource tokens. The Rust driver accepts only the first two
shapes, and only a *synchronous* token credential -- it signs requests on a
plain worker thread with no event loop running.

:func:`resolve_credential` is the single place that sorts those shapes out. It
returns exactly one of a master key or a synchronous token credential, wrapping
an async credential in an :class:`AsyncTokenCredentialBridge` so it still works,
and rejecting what the driver genuinely cannot do -- at ``CosmosClient(...)``,
where the customer can see which argument was wrong, rather than on their first
database call.

Both the sync factory (:mod:`~azure.cosmos._backend.factory`) and the async one
(:mod:`~azure.cosmos.aio._backend.factory`) call it, so the two clients accept
and reject exactly the same credentials.
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
    """Detect whether the customer's credential logs in asynchronously: its
    ``get_token`` or ``get_token_info`` is a coroutine, or it is an
    ``azure.identity.aio``-style async context manager.

    Why it matters: the Rust driver calls ``get_token`` on a plain worker thread
    that has no async event loop, so an async credential would crash there.
    Detecting it lets the next step (:func:`resolve_credential`) wrap it safely
    in an :class:`AsyncTokenCredentialBridge`, which supplies that event loop,
    instead of calling it directly. The token method is unwrapped first in case
    it is decorated.
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
    # Async-only credentials are async context managers; treat that as async even
    # if the token-method check above did not catch it.
    if hasattr(credential, "__aenter__") and (
        hasattr(credential, "get_token") or hasattr(credential, "get_token_info")
    ):
        return True
    return False


def _is_resource_token_credential(credential: Any) -> bool:
    """Detect the "per-user permission token" style of credential, rather than a
    master key or a token credential.

    Why: the Rust driver has no code to log in that way yet, so this lets the
    factory reject it clearly (in :func:`resolve_credential`) instead of failing
    deep inside the driver later. These take the shape of a mapping of resource
    link to token (without a ``masterKey`` entry, which is handled earlier), a
    mapping with ``resourceTokens`` / ``permissionFeed`` keys, or a concrete
    sequence (list / tuple) of permission entries.
    """
    if isinstance(credential, str):
        return False
    if isinstance(credential, Mapping):
        # A master-key dict is resolved as a master key before this is reached;
        # any other mapping shape is resource/permission tokens.
        return "masterKey" not in credential
    if isinstance(credential, bytes):
        return False
    # A permission feed is a concrete sequence (list / tuple) of permission
    # entries. Restrict to Sequence rather than any Iterable so an unusual custom
    # credential object that merely happens to be iterable is not mislabeled a
    # resource-token credential -- it falls through to the generic
    # "unsupported shape" message instead.
    return isinstance(credential, _AbcSequence)


def resolve_credential(credential: Any) -> Tuple[Optional[str], Optional[Any]]:
    """The credential sorter: turn whatever the customer passed into exactly one
    of a master key or a synchronous token credential, or raise ``ValueError``.

    Without it: an unsupported login would blow up on the first request with an
    opaque error, not at the line where the customer created the client. So this
    rejects anything Rust can't do upfront -- at construction. Returns
    ``(master_key, token_credential)`` with exactly one entry set:

    * a ``str`` or a dict with a ``'masterKey'`` entry -> master key (rejected if
      empty or, in the dict case, not a non-empty string);
    * an object with a synchronous ``get_token`` (e.g. an ``azure-identity``
      credential) -> token credential, forwarded to the driver, which calls
      ``get_token`` during request signing;
    * an *async* token credential (coroutine ``get_token`` / ``get_token_info``,
      or the ``azure.identity.aio`` async-context-manager shape) is first wrapped
      in an :class:`AsyncTokenCredentialBridge`, which drives its coroutine on a
      dedicated event-loop thread and presents the synchronous ``get_token`` the
      driver's worker thread calls -- so async credentials work on the Rust path
      with no driver change;
    * a resource-token / permission-feed credential (per-user scoped tokens) is
      rejected: the Rust driver has no resource-token auth support yet;
    * anything else (``None`` and unrecognized shapes) is rejected.
    """
    if isinstance(credential, str):
        if not credential:
            raise ValueError(
                "_backend='rust' requires a non-empty master-key string."
            )
        return credential, None
    if isinstance(credential, Mapping) and "masterKey" in credential:
        master_key = credential["masterKey"]
        if not isinstance(master_key, str) or not master_key:
            # A non-string (or empty) masterKey would otherwise be accepted here and
            # fail later in a murkier place (credential-key computation or the
            # driver). Reject it at construction with a clear message.
            raise ValueError(
                "_backend='rust' requires the 'masterKey' entry to be a non-empty "
                "string; got {!r}.".format(master_key)
            )
        return master_key, None
    # Check async *before* the sync get_token acceptance, since an async
    # credential also exposes a (coroutine) get_token. Wrap it rather than reject
    # it: the bridge drives the coroutine on its own event-loop thread and exposes
    # the synchronous get_token the driver calls, so async credentials work with no
    # driver change.
    if _is_async_credential(credential):
        return None, AsyncTokenCredentialBridge.acquire(credential)
    get_token = getattr(credential, "get_token", None)
    if callable(get_token):
        return None, credential
    if _is_resource_token_credential(credential):
        raise ValueError(
            "_backend='rust' does not support resource-token (per-user / "
            "permission) credentials yet -- that needs Rust-driver auth support "
            "that isn't available. Use a master-key credential or a synchronous "
            "token credential, or the core-python backend."
        )
    # Falls through for None and any other unrecognized shape.
    raise ValueError(
        "_backend='rust' requires a master-key credential (a string, or a dict "
        "with a 'masterKey' entry) or a synchronous token credential. The Rust "
        "backend does not support resource-token auth."
    )


@contextmanager
def resolved_credential(
    credential: Any,
) -> Iterator[Tuple[Optional[str], Optional[Any]]]:
    """Sort the customer's credential as :func:`resolve_credential` does, and undo
    the wrapping if the caller fails to finish building its backend.

    An async credential is not sorted for free: :func:`resolve_credential` wraps it
    in an :class:`AsyncTokenCredentialBridge`, which starts a background event-loop
    thread and takes a hold on the shared bridge for that credential object. Only a
    backend that is successfully constructed will ever close that hold.

    Everything the factories do after sorting the credential can still raise -- an
    unsupported consistency level or an out-of-range timeout while building the
    client config, a process-wide proxy or transport-timeout conflict, or a strict
    isolation clash while registering. Without this helper each of those turns a
    plain ``ValueError`` at ``CosmosClient(...)`` into a permanently leaked thread
    that also pins the customer's credential object alive for the life of the
    process, with nothing left holding a reference that could ever release it.

    So the caller builds its backend inside this context manager. On success the
    bridge is left open for the backend that now owns it; on any exception the hold
    is released and the original error propagates unchanged.
    """
    master_key, token_credential = resolve_credential(credential)
    try:
        yield master_key, token_credential
    except BaseException:
        close_credential_bridge_quietly(token_credential)
        raise