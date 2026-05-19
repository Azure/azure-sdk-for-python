# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
"""Tests for _toolbox module — MCP toolbox discovery, McpBridge, and tool wrapping."""
import json
import pathlib
from unittest import mock

import pytest

# Import _toolbox directly to avoid triggering the full package __init__.py
# which depends on the Copilot SDK (may not be installed in test envs).
import sys
import importlib
_toolbox = importlib.import_module(
    "azure.ai.agentserver.githubcopilot._toolbox"
) if "azure.ai.agentserver.githubcopilot._toolbox" in sys.modules else None

if _toolbox is None:
    import importlib.util
    import pathlib

    _mod_path = (
        pathlib.Path(__file__).resolve().parents[2]
        / "azure" / "ai" / "agentserver" / "githubcopilot" / "_toolbox.py"
    )
    _spec = importlib.util.spec_from_file_location(
        "azure.ai.agentserver.githubcopilot._toolbox", _mod_path
    )
    _toolbox = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_toolbox)

_FOUNDRY_TOOLBOX_FEATURE_HEADER = _toolbox._FOUNDRY_TOOLBOX_FEATURE_HEADER
_FOUNDRY_TOOLBOX_SERVER_KEY = _toolbox._FOUNDRY_TOOLBOX_SERVER_KEY
discover_mcp_servers = _toolbox.discover_mcp_servers
refresh_mcp_auth = _toolbox.refresh_mcp_auth
_sanitize_tool_name = _toolbox._sanitize_tool_name
_format_tool_result = _toolbox._format_tool_result
_extract_citations = _toolbox._extract_citations
_make_copilot_tools = _toolbox._make_copilot_tools
McpBridge = _toolbox.McpBridge


# ---------------------------------------------------------------------------
# discover_mcp_servers
# ---------------------------------------------------------------------------


