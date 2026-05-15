# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Sync core-python backend.

"Core-python" is the existing in-tree path: an azure-core pipeline plus
the ``CosmosClientConnection`` helpers that have shipped with this
package for years. It is the default and is *not* deprecated.
"""
from __future__ import annotations

from typing import Optional

from .base import BackendResponse, CosmosBackend, PreparedRequest
from .constants import BACKEND_NAME_CORE_PYTHON


class CorePythonBackend(CosmosBackend):
    """Routes Cosmos calls through the existing azure-core stack.

    Today this class's ``execute`` returns ``None`` to tell the
    dispatch site "delegate to the existing in-place call." When the
    request-preparation helper and the response-parsing helper land,
    this method will build an azure-core ``HttpRequest`` from the
    ``PreparedRequest``, send it through
    ``client_connection.pipeline_client``, and return a populated
    ``BackendResponse``.
    """

    name = BACKEND_NAME_CORE_PYTHON

    def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        # Returning None tells the helper to fall through to the
        # existing in-place CreateItem path. The real adapter lands
        # once request prep and response parsing fully move into the
        # helper layer.
        return None

