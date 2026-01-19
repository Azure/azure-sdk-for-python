# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import Any, Dict

from ._user import UserProvider
from ..client._client import FoundryToolClient
from ..client._models import ResolvedFoundryTool


class FoundryToolInvoker(ABC):
    """Abstract base class for Foundry tool invokers."""

    @property
    @abstractmethod
    def resolved_tool(self) -> ResolvedFoundryTool:
        """Get the resolved tool definition.

        :return: The tool definition.
        :rtype: ResolvedFoundryTool
        """
        raise NotImplementedError

    @abstractmethod
    async def invoke(self, arguments: Dict[str, Any]) -> Any:
        """Invoke the tool with the given arguments.

        :param arguments: The arguments to pass to the tool.
        :type arguments: Dict[str, Any]
        :return: The result of the tool invocation
        :rtype: Any
        """
        raise NotImplementedError


class DefaultFoundryToolInvoker(FoundryToolInvoker):
    """Default implementation of FoundryToolInvoker."""

    def __init__(self,
                 resolved_tool: ResolvedFoundryTool,
                 client: FoundryToolClient,
                 user_provider: UserProvider,
                 agent_name: str):
        self._resolved_tool = resolved_tool
        self._client = client
        self._user_provider = user_provider
        self._agent_name = agent_name

    @property
    def resolved_tool(self) -> ResolvedFoundryTool:
        """Get the resolved tool definition.

        :return: The tool definition.
        :rtype: ResolvedFoundryTool
        """
        return self._resolved_tool

    async def invoke(self, arguments: Dict[str, Any]) -> Any:
        """Invoke the tool with the given arguments.

        :param arguments: The arguments to pass to the tool
        :type arguments: Dict[str, Any]
        :return: The result of the tool invocation
        :rtype: Any
        """
        user = await self._user_provider.get_user()
        result = await self._client.invoke_tool(self._resolved_tool, arguments, self._agent_name, user)
        return result
