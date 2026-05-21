# Re-export WorkspaceClient from the generated sub-client
from .azure.ai.discovery import WorkspaceClient  # type: ignore

__all__ = ["WorkspaceClient"]
