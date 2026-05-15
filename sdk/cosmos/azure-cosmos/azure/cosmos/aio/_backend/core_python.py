# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async core-python backend.
"Core-python" is the existing in-tree async path: an azure-core async
pipeline plus the ``CosmosClientConnection`` async helpers that have
shipped with this package for years. It is the default backend for the
async client and is *not* deprecated.
"""
from __future__ import annotations
from typing import Optional
from azure.cosmos._backend.constants import BACKEND_NAME_CORE_PYTHON
from .base import AsyncCosmosBackend, BackendResponse, PreparedRequest
class AsyncCorePythonBackend(AsyncCosmosBackend):
    """Routes async Cosmos calls through the existing azure-core stack.
    Today this class's ``execute`` returns ``None`` to tell the async
    helper "delegate to the existing in-place call." When the
    request-preparation helper and the response-parsing helper land,
    this method will build an azure-core ``HttpRequest`` from the
    ``PreparedRequest``, send it through
    ``client_connection.pipeline_client``, and return a populated
    ``BackendResponse``.
    """
    name = BACKEND_NAME_CORE_PYTHON
    async def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        # Returning None tells the async helper to fall through to the
        # existing in-place CreateItem path. The real adapter — building
        # an azure-core HttpRequest from the PreparedRequest and
        # awaiting it through the async pipeline — lands once request
        # prep and response parsing fully move into the helper layer.
        return None