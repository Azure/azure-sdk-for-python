# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import re
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
#     - "project_connection_id": str     Project connection id of Foundry connected tools,
#                                        required when "type" is "mcp" or "a2a".
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

        # Parse the connection identifier to extract the connection name
        connection_name = _parse_connection_id(project_connection_id)
        return FoundryConnectedTool(protocol=protocol, project_connection_id=connection_name)
    except ValueError:
        return FoundryHostedMcpTool(name=tool_type, configuration=tool)


# Pattern for Azure resource ID format:
# /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.CognitiveServices/accounts
#    /<account>/projects/<project>/connections/<name>
_RESOURCE_ID_PATTERN = re.compile(
    r"^/subscriptions/[^/]+/resourceGroups/[^/]+/providers/Microsoft\.CognitiveServices/"
    r"accounts/[^/]+/projects/[^/]+/connections/(?P<name>[^/]+)$",
    re.IGNORECASE,
)


def _parse_connection_id(connection_id: str) -> str:
    """Parse the connection identifier and extract the connection name.

    Supports two formats:
    1. Simple name: "my-connection-name"
    2. Resource ID: "/subscriptions/<sub>/resourceGroups/<rg>/providers
            /Microsoft.CognitiveServices/accounts/<account>/projects/<project>/connections/<name>"

    :param connection_id: The connection identifier, either a simple name or a full resource ID.
    :type connection_id: str
    :return: The connection name extracted from the identifier.
    :rtype: str
    :raises InvalidToolFacadeError: If the connection_id format is invalid.
    """
    if not connection_id:
        raise InvalidToolFacadeError("Connection identifier cannot be empty.")

    # Check if it's a resource ID format (starts with /)
    if connection_id.startswith("/"):
        match = _RESOURCE_ID_PATTERN.match(connection_id)
        if not match:
            raise InvalidToolFacadeError(
                f"Invalid resource ID format for connection: '{connection_id}'. "
                "Expected format: /subscriptions/<sub>/resourceGroups/<rg>/providers/"
                "Microsoft.CognitiveServices/accounts/<account>/projects/<project>/connections/<name>"
            )
        return match.group("name")

    # Otherwise, treat it as a simple connection name
    return connection_id
