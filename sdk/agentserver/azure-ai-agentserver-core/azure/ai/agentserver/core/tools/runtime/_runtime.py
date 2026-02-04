# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, AsyncContextManager, ClassVar, Dict, Optional, Union

from azure.core.credentials_async import AsyncTokenCredential

from ._catalog import DefaultFoundryToolCatalog, FoundryToolCatalog
from ._facade import FoundryToolLike
from ._resolver import DefaultFoundryToolInvocationResolver, FoundryToolInvocationResolver
from ._user import ContextVarUserProvider, UserProvider
from ..client._models import ResolvedFoundryTool
from ..client._client import FoundryToolClient
from ...constants import Constants


def create_tool_runtime(project_endpoint: str | None,
                        credential: AsyncTokenCredential | None) -> "FoundryToolRuntime":
    """Create a Foundry tool runtime.
    Returns a DefaultFoundryToolRuntime if both project_endpoint and credential are provided,
    otherwise returns a ThrowingFoundryToolRuntime which raises errors on usage.

    :param project_endpoint: The project endpoint.
    :type project_endpoint: str | None
    :param credential: The credential.
    :type credential: AsyncTokenCredential | None
    :return: The Foundry tool runtime.
    :rtype: FoundryToolRuntime
    """
    if project_endpoint and credential:
        return DefaultFoundryToolRuntime(project_endpoint=project_endpoint, credential=credential)
    return ThrowingFoundryToolRuntime()

class FoundryToolRuntime(AsyncContextManager["FoundryToolRuntime"], ABC):
    """Base class for Foundry tool runtimes."""

    @property
    @abstractmethod
    def catalog(self) -> FoundryToolCatalog:
        """The tool catalog.

        :return: The tool catalog.
        :rtype: FoundryToolCatalog
        """
        raise NotImplementedError

    @property
    @abstractmethod
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
        """The tool catalog.

        :rtype: FoundryToolCatalog
        """
        return self._catalog

    @property
    def invocation(self) -> FoundryToolInvocationResolver:
        """The tool invocation resolver.

        :rtype: FoundryToolInvocationResolver
        """
        return self._invocation

    async def __aenter__(self) -> "DefaultFoundryToolRuntime":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._client.__aexit__(exc_type, exc_value, traceback)


class ThrowingFoundryToolRuntime(FoundryToolRuntime):
    """A FoundryToolRuntime that raises errors on usage."""
    _ERROR_MESSAGE: ClassVar[str] = ("FoundryToolRuntime is not configured. "
                                     "Please provide a valid project endpoint and credential.")

    @property
    def catalog(self) -> FoundryToolCatalog:
        """The tool catalog.

        :returns: The tool catalog.
        :rtype: FoundryToolCatalog
        :raises RuntimeError: Always raised to indicate the runtime is not configured.
        """
        raise RuntimeError(self._ERROR_MESSAGE)

    @property
    def invocation(self) -> FoundryToolInvocationResolver:
        """The tool invocation resolver.

        :returns: The tool invocation resolver.
        :rtype: FoundryToolInvocationResolver
        :raises RuntimeError: Always raised to indicate the runtime is not configured.
        """
        raise RuntimeError(self._ERROR_MESSAGE)

    async def __aenter__(self) -> "ThrowingFoundryToolRuntime":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass
