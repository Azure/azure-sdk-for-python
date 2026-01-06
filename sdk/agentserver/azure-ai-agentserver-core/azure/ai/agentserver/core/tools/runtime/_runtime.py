# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from ._catalog import FoundryToolCatalog
from ._resolver import FoundryToolInvocationResolver


class FoundryToolRuntime:
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
