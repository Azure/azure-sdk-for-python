# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import Optional, Union, TYPE_CHECKING

from azure.ai.agentserver.core.application import PackageMetadata, set_current_app
from azure.ai.agentserver.core.logger import get_project_endpoint

from ._context import LanggraphRunContext
from ._version import VERSION
from .langgraph import LangGraphAdapter

if TYPE_CHECKING:  # pragma: no cover
    from langgraph.graph.state import CompiledStateGraph
    from .models.response_api_converter import ResponseAPIConverter
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.credentials import TokenCredential


def from_langgraph(
    agent: "CompiledStateGraph",
    /,
    credentials: Optional[Union["AsyncTokenCredential", "TokenCredential"]] = None,
    converter: Optional["ResponseAPIConverter"] = None,
    *,
    managed_checkpoints: bool = False,
    project_endpoint: Optional[str] = None,
) -> "LangGraphAdapter":
    """Create a LangGraph adapter for Azure AI Agent Server.

    :param agent: The compiled LangGraph state graph.
    :type agent: CompiledStateGraph
    :param credentials: Azure credentials for authentication.
    :type credentials: Optional[Union[AsyncTokenCredential, TokenCredential]]
    :param converter: Custom response converter.
    :type converter: Optional[ResponseAPIConverter]
    :param managed_checkpoints: If True, use Azure AI Foundry managed checkpoint storage.
        When enabled, the graph's checkpointer will be replaced with FoundryCheckpointSaver.
    :type managed_checkpoints: bool
    :param project_endpoint: The Azure AI Foundry project endpoint. If not provided,
        will be read from AZURE_AI_PROJECT_ENDPOINT environment variable.
        Example: "https://<resource>.services.ai.azure.com/api/projects/<project-id>"
    :type project_endpoint: Optional[str]
    :return: A LangGraphAdapter instance.
    :rtype: LangGraphAdapter
    :raises ValueError: If managed_checkpoints=True but required parameters are missing.
    """
    if managed_checkpoints:
        # Validate requirements
        resolved_endpoint = get_project_endpoint() or project_endpoint
        if not resolved_endpoint:
            raise ValueError(
                "project_endpoint is required when managed_checkpoints=True. "
                "Set AZURE_AI_PROJECT_ENDPOINT environment variable or pass project_endpoint parameter."
            )
        if not credentials:
            raise ValueError("credentials are required when managed_checkpoints=True")

        # Create and attach Foundry checkpointer
        from azure.core.credentials_async import AsyncTokenCredential
        from azure.ai.agentserver.core.checkpoints import FoundryCheckpointClient
        from .checkpointer import FoundryCheckpointSaver

        if not isinstance(credentials, AsyncTokenCredential):
            raise TypeError(
                "managed_checkpoints requires an AsyncTokenCredential. "
                "Please use an async credential like DefaultAzureCredential from azure.identity.aio."
            )

        client = FoundryCheckpointClient(resolved_endpoint, credentials)
        checkpointer = FoundryCheckpointSaver(client)

        # Validate and replace the checkpointer directly (preserves all other compile parameters)
        from langgraph.types import ensure_valid_checkpointer
        agent.checkpointer = ensure_valid_checkpointer(checkpointer)

    return LangGraphAdapter(agent, credentials=credentials, converter=converter)


__all__ = ["from_langgraph", "LanggraphRunContext"]
__version__ = VERSION

set_current_app(PackageMetadata.from_dist("azure-ai-agentserver-langgraph"))
