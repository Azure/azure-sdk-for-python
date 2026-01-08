# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import Any, List, Mapping, MutableMapping, Optional

from cachetools import TTLCache

from ._user import UserProvider
from ..client._client import FoundryToolClient
from ..client._models import FoundryTool, FoundryToolDetails, FoundryToolSource, ResolvedFoundryTool, UserInfo


class FoundryToolCatalog(ABC):
    """Base class for Foundry tool catalogs."""
    def __init__(self, user_provider: UserProvider):
        self._user_provider = user_provider

    async def get(self, tool: FoundryTool) -> Optional[ResolvedFoundryTool]:
        """Gets a Foundry tool by its definition.

        :param tool: The Foundry tool to resolve.
        :type tool: FoundryTool
        :return: The resolved Foundry tool.
        :rtype: Optional[ResolvedFoundryTool]
        """
        tools = await self.list([tool])
        return tools[0] if tools else None

    @abstractmethod
    async def list(self, tools: List[FoundryTool]) -> List[ResolvedFoundryTool]:
        """Lists all available Foundry tools.

        :param tools: The list of Foundry tools to resolve.
        :type tools: List[FoundryTool]
        :return: A list of resolved Foundry tools.
        :rtype: List[ResolvedFoundryTool]
        """
        raise NotImplementedError


class CachedFoundryToolCatalog(FoundryToolCatalog, ABC):

    def __init__(self, user_provider: UserProvider):
        super().__init__(user_provider)
        self._cache: MutableMapping[FoundryTool, FoundryToolDetails] = self._create_cache()

    def _create_cache(self) -> MutableMapping[FoundryTool, FoundryToolDetails]:
        return TTLCache(maxsize=1024, ttl=600)

    def _get_key(self, user: Optional[UserInfo], tool: FoundryTool) -> Any:
        if tool.source is FoundryToolSource.HOSTED_MCP:
            return tool
        return user, tool

    async def list(self, tools: List[FoundryTool]) -> List[ResolvedFoundryTool]:
        resolved_tools = []
        tools_to_fetch = []

        user = await self._user_provider.get_user()
        for tool in tools:
            key = self._get_key(user, tool)

            cached_tool: Optional[FoundryToolDetails] = self._cache.get(key)
            if cached_tool:
                resolved_tools.append(ResolvedFoundryTool(definition=tool, details=cached_tool))
            else:
                tools_to_fetch.append(tool)

        if tools_to_fetch:
            fetched_tools = await self._fetch_tools(tools_to_fetch, user)
            for tool, detail in fetched_tools.items():
                # no lock for
                self._cache[self._get_key(user, tool)] = detail
                resolved_tools.append(ResolvedFoundryTool(definition=tool, details=detail))
        return resolved_tools

    @abstractmethod
    async def _fetch_tools(self,
                           tools: List[FoundryTool],
                           user: Optional[UserInfo]) -> Mapping[FoundryTool, FoundryToolDetails]:
        raise NotImplementedError


class DefaultFoundryToolCatalog(CachedFoundryToolCatalog):
    def __init__(self, client: FoundryToolClient, user_provider: UserProvider, agent_name: str):
        super().__init__(user_provider)
        self._client = client
        self._agent_name = agent_name

    async def _fetch_tools(self,
                           tools: List[FoundryTool],
                           user: Optional[UserInfo]) -> Mapping[FoundryTool, FoundryToolDetails]:
        return await self._client.list_tools(tools, user, self._agent_name)
