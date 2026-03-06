# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=docstring-should-be-keyword
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import Optional, Union, TYPE_CHECKING

from azure.ai.agentserver.core.application import PackageMetadata, set_current_app

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
) -> "LangGraphAdapter":
    """
    Create a LangGraph adapter for Azure AI Agent Server.

    :param agent: The compiled LangGraph state graph. To use persistent checkpointing,
                    compile the graph with a checkpointer via ``builder.compile(checkpointer=saver)``.
    :type agent: CompiledStateGraph
    :param credentials: Azure credentials for authentication.
    :type credentials: Optional[Union[AsyncTokenCredential, TokenCredential]]
    :param converter: Custom response converter.
    :type converter: Optional[ResponseAPIConverter]
    :return: A LangGraphAdapter instance.
    :rtype: LangGraphAdapter
    """
    return LangGraphAdapter(agent, credentials=credentials, converter=converter)


__all__ = ["from_langgraph", "LanggraphRunContext"]
__version__ = VERSION

set_current_app(PackageMetadata.from_dist("azure-ai-agentserver-langgraph"))
