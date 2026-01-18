# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio
import threading
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import Future
from typing import Any, Awaitable, Collection, Dict, List, Mapping, MutableMapping, Optional, Tuple, Union

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


_CachedValueType = Union[Awaitable[List[FoundryToolDetails]], List[FoundryToolDetails]]


class CachedFoundryToolCatalog(FoundryToolCatalog, ABC):
    """Cached implementation of FoundryToolCatalog with concurrency-safe caching."""

    def __init__(self, user_provider: UserProvider):
        super().__init__(user_provider)
        self._cache: MutableMapping[Any, _CachedValueType] = self._create_cache()

    def _create_cache(self) -> MutableMapping[Any, _CachedValueType]:
        return TTLCache(maxsize=1024, ttl=600)

    def _get_key(self, user: Optional[UserInfo], tool: FoundryTool) -> Any:
        if tool.source is FoundryToolSource.HOSTED_MCP:
            return tool.id
        return user, tool.id

    async def list(self, tools: List[FoundryToolLike]) -> List[ResolvedFoundryTool]:
        user = await self._user_provider.get_user()
        foundry_tools = {}
        tools_to_fetch = {}
        for t in tools:
            tool = ensure_foundry_tool(t)
            key = self._get_key(user, tool)
            foundry_tools[key] = tool
            if key not in self._cache:
                tools_to_fetch[key] = tool

        # for tools that are not being listed, create a batch task, convert to per-tool resolving tasks, and cache them
        if tools_to_fetch:
            # Awaitable[Mapping[str, List[FoundryToolDetails]]]
            fetched_tools = asyncio.create_task(self._fetch_tools(tools_to_fetch.values(), user))

            for k in tools_to_fetch.keys():
                # safe to write cache since it's the only runner in this event loop
                self._cache[k] = asyncio.create_task(self._as_resolving_task(k, fetched_tools))

        try:
            # now we have every tool associated with a task
            tasks = [
                task_or_value
                for key, tool in foundry_tools.items()
                if (task_or_value := self._cache[key]) and isinstance(task_or_value, Awaitable)
            ]
            await asyncio.gather(*tasks)
        except:
            # exception can only be caused by fetching tasks, remove them from cache
            for k in tools_to_fetch.keys():
                if k in self._cache:
                    del self._cache[k]
            raise

        resolved_tools = []
        for key, tool in foundry_tools.items():
            # this acts like a lock - every task of the same tool waits for the same underlying fetch
            task_or_value = self._cache[key]
            if isinstance(task_or_value, Awaitable):
                details_list = await task_or_value
            else:
                details_list = task_or_value

            for details in details_list:
                resolved_tools.append(
                    ResolvedFoundryTool(
                        definition=tool,
                        details=details
                    )
                )

        return resolved_tools

    async def _as_resolving_task(
            self,
            tool_id: str,
            fetching: Awaitable[Mapping[str, List[FoundryToolDetails]]]
    ) -> List[FoundryToolDetails]:
        details = await fetching
        details_list = details.get(tool_id, [])
        # replace the task in cache with the actual value to optimize memory usage
        self._cache[tool_id] = details_list
        return details_list

    @abstractmethod
    async def _fetch_tools(self,
                           tools: Collection[FoundryTool],
                           user: Optional[UserInfo]) -> Mapping[str, List[FoundryToolDetails]]:
        raise NotImplementedError


class DefaultFoundryToolCatalog(CachedFoundryToolCatalog):
    """Default implementation of FoundryToolCatalog."""

    def __init__(self, client: FoundryToolClient, user_provider: UserProvider, agent_name: str):
        super().__init__(user_provider)
        self._client = client
        self._agent_name = agent_name

    async def _fetch_tools(self,
                           tools: Collection[FoundryTool],
                           user: Optional[UserInfo]) -> Mapping[str, List[FoundryToolDetails]]:
        return await self._client.list_tools_details(tools, self._agent_name, user)
