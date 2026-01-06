# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import List

from ..client._models import FoundryTool, ResolvedFoundryTool


class FoundryToolCatalog(ABC):
    """Base class for Foundry tool catalogs."""

    @abstractmethod
    async def get(self, tool: FoundryTool) -> ResolvedFoundryTool:
        """Gets a Foundry tool by its definition.

        :param tool: The Foundry tool to resolve.
        :type tool: FoundryTool
        :return: The resolved Foundry tool.
        :rtype: ResolvedFoundryTool
        """
        raise NotImplementedError

    @abstractmethod
    async def list(self, tools: List[FoundryTool]) -> List[ResolvedFoundryTool]:
        """Lists all available Foundry tools.

        :param tools: The list of Foundry tools to resolve.
        :type tools: List[FoundryTool]
        :return: A list of resolved Foundry tools.
        :rtype: List[ResolvedFoundryTool]
        """
        raise NotImplementedError