class TestDiscoverMcpServers:
    """Tests for discover_mcp_servers()."""

    def test_no_mcp_json_no_endpoint_returns_empty(self, tmp_path):
        result = discover_mcp_servers(tmp_path)
        assert result == {}

    def test_loads_from_mcp_json(self, tmp_path):
        mcp = {"my-server": {"type": "http", "url": "https://example.com/mcp"}}
        (tmp_path / "mcp.json").write_text(json.dumps(mcp))

        result = discover_mcp_servers(tmp_path)
        assert "my-server" in result
        assert result["my-server"]["url"] == "https://example.com/mcp"

    def test_mcp_json_server_without_auth_gets_auto_auth(self, tmp_path):
        mcp = {"my-server": {"type": "http", "url": "https://example.com"}}
        (tmp_path / "mcp.json").write_text(json.dumps(mcp))

        result = discover_mcp_servers(tmp_path)
        assert result["my-server"]["headers"]["_auto_auth"] is True

    def test_mcp_json_server_with_explicit_auth_no_auto_auth(self, tmp_path):
        mcp = {
            "my-server": {
                "type": "http",
                "url": "https://example.com",
                "headers": {"Authorization": "Bearer static-token"},
            }
        }
        (tmp_path / "mcp.json").write_text(json.dumps(mcp))

        result = discover_mcp_servers(tmp_path)
        assert result["my-server"]["headers"].get("_auto_auth") is None

    def test_explicit_toolbox_endpoint_creates_entry(self, tmp_path):
        result = discover_mcp_servers(tmp_path, toolbox_endpoint="https://toolbox.example.com/mcp")

        assert _FOUNDRY_TOOLBOX_SERVER_KEY in result
        server = result[_FOUNDRY_TOOLBOX_SERVER_KEY]
        assert server["url"] == "https://toolbox.example.com/mcp"
        assert server["headers"]["Foundry-Features"] == _FOUNDRY_TOOLBOX_FEATURE_HEADER
        assert server["headers"]["_auto_auth"] is True
        assert server["type"] == "http"
        assert server["tools"] == ["*"]

    def test_mcp_json_toolbox_entry_not_overridden_by_explicit_endpoint(self, tmp_path):
        """If mcp.json already defines foundry-toolbox, the explicit endpoint is ignored."""
        mcp = {
            _FOUNDRY_TOOLBOX_SERVER_KEY: {
                "type": "http",
                "url": "https://from-mcp-json.example.com",
            }
        }
        (tmp_path / "mcp.json").write_text(json.dumps(mcp))

        result = discover_mcp_servers(tmp_path, toolbox_endpoint="https://explicit.example.com")
        assert result[_FOUNDRY_TOOLBOX_SERVER_KEY]["url"] == "https://from-mcp-json.example.com"

    def test_invalid_mcp_json_is_handled_gracefully(self, tmp_path):
        (tmp_path / "mcp.json").write_text("not valid json {{{")

        result = discover_mcp_servers(tmp_path)
        assert result == {}

    def test_non_dict_mcp_json_is_handled_gracefully(self, tmp_path):
        (tmp_path / "mcp.json").write_text(json.dumps(["not", "a", "dict"]))

        # json.load succeeds but dict.update with a list raises TypeError
        result = discover_mcp_servers(tmp_path)
        assert result == {}

    def test_explicit_endpoint_combined_with_mcp_json(self, tmp_path):
        mcp = {"other-server": {"type": "http", "url": "https://other.example.com"}}
        (tmp_path / "mcp.json").write_text(json.dumps(mcp))

        result = discover_mcp_servers(tmp_path, toolbox_endpoint="https://toolbox.example.com/mcp")
        assert "other-server" in result
        assert _FOUNDRY_TOOLBOX_SERVER_KEY in result

    def test_no_env_vars_read(self, tmp_path):
        """Verify env vars are not consulted — the old behaviour is removed."""
        with mock.patch.dict("os.environ", {
            "FOUNDRY_AGENT_TOOLBOX_ENDPOINT": "https://should-be-ignored.com",
            "TOOLBOX_MCP_ENDPOINT": "https://also-ignored.com",
        }):
            result = discover_mcp_servers(tmp_path)
        assert result == {}

    def test_toolbox_url_gets_foundry_features_header(self, tmp_path):
        """Servers with /toolboxes/ in the URL get Foundry-Features auto-injected."""
        mcp = {
            "my-toolbox": {
                "type": "http",
                "url": "https://example.com/api/projects/proj/toolboxes/MyTB/mcp",
            }
        }
        (tmp_path / "mcp.json").write_text(json.dumps(mcp))

        result = discover_mcp_servers(tmp_path)
        assert result["my-toolbox"]["headers"]["Foundry-Features"] == _FOUNDRY_TOOLBOX_FEATURE_HEADER

    def test_toolbox_url_does_not_override_existing_foundry_features(self, tmp_path):
        """If the mcp.json already sets Foundry-Features, don't overwrite it."""
        mcp = {
            "my-toolbox": {
                "type": "http",
                "url": "https://example.com/toolboxes/TB/mcp",
                "headers": {"Foundry-Features": "CustomValue"},
            }
        }
        (tmp_path / "mcp.json").write_text(json.dumps(mcp))

        result = discover_mcp_servers(tmp_path)
        assert result["my-toolbox"]["headers"]["Foundry-Features"] == "CustomValue"

    def test_non_toolbox_url_no_foundry_features(self, tmp_path):
        """Servers without /toolboxes/ in the URL don't get the header."""
        mcp = {"regular": {"type": "http", "url": "https://example.com/mcp"}}
        (tmp_path / "mcp.json").write_text(json.dumps(mcp))

        result = discover_mcp_servers(tmp_path)
        assert "Foundry-Features" not in result["regular"]["headers"]


# ---------------------------------------------------------------------------
# refresh_mcp_auth
# ---------------------------------------------------------------------------


class TestRefreshMcpAuth:
    def test_refreshes_auto_auth_servers(self):
        servers = {
            "s1": {"headers": {"_auto_auth": True}},
            "s2": {"headers": {"Authorization": "Bearer old", "_auto_auth": True}},
        }
        credential = mock.Mock()
        credential.get_token.return_value = mock.Mock(token="fresh-token")

        refresh_mcp_auth(servers, credential)

        assert servers["s1"]["headers"]["Authorization"] == "Bearer fresh-token"
        assert servers["s2"]["headers"]["Authorization"] == "Bearer fresh-token"
        credential.get_token.assert_called_once_with("https://ai.azure.com/.default")

    def test_skips_servers_without_auto_auth(self):
        servers = {
            "s1": {"headers": {"Authorization": "Bearer static"}},
        }
        credential = mock.Mock()
        credential.get_token.return_value = mock.Mock(token="fresh-token")

        refresh_mcp_auth(servers, credential)

        assert servers["s1"]["headers"]["Authorization"] == "Bearer static"


