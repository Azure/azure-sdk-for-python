# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Abstract async backend type plus re-exports of the data classes.

Same shape as the sync ABC, except ``execute`` is a coroutine so the
async container can ``await`` it without bridging threads.
``PreparedRequest`` and ``BackendResponse`` are shared with the sync
side (they carry pure data with no I/O).
"""
from __future__ import annotations

import abc
from typing import Optional

from azure.cosmos._backend.base import BackendResponse, PreparedRequest

__all__ = ["AsyncCosmosBackend", "PreparedRequest", "BackendResponse"]


class AsyncCosmosBackend(abc.ABC):
    """Abstract dispatch target for any async Cosmos operation.

    The async helper holds one of these by interface and awaits
    ``execute``. The operation kind is on ``prepared.op``; the backend
    branches on it.

    Until the helper layer takes over request prep and response parsing
    for every operation, ``execute`` may return ``None`` to signal
    "caller should run the legacy in-place implementation."
    """

    #: Short identifier surfaced in the startup INFO log and the
    #: per-request user-agent suffix. Subclasses set this from
    #: ``BACKEND_NAME_RUST`` etc.
    name: str = "abstract"

    @abc.abstractmethod
    async def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Issue a single async Cosmos operation.

        Dispatch on ``prepared.op``. Return ``None`` to let the caller
        run the legacy implementation, or a ``BackendResponse`` to have
        the caller parse the result.
        """
        ...

