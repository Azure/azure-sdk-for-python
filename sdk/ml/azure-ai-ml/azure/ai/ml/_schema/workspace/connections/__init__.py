# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from .workspace_connection import WorkspaceConnectionSchema

__all__ = ["WorkspaceConnectionSchema"]