# ---------------------------------------------------------------------------
# _sanitize_tool_name
# ---------------------------------------------------------------------------


class TestSanitizeToolName:
    def test_strips_foundry_prefix(self):
        assert _sanitize_tool_name("FoundryMCPServerpreview.agent_get") == "agent_get"

    def test_strips_generic_server_prefix(self):
        assert _sanitize_tool_name("WorkIQTeams.ListChats") == "ListChats"

    def test_replaces_dots_and_hyphens(self):
        # "my-tool" is not stripped because the regex requires alphanumeric prefix before dot
        assert _sanitize_tool_name("my-tool.v2") == "my_tool_v2"
        # But "MyTool.v2" matches the prefix pattern
        assert _sanitize_tool_name("MyTool.v2") == "v2"

    def test_plain_name_unchanged(self):
        assert _sanitize_tool_name("agent_get") == "agent_get"

    def test_special_chars_replaced(self):
        assert _sanitize_tool_name("tool@name#1") == "tool_name_1"


# ---------------------------------------------------------------------------
# _format_tool_result / _extract_citations
# ---------------------------------------------------------------------------


class TestFormatToolResult:
    def test_simple_text(self):
        result = {"content": [{"type": "text", "text": "hello world"}]}
        assert _format_tool_result(result) == "hello world"

    def test_multiple_text_parts(self):
        result = {
            "content": [
                {"type": "text", "text": "line1"},
                {"type": "text", "text": "line2"},
            ]
        }
        assert _format_tool_result(result) == "line1\nline2"

    def test_non_text_content_ignored(self):
        result = {
            "content": [
                {"type": "image", "data": "..."},
                {"type": "text", "text": "actual"},
            ]
        }
        assert _format_tool_result(result) == "actual"

    def test_empty_content_falls_back_to_json(self):
        result = {"content": []}
        output = _format_tool_result(result)
        assert "content" in output  # JSON dump of the result

    def test_citations_appended(self):
        result = {
            "content": [{"type": "text", "text": "answer"}],
            "structuredContent": {
                "documents": [
                    {"title": "Doc1", "url": "https://example.com/1", "score": 0.9},
                ]
            },
        }
        output = _format_tool_result(result)
        assert "answer" in output
        assert "Sources:" in output
        assert "Doc1" in output
        assert "0.9" in output
        assert "https://example.com/1" in output


class TestExtractCitations:
    def test_no_structured_content(self):
        assert _extract_citations({}) == []

    def test_valid_documents(self):
        result = {
            "structuredContent": {
                "documents": [
                    {"title": "A", "url": "http://a.com", "score": 0.8},
                    {"id": "B"},
                ]
            }
        }
        citations = _extract_citations(result)
        assert len(citations) == 2
        assert citations[0]["title"] == "A"
        assert citations[1]["title"] == "B"

    def test_non_dict_documents_skipped(self):
        result = {"structuredContent": {"documents": ["not-a-dict", {"title": "X"}]}}
        citations = _extract_citations(result)
        assert len(citations) == 1


# ---------------------------------------------------------------------------
# _make_copilot_tools
# ---------------------------------------------------------------------------


class TestMakeCopilotTools:
    def test_creates_tools_with_sanitized_names(self):
        bridge = mock.Mock(spec=McpBridge)
        mcp_tools = [
            {
                "name": "FoundryMCPServerpreview.agent_get",
                "description": "Get an agent",
                "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}}},
            },
        ]
        tools = _make_copilot_tools(bridge, mcp_tools)
        assert len(tools) == 1
        assert tools[0].name == "agent_get"

    def test_deduplicates_names(self):
        bridge = mock.Mock(spec=McpBridge)
        mcp_tools = [
            {"name": "ServerA.list", "description": "List A"},
            {"name": "ServerB.list", "description": "List B"},
        ]
        tools = _make_copilot_tools(bridge, mcp_tools)
        names = [t.name for t in tools]
        assert len(set(names)) == 2  # No duplicates
        assert "list" in names
        assert "list_1" in names

    def test_default_schema_when_missing(self):
        bridge = mock.Mock(spec=McpBridge)
        mcp_tools = [{"name": "simple_tool", "description": "A tool"}]
        tools = _make_copilot_tools(bridge, mcp_tools)
        assert tools[0].parameters == {"type": "object", "properties": {}}
