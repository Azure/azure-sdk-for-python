# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import Any, Dict

from ..client._models import ResolvedFoundryTool


class FoundryToolInvoker(ABC):

    @property
    @abstractmethod
    def definition(self) -> ResolvedFoundryTool:
        """The definition of the tool.

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
