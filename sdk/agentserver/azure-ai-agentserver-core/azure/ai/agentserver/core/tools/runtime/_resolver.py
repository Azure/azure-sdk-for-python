# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod

from ._invoker import FoundryToolInvoker
from ..client._models import FoundryTool


class FoundryToolInvocationResolver(ABC):
    """Resolver for Foundry tool invocations."""

    @abstractmethod
    async def resolve(self, tool: FoundryTool) -> FoundryToolInvoker:
        """Resolves a Foundry tool invocation.

        :param tool: The Foundry tool to resolve.
        :type tool: FoundryTool
        :return: The resolved Foundry tool invoker.
        :rtype: FoundryToolInvoker
        """
        raise NotImplementedError