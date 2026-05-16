# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Abstract async backend type plus re-exports of the data classes.

This module defines the async dispatch contract — the ABC every async
backend implements and the data classes that flow across it. The
contract has the same shape as the sync one (``execute(prepared)``
plus a ``name`` identifier) with one difference: ``execute`` here is
a coroutine, so the async container can ``await`` it without
bridging threads.

The ``PreparedRequest`` and ``BackendResponse`` data classes are
imported from the sync module and re-exported here so that the rest of
the async-side code can keep its imports local. Those two classes hold
pure data with no I/O, so there is no separate async/sync version of
them — sharing one definition keeps the wire-format contract aligned
across both sides of the package.
"""
from __future__ import annotations

import abc
from typing import Optional

from azure.cosmos._backend.base import BackendResponse, PreparedRequest

__all__ = ["AsyncCosmosBackend", "PreparedRequest", "BackendResponse"]


class AsyncCosmosBackend(abc.ABC):
    """Abstract dispatch target for any async Cosmos operation.

    Every async backend (today: ``AsyncRustBackend`` only)
    inherits from this class. The async helper holds one of these by
    interface and awaits ``execute`` on it without knowing which
    concrete backend it has. The operation kind is on ``prepared.op``;
    the backend is the one place that branches on it.

    Today, request preparation and response parsing still live in their
    existing locations inside the async client connection. So a backend
    that returns ``None`` from ``execute`` is interpreted as "I have
    nothing to return; the caller should run its existing in-place
    implementation." That contract goes away once the helper layer
    takes over request prep and response parsing — at that point every
    backend will return a real ``BackendResponse`` and the
    ``Optional`` annotations on the method signature drop.
    """

    #: Short identifier for this backend, surfaced in two places: the
    #: ``INFO`` log line emitted at client construction, and the
    #: per-request user-agent suffix (``backend=<name>``). The two valid
    #: values are defined in ``azure.cosmos._backend.constants`` —
    #: ``BACKEND_NAME_CORE_PYTHON`` and ``BACKEND_NAME_RUST``. Concrete
    #: subclasses set this to one of those two constants.
    name: str = "abstract"

    @abc.abstractmethod
    async def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Issue a single async Cosmos operation and return its result.

        The operation kind is on ``prepared.op``; the backend dispatches
        on it. Returning ``None`` (the temporary contract until the
        helper layer takes over request prep) tells the caller to use
        its existing in-place implementation. Returning a
        ``BackendResponse`` tells the caller to use that response
        directly. ``prepared`` may be ``None`` for as long as the
        caller still owns request preparation.
        """
        ...

