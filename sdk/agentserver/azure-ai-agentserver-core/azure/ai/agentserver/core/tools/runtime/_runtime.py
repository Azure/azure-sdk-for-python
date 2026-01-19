# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from typing import Any, AsyncContextManager, Dict, Optional, Union

from azure.core.credentials_async import AsyncTokenCredential

from ._catalog import DefaultFoundryToolCatalog, FoundryToolCatalog
from ._facade import FoundryToolLike
from ._resolver import DefaultFoundryToolInvocationResolver, FoundryToolInvocationResolver
from ._user import ContextVarUserProvider, UserProvider
from ..client._models import ResolvedFoundryTool
from ..client._client import FoundryToolClient
from ...constants import Constants


class FoundryToolRuntime(AsyncContextManager["FoundryToolRuntime"]):
    """Base class for Foundry tool runtimes."""

    @property
    def catalog(self) -> FoundryToolCatalog:
        """The tool catalog.

        :return: The tool catalog.
        :rtype: FoundryToolCatalog
        """
        raise NotImplementedError

    @property
    def invocation(self) -> FoundryToolInvocationResolver:
        """The tool invocation resolver.

        :return: The tool invocation resolver.
        :rtype: FoundryToolInvocationResolver
        """
        raise NotImplementedError

    async def invoke(self, tool: Union[FoundryToolLike, ResolvedFoundryTool], arguments: Dict[str, Any]) -> Any:
        """Invoke a tool with the given arguments.

        :param tool: The tool to invoke.
        :type tool: Union[FoundryToolLike, ResolvedFoundryTool]
        :param arguments: The arguments to pass to the tool.
        :type arguments: Dict[str, Any]
        :return: The result of the tool invocation.
        :rtype: Any
        """
        invoker = await self.invocation.resolve(tool)
        return await invoker.invoke(arguments)


class DefaultFoundryToolRuntime(FoundryToolRuntime):
    """Default implementation of FoundryToolRuntime."""

    def __init__(self,
                 project_endpoint: str,
                 credential: "AsyncTokenCredential",
                 user_provider: Optional[UserProvider] = None):
        # Do we need introduce DI here?
        self._user_provider = user_provider or ContextVarUserProvider()
        self._agent_name = os.getenv(Constants.AGENT_NAME, "$default")
        self._client = FoundryToolClient(endpoint=project_endpoint, credential=credential)
        self._catalog = DefaultFoundryToolCatalog(client=self._client,
                                                  user_provider=self._user_provider,
                                                  agent_name=self._agent_name)
        self._invocation = DefaultFoundryToolInvocationResolver(catalog=self._catalog,
                                                                client=self._client,
                                                                user_provider=self._user_provider,
                                                                agent_name=self._agent_name)

    @property
    def catalog(self) -> FoundryToolCatalog:
        """The tool catalog."""
        return self._catalog

    @property
    def invocation(self) -> FoundryToolInvocationResolver:
        """The tool invocation resolver."""
        return self._invocation

    async def __aenter__(self) -> "DefaultFoundryToolRuntime":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._client.__aexit__(exc_type, exc_value, traceback)
