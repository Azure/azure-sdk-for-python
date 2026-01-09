# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod

from ._catalog import FoundryToolCatalog
from ._facade import FoundryToolLike, ensure_foundry_tool
from ._invoker import DefaultFoundryToolInvoker, FoundryToolInvoker
from ._user import UserProvider
from .. import FoundryToolClient
from .._exceptions import UnableToResolveToolInvocationError
from ..client._models import FoundryTool


class FoundryToolInvocationResolver(ABC):
    """Resolver for Foundry tool invocations."""

    @abstractmethod
    async def resolve(self, tool: FoundryToolLike) -> FoundryToolInvoker:
        """Resolves a Foundry tool invocation.

        :param tool: The Foundry tool to resolve.
        :type tool: FoundryToolLike
        :return: The resolved Foundry tool invoker.
        :rtype: FoundryToolInvoker
        """
        raise NotImplementedError


class DefaultFoundryToolInvocationResolver(FoundryToolInvocationResolver):
    """Default implementation of FoundryToolInvocationResolver."""

    def __init__(self,
                 catalog: FoundryToolCatalog,
                 client: FoundryToolClient,
                 user_provider: UserProvider,
                 agent_name: str):
        self._catalog = catalog
        self._client = client
        self._user_provider = user_provider
        self._agent_name = agent_name

    async def resolve(self, tool: FoundryToolLike) -> FoundryToolInvoker:
        """Resolves a Foundry tool invocation.

        :param tool: The Foundry tool to resolve.
        :type tool: FoundryToolLike
        :return: The resolved Foundry tool invoker.
        :rtype: FoundryToolInvoker
        """
        tool = ensure_foundry_tool(tool)
        resolved_tool = await self._catalog.get(tool)
        if not resolved_tool:
            raise UnableToResolveToolInvocationError(f"Unable to resolve tool {tool} from catalog", tool)
        return DefaultFoundryToolInvoker(resolved_tool, self._client, self._user_provider, self._agent_name)
