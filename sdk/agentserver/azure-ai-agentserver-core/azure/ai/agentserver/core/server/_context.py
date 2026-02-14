# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import AsyncContextManager, ClassVar, Optional

from azure.ai.agentserver.core.tools import FoundryToolRuntime


class AgentServerContext(AsyncContextManager["AgentServerContext"]):
    _INSTANCE: ClassVar[Optional["AgentServerContext"]] = None

    def __init__(self, tool_runtime: FoundryToolRuntime):
        self._tool_runtime = tool_runtime

        self.__class__._INSTANCE = self

    @classmethod
    def get(cls) -> "AgentServerContext":
        if cls._INSTANCE is None:
            raise ValueError("AgentServerContext has not been initialized.")
        return cls._INSTANCE

    @property
    def tools(self) -> FoundryToolRuntime:
        return self._tool_runtime

    async def __aenter__(self) -> "AgentServerContext":
        await self._tool_runtime.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._tool_runtime.__aexit__(exc_type, exc_value, traceback)
