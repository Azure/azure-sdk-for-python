# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from .workspace_hub import WorkspaceHubSchema

__all__ = ["WorkspaceHubSchema"]
