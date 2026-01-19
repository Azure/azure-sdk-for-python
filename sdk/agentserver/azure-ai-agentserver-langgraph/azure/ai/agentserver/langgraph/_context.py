# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from dataclasses import dataclass
from typing import TYPE_CHECKING

from langgraph.runtime import get_runtime

from .tools._context import FoundryToolContext


@dataclass
class LanggraphRunContext:

    tools: FoundryToolContext

    @classmethod
    def get_current(cls) -> "LanggraphRunContext":
        lg_runtime = get_runtime(cls)
        return lg_runtime.context
