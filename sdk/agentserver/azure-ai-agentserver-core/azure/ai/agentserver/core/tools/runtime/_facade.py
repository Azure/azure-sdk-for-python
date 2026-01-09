# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Union

from .. import FoundryConnectedTool, FoundryHostedMcpTool
from .._exceptions import InvalidToolFacadeError
from ..client._models import FoundryTool, FoundryToolProtocol

# FoundryToolFacade: a “tool descriptor” bag.
#
# Reserved keys:
#   Required:
#     - "type": str            Discriminator, e.g. "mcp" | "a2a" | "code_interpreter" | ...
#   Optional:
#     - "project_connection_id": str     Project connection id of Foundry connected tools, required with "type" is "mcp" or a2a.
#
# Custom keys:
#   - Allowed, but MUST NOT shadow reserved keys.
FoundryToolFacade = Dict[str, Any]

FoundryToolLike = Union[FoundryToolFacade, FoundryTool]


def ensure_foundry_tool(tool: FoundryToolLike) -> FoundryTool:
    """Ensure the input is a FoundryTool instance.

    :param tool: The tool descriptor, either as a FoundryToolFacade or FoundryTool.
    :type tool: FoundryToolLike
    :return: The corresponding FoundryTool instance.
    :rtype: FoundryTool
    """
    if isinstance(tool, FoundryTool):
        return tool

    tool = tool.copy()
    tool_type = tool.pop("type", None)
    if not isinstance(tool_type, str) or not tool_type:
        raise InvalidToolFacadeError("FoundryToolFacade must have a valid 'type' field of type str.")

    try:
        protocol = FoundryToolProtocol(tool_type)
        project_connection_id = tool.pop("project_connection_id", None)
        if not isinstance(project_connection_id, str) or not project_connection_id:
            raise InvalidToolFacadeError(f"project_connection_id is required for tool protocol {protocol}.")

        return FoundryConnectedTool(protocol=protocol, project_connection_id=project_connection_id)
    except:
        return FoundryHostedMcpTool(name=tool_type, configuration=tool)
