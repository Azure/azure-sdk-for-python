# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from ..client._models import ResolvedFoundryTool


class ToolNameResolver:
    """Utility class for resolving tool names to be registered to model."""

    def __init__(self):
        self._count_by_name = {}
        self._stable_names = {}

    def resolve(self, tool: ResolvedFoundryTool) -> str:
        """Resolve a stable name for the given tool.
        If the tool name has not been used before, use it as is.
        If it has been used, append an underscore and a count to make it unique.

        :param tool: The tool to resolve the name for.
        :type tool: ResolvedFoundryTool
        :return: The resolved stable name for the tool.
        :rtype: str
        """
        final_name = self._stable_names.get(tool.id)
        if final_name is not None:
            return final_name

        dup_count = self._count_by_name.setdefault(tool.details.name, 0)

        if dup_count == 0:
            final_name = tool.details.name
        else:
            final_name = f"{tool.details.name}_{dup_count}"

        self._stable_names[tool.id] = final_name
        self._count_by_name[tool.details.name] = dup_count + 1
        return self._stable_names[tool.id]
