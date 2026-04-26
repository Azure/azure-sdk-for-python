# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from typing import TYPE_CHECKING, Optional

from ._version import VERSION

if TYPE_CHECKING:  # pragma: no cover
    from . import models


def from_langgraph(agent, state_converter: Optional["models.LanggraphStateConverter"] = None):
    from .langgraph import LangGraphAdapter

    return LangGraphAdapter(agent, state_converter=state_converter)


__all__ = ["from_langgraph"]
__version__ = VERSION
