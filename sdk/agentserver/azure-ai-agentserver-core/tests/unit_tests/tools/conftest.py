# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for tools unit tests."""
import json
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.ai.agentserver.core.tools.client._models import (
    FoundryConnectedTool,
    FoundryHostedMcpTool,
    FoundryToolDetails,
    ResolvedFoundryTool,
    SchemaDefinition,
    SchemaProperty,
    SchemaType,
    UserInfo,
)


@pytest.fixture
def mock_credential():
    """Create a mock async token credential."""
    credential = AsyncMock()
    credential.get_token = AsyncMock(return_value=MagicMock(token="test-token"))
    return credential


@pytest.fixture
def sample_user_info():
    """Create a sample UserInfo instance."""
    return UserInfo(object_id="test-object-id", tenant_id="test-tenant-id")


@pytest.fixture
def sample_hosted_mcp_tool():
    """Create a sample FoundryHostedMcpTool."""
    return FoundryHostedMcpTool(
        name="test_mcp_tool",
        configuration={"model_deployment_name": "gpt-4"}
    )


@pytest.fixture
def sample_connected_tool():
    """Create a sample FoundryConnectedTool."""
    return FoundryConnectedTool(
        protocol="mcp",
        project_connection_id="test-connection-id"
    )


@pytest.fixture
def sample_schema_definition():
    """Create a sample SchemaDefinition."""
    return SchemaDefinition(
        type=SchemaType.OBJECT,
        properties={
            "input": SchemaProperty(type=SchemaType.STRING, description="Input parameter")
        },
        required={"input"}
    )


@pytest.fixture
def sample_tool_details(sample_schema_definition):
    """Create a sample FoundryToolDetails."""
    return FoundryToolDetails(
        name="test_tool",
        description="A test tool",
        input_schema=sample_schema_definition
    )


@pytest.fixture
def sample_resolved_mcp_tool(sample_hosted_mcp_tool, sample_tool_details):
    """Create a sample ResolvedFoundryTool for MCP."""
    return ResolvedFoundryTool(
        definition=sample_hosted_mcp_tool,
        details=sample_tool_details
    )


@pytest.fixture
def sample_resolved_connected_tool(sample_connected_tool, sample_tool_details):
    """Create a sample ResolvedFoundryTool for connected tools."""
    return ResolvedFoundryTool(
        definition=sample_connected_tool,
        details=sample_tool_details
    )


def create_mock_http_response(
    status_code: int = 200,
    json_data: Optional[Dict[str, Any]] = None
) -> AsyncMock:
    """Create a mock HTTP response that simulates real Azure SDK response behavior.

    This mock matches the behavior expected by BaseOperations._extract_response_json,
    where response.text() and response.body() are synchronous methods that return
    the actual string/bytes values directly.

    :param status_code: HTTP status code.
    :param json_data: JSON data to return.
    :return: Mock response object.
    """
    response = AsyncMock()
    response.status_code = status_code

    if json_data is not None:
        json_str = json.dumps(json_data)
        json_bytes = json_str.encode("utf-8")
        # text() and body() are synchronous methods in AsyncHttpResponse
        # They must be MagicMock (not AsyncMock) to return values directly when called
        response.text = MagicMock(return_value=json_str)
        response.body = MagicMock(return_value=json_bytes)
    else:
        response.text = MagicMock(return_value="")
        response.body = MagicMock(return_value=b"")

    # Support async context manager
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=None)

    return response
