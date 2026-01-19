# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import Optional, TYPE_CHECKING

from azure.ai.agentserver.core.application import PackageMetadata, set_current_app
from ._context import LanggraphRunContext
from ._version import VERSION
from .langgraph import LangGraphAdapter

if TYPE_CHECKING:  # pragma: no cover
    from .models.response_api_converter import ResponseAPIConverter
    from azure.core.credentials_async import AsyncTokenCredential


def from_langgraph(
    agent,
    credentials: Optional["AsyncTokenCredential"] = None,
    converter: Optional["ResponseAPIConverter"] = None
) -> "LangGraphAdapter":

    return LangGraphAdapter(agent, credentials=credentials, converter=converter)


__all__ = ["from_langgraph", "LanggraphRunContext"]
__version__ = VERSION

set_current_app(PackageMetadata.from_dist("azure-ai-agentserver-langgraph"))