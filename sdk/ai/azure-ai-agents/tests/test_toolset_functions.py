# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

import azure.ai.agents.models as _models


class TestToolSetFunctions:
    def test_remove_code_interpreter_tool(self):
        """Test removing a CodeInterpreterTool from ToolSet."""
        toolset = _models.ToolSet()
        code_interpreter = _models.CodeInterpreterTool(file_ids=["file1", "file2"])
        toolset.add(code_interpreter)

        # Verify tool was added
        assert len(toolset._tools) == 1
        assert isinstance(toolset._tools[0], _models.CodeInterpreterTool)

        # Remove the tool
        toolset.remove(_models.CodeInterpreterTool)

        # Verify tool was removed
        assert len(toolset._tools) == 0

    def test_remove_file_search_tool(self):
        """Test removing a FileSearchTool from ToolSet."""
        toolset = _models.ToolSet()
        file_search = _models.FileSearchTool(vector_store_ids=["vs1", "vs2"])
        toolset.add(file_search)

        # Verify tool was added
        assert len(toolset._tools) == 1
        assert isinstance(toolset._tools[0], _models.FileSearchTool)

        # Remove the tool
        toolset.remove(_models.FileSearchTool)

        # Verify tool was removed
        assert len(toolset._tools) == 0

    def test_add_and_remove_openapi_tool_by_name(self):
        """Test removing a specific API definition from OpenApiTool by name."""
        from azure.ai.agents.models import OpenApiAuthDetails

        toolset = _models.ToolSet()
        auth = OpenApiAuthDetails(type="api_key")
        openapi_tool = _models.OpenApiTool(name="api1", description="First API", spec={"openapi": "3.0.0"}, auth=auth)

        # Add another definition to the same tool
        openapi_tool2 = _models.OpenApiTool(name="api2", description="Second API", spec={"openapi": "3.0.0"}, auth=auth)

        toolset.add(openapi_tool)
        toolset.add(openapi_tool2)

        # Verify tool was added with 2 definitions
        assert len(toolset._tools) == 1
        assert len(toolset._tools[0].definitions) == 2

        # Remove one definition by name
        toolset.remove(_models.OpenApiTool, name="api1")

        # Verify tool still exists but with only 1 definition
        assert len(toolset._tools) == 1
        assert len(toolset._tools[0].definitions) == 1
        assert toolset._tools[0].definitions[0].openapi.name == "api2"

    def test_remove_openapi_tool_entire_tool(self):
        """Test removing entire OpenApiTool without specifying name."""
        from azure.ai.agents.models import OpenApiAuthDetails

        toolset = _models.ToolSet()
        auth = OpenApiAuthDetails(type="api_key")
        openapi_tool = _models.OpenApiTool(name="api1", description="First API", spec={"openapi": "3.0.0"}, auth=auth)

        # Add another definition
        openapi_tool.add_definition(name="api2", description="Second API", spec={"openapi": "3.0.0"}, auth=auth)

        toolset.add(openapi_tool)

        # Verify tool was added with 2 definitions
        assert len(toolset._tools) == 1
        assert len(toolset._tools[0].definitions) == 2

        # Remove entire OpenApiTool without name parameter
        toolset.remove(_models.OpenApiTool)

        # Verify entire tool was removed
        assert len(toolset._tools) == 0

    def test_remove_mcp_tool_by_server_label(self):
        """Test removing a specific McpTool by server label."""
        toolset = _models.ToolSet()

        mcp_tool1 = _models.McpTool(server_label="server1", server_url="http://server1.com", allowed_tools=["tool1"])

        mcp_tool2 = _models.McpTool(server_label="server2", server_url="http://server2.com", allowed_tools=["tool2"])

        toolset.add(mcp_tool1)
        toolset.add(mcp_tool2)

        # Verify both tools were added
        assert len(toolset._tools) == 2

        # Remove one by server label
        toolset.remove(_models.McpTool, server_label="server1")

        # Verify only one tool remains
        assert len(toolset._tools) == 1
        assert toolset._tools[0].server_label == "server2"

    def test_remove_all_mcp_tools(self):
        """Test removing all McpTool instances without specifying server_label."""
        toolset = _models.ToolSet()

        mcp_tool1 = _models.McpTool(server_label="server1", server_url="http://server1.com", allowed_tools=["tool1"])

        mcp_tool2 = _models.McpTool(server_label="server2", server_url="http://server2.com", allowed_tools=["tool2"])

        toolset.add(mcp_tool1)
        toolset.add(mcp_tool2)

        # Add a non-MCP tool
        def dummy_function():
            pass

        function_tool = _models.FunctionTool({dummy_function})
        toolset.add(function_tool)

        # Verify all tools were added
        assert len(toolset._tools) == 3

        # Remove all MCP tools
        toolset.remove(_models.McpTool)

        # Verify only the function tool remains
        assert len(toolset._tools) == 1
        assert isinstance(toolset._tools[0], _models.FunctionTool)

    def test_remove_nonexistent_tool_type(self):
        """Test error when trying to remove a tool type that doesn't exist."""
        toolset = _models.ToolSet()

        with pytest.raises(ValueError, match="Tool of type FunctionTool not found in the ToolSet"):
            toolset.remove(_models.FunctionTool)

    def test_remove_openapi_tool_nonexistent_name(self):
        """Test error when trying to remove nonexistent API definition by name."""
        from azure.ai.agents.models import OpenApiAuthDetails

        toolset = _models.ToolSet()
        auth = OpenApiAuthDetails(type="api_key")
        openapi_tool = _models.OpenApiTool(name="api1", description="First API", spec={"openapi": "3.0.0"}, auth=auth)

        toolset.add(openapi_tool)

        # Try to remove a definition that doesn't exist
        with pytest.raises(ValueError, match="Definition with the name 'nonexistent' does not exist"):
            toolset.remove(_models.OpenApiTool, name="nonexistent")

    def test_remove_openapi_tool_by_name_no_openapi_tool(self):
        """Test error when trying to remove API definition by name but no OpenApiTool exists."""
        toolset = _models.ToolSet()

        with pytest.raises(ValueError, match="Tool of type OpenApiTool not found in the ToolSet"):
            toolset.remove(_models.OpenApiTool, name="api1")

    def test_remove_mcp_tool_nonexistent_server_label(self):
        """Test error when trying to remove McpTool with nonexistent server label."""
        toolset = _models.ToolSet()

        mcp_tool = _models.McpTool(server_label="server1", server_url="http://server1.com", allowed_tools=["tool1"])

        toolset.add(mcp_tool)

        # Try to remove MCP tool with nonexistent server label
        with pytest.raises(ValueError, match="McpTool with server label 'nonexistent' not found in the ToolSet"):
            toolset.remove(_models.McpTool, server_label="nonexistent")

    def test_remove_mcp_tool_no_mcp_tools(self):
        """Test error when trying to remove McpTool but none exist."""
        toolset = _models.ToolSet()

        with pytest.raises(ValueError, match="No tools of type McpTool found in the ToolSet"):
            toolset.remove(_models.McpTool)
