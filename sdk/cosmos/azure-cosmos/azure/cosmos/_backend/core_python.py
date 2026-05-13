# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Sync core-python backend.

"Core-python" is the existing in-tree path: an azure-core pipeline plus
the ``CosmosClientConnection`` helpers that have shipped with this
package for years. It is the default and is *not* deprecated. It is also
the always-available fallback the dispatch site uses for any request
whose kwargs the Rust backend does not support yet (today: the two
kwargs ``availability_strategy`` and ``retry_write``).
"""
from __future__ import annotations

from typing import Optional

from .base import BackendResponse, CosmosBackend, PreparedRequest
from .constants import BACKEND_NAME_CORE_PYTHON


class CorePythonBackend(CosmosBackend):
    """Routes ``create_item`` calls through the existing azure-core stack.

    Today this class's ``create_item`` returns ``None`` to tell the
    dispatch site "delegate to the existing in-place call." When the
    request-preparation helper and the response-parsing helper land,
    this method will build an azure-core ``HttpRequest`` from the
    ``PreparedRequest``, send it through
    ``client_connection.pipeline_client``, and return a populated
    ``BackendResponse``.
    """

    name = BACKEND_NAME_CORE_PYTHON

    def create_item(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        # Returning None tells the container's dispatch site to fall
        # through to the existing in-place create_item code path. The
        # real adapter lands once the helper layer exists.
        return None

