# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import TYPE_CHECKING, Optional

from ._version import VERSION

if TYPE_CHECKING:  # pragma: no cover
    from . import models
    from azure.core.credentials_async import AsyncTokenCredential


def from_langgraph(agent, credentials: Optional["AsyncTokenCredential"] = None, state_converter: Optional["models.LanggraphStateConverter"] = None):
    from .langgraph import LangGraphAdapter

    return LangGraphAdapter(agent, credentials=credentials, state_converter=state_converter)


from .tool_client import ToolClient


__all__ = ["from_langgraph", "ToolClient"]
__version__ = VERSION
