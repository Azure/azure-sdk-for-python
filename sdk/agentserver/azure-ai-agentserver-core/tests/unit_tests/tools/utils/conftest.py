# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for utils unit tests.

Common fixtures are inherited from the parent conftest.py automatically by pytest.
"""
from typing import Optional

from azure.ai.agentserver.core.tools.client._models import (
    FoundryConnectedTool,
    FoundryHostedMcpTool,
    FoundryToolDetails,
    ResolvedFoundryTool,
    SchemaDefinition,
    SchemaType,
)


def create_resolved_tool_with_name(
    name: str,
    tool_type: str = "mcp",
    connection_id: Optional[str] = None
) -> ResolvedFoundryTool:
    """Helper to create a ResolvedFoundryTool with a specific name.

    :param name: The name for the tool details.
    :param tool_type: Either "mcp" or "connected".
    :param connection_id: Connection ID for connected tools. If provided with tool_type="mcp",
                          will automatically use "connected" type to ensure unique tool IDs.
    :return: A ResolvedFoundryTool instance.
    """
    schema = SchemaDefinition(
        type=SchemaType.OBJECT,
        properties={},
        required=set()
    )
    details = FoundryToolDetails(
        name=name,
        description=f"Tool named {name}",
        input_schema=schema
    )

    # If connection_id is provided, use connected tool to ensure unique IDs
    if connection_id is not None or tool_type == "connected":
        definition = FoundryConnectedTool(
            protocol="mcp",
            project_connection_id=connection_id or f"conn-{name}"
        )
    else:
        definition = FoundryHostedMcpTool(
            name=f"mcp-{name}",
            configuration={}
        )

    return ResolvedFoundryTool(definition=definition, details=details)
