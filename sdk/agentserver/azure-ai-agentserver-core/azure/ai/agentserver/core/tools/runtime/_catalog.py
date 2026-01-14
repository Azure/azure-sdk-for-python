# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Dict, List, Mapping, MutableMapping, Optional

from cachetools import TTLCache

from ._facade import FoundryToolLike, ensure_foundry_tool
from ._user import UserProvider
from ..client._client import FoundryToolClient
from ..client._models import FoundryTool, FoundryToolDetails, FoundryToolSource, ResolvedFoundryTool, UserInfo


class FoundryToolCatalog(ABC):
    """Base class for Foundry tool catalogs."""
    def __init__(self, user_provider: UserProvider):
        self._user_provider = user_provider

    async def get(self, tool: FoundryToolLike) -> Optional[ResolvedFoundryTool]:
        """Gets a Foundry tool by its definition.

        :param tool: The Foundry tool to resolve.
        :type tool: FoundryToolLike
        :return: The resolved Foundry tool.
        :rtype: Optional[ResolvedFoundryTool]
        """
        tools = await self.list([tool])
        return tools[0] if tools else None

    @abstractmethod
    async def list(self, tools: List[FoundryToolLike]) -> List[ResolvedFoundryTool]:
        """Lists all available Foundry tools.

        :param tools: The list of Foundry tools to resolve.
        :type tools: List[FoundryToolLike]
        :return: A list of resolved Foundry tools.
        :rtype: List[ResolvedFoundryTool]
        """
        raise NotImplementedError


class CachedFoundryToolCatalog(FoundryToolCatalog, ABC):
    """Cached implementation of FoundryToolCatalog with concurrency-safe caching."""

    def __init__(self, user_provider: UserProvider):
        super().__init__(user_provider)
        self._cache: MutableMapping[FoundryTool, Awaitable[Optional[FoundryToolDetails]]] = self._create_cache()

    def _create_cache(self) -> MutableMapping[FoundryTool, Awaitable[Optional[FoundryToolDetails]]]:
        return TTLCache(maxsize=1024, ttl=600)

    def _get_key(self, user: Optional[UserInfo], tool: FoundryTool) -> Any:
        if tool.source is FoundryToolSource.HOSTED_MCP:
            return tool
        return user, tool

    async def list(self, tools: List[FoundryToolLike]) -> List[ResolvedFoundryTool]:
        """Lists all available Foundry tools with concurrency-safe caching.

        :param tools: The list of Foundry tools to resolve.
        :type tools: List[FoundryToolLike]
        :return: A list of resolved Foundry tools.
        :rtype: List[ResolvedFoundryTool]
        """
        user = await self._user_provider.get_user()
        tools: List[FoundryTool] = [ensure_foundry_tool(tool) for tool in tools]  # type: ignore

        # for tools that are not being listed, create a batch task, convert to per-tool resolving tasks, and cache them
        tools_to_fetch = [tool for tool in tools if self._get_key(user, tool) not in self._cache]
        if tools_to_fetch:
            # Awaitable[Mapping[FoundryTool, FoundryToolDetails]]
            fetched_tools = asyncio.create_task(self._fetch_tools(tools_to_fetch, user))

            for tool in tools_to_fetch:
                # safe to write cache since it's the only runner in this event loop
                self._cache[self._get_key(user, tool)] = asyncio.create_task(self._as_resolving_task(tool, fetched_tools))

        # now we have every tool associated with a task
        resolving_tasks: Dict[FoundryTool, Awaitable[Optional[FoundryToolDetails]]] = {
            tool: self._cache[self._get_key(user, tool)]
            for tool in tools
        }

        await asyncio.gather(*resolving_tasks.values())

        resolved_tools = []
        for tool, task in resolving_tasks.items():
            # this acts like a lock - every task of the same tool waits for the same underlying fetch
            details = await task
            if details is not None:
                # filter out unresolved tools in _as_resolving_task()
                resolved_tools.append(
                    ResolvedFoundryTool(
                        definition=tool,
                        details=details
                    )
                )

        return resolved_tools

    @staticmethod
    async def _as_resolving_task(
            tool: FoundryTool,
            fetching: Awaitable[Mapping[FoundryTool, FoundryToolDetails]]) -> Optional[FoundryToolDetails]:
        details = await fetching
        return details.get(tool, None)

    @abstractmethod
    async def _fetch_tools(self,
                           tools: List[FoundryTool],
                           user: Optional[UserInfo]) -> Mapping[FoundryTool, FoundryToolDetails]:
        raise NotImplementedError


class DefaultFoundryToolCatalog(CachedFoundryToolCatalog):
    """Default implementation of FoundryToolCatalog."""

    def __init__(self, client: FoundryToolClient, user_provider: UserProvider, agent_name: str):
        super().__init__(user_provider)
        self._client = client
        self._agent_name = agent_name

    async def _fetch_tools(self,
                           tools: List[FoundryTool],
                           user: Optional[UserInfo]) -> Mapping[FoundryTool, FoundryToolDetails]:
        return await self._client.list_tools(tools, self._agent_name, user)
