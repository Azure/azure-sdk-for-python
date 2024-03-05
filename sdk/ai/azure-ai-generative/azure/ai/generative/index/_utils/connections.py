# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MLIndex auth connection utilities."""
from typing import Optional

from azure.ai.generative.index._utils.logging import get_logger
from azure.ai.resources._index._utils.connections import get_connection_by_id_v2, get_metadata_from_connection

try:
    from azure.ai.resources.entities import BaseConnection
except Exception:
    BaseConnection = None  # type: ignore[misc,assignment]
try:
    from azure.ai.ml import MLClient
    from azure.ai.ml.entities import WorkspaceConnection
except Exception:
    MLClient = None
    WorkspaceConnection = None
try:
    from azure.core.credentials import TokenCredential
except Exception:
    TokenCredential = object  # type: ignore[misc,assignment]

logger = get_logger("connections")

def get_pinecone_environment(config, credential: Optional[TokenCredential] = None):
    """Get the Pinecone project environment from a connection."""
    connection_type = config.get("connection_type", None)
    if connection_type != "workspace_connection":
        raise ValueError(f"Unsupported connection type for Pinecone index: {connection_type}")

    connection_id = config.get("connection", {}).get("id")
    connection = get_connection_by_id_v2(connection_id, credential=credential)
    return get_metadata_from_connection(connection)["environment"]