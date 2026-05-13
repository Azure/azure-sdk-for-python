# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async core-python backend.

"Core-python" is the existing in-tree async path: an azure-core async
pipeline plus the ``CosmosClientConnection`` async helpers that have
shipped with this package for years. It is the default backend for the
async client and is *not* deprecated. It is also the always-available
fallback the async dispatch site uses for any request whose kwargs the
Rust backend does not support yet (today: the two kwargs
``availability_strategy`` and ``retry_write``).
"""
from __future__ import annotations

from typing import Optional

from azure.cosmos._backend.constants import BACKEND_NAME_CORE_PYTHON

from .base import AsyncCosmosBackend, BackendResponse, PreparedRequest


class AsyncCorePythonBackend(AsyncCosmosBackend):
    """Routes async ``create_item`` calls through the existing azure-core stack.

    This is the default backend for the async ``CosmosClient`` and the
    always-available fallback for any request whose kwargs the Rust
    backend does not support yet.

    Today this class's ``create_item`` returns ``None`` to tell the
    async dispatch site "delegate to the existing in-place call." When
    the request-preparation helper and the response-parsing helper
    land, this method will build an azure-core ``HttpRequest`` from the
    ``PreparedRequest``, send it through
    ``client_connection.pipeline_client``, and return a populated
    ``BackendResponse``.
    """

    name = BACKEND_NAME_CORE_PYTHON

    async def create_item(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        # Returning None tells the async container's dispatch site to
        # fall through to the existing in-place create_item code path.
        # The real adapter — building an azure-core HttpRequest from
        # the PreparedRequest and awaiting it through the async
        # pipeline — lands once the helper layer exists.
        return None

