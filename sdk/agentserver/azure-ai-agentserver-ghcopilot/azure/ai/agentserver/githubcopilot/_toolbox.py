# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
"""Foundry toolbox MCP bridge and discovery.

Centralises all toolbox-related logic:

- Discovering MCP server configs from ``mcp.json``
- Connecting to toolbox MCP endpoints via HTTP (JSON-RPC)
- Discovering available tools via ``tools/list``
- Creating Copilot SDK ``Tool`` wrappers that proxy calls to the MCP endpoint
- Handling auth token refresh

Instead of passing ``mcp_servers`` to the Copilot SDK (which has issues
with dotted tool names), we own the entire MCP interaction and register
tools as regular Copilot SDK custom tools.
"""
import asyncio
import json
import logging
import pathlib
import re
from typing import Any, Dict, List, Optional

import httpx
from copilot.tools import Tool, ToolResult

logger = logging.getLogger("azure.ai.agentserver.githubcopilot")

# Canary — proves which version of _toolbox.py is deployed.
_TOOLBOX_BUILD_TAG = "toolbox-v4-persistent-client"
logger.info("Toolbox module loaded: %s", _TOOLBOX_BUILD_TAG)

_FOUNDRY_TOOLBOX_FEATURE_HEADER = "Toolboxes=V1Preview"
_FOUNDRY_TOOLBOX_SERVER_KEY = "foundry-toolbox"
_FOUNDRY_SCOPE = "https://ai.azure.com/.default"



# ---------------------------------------------------------------------------
# Discovery — read mcp.json and build server config dicts
# ---------------------------------------------------------------------------

def discover_mcp_servers(
    project_root: pathlib.Path,
    toolbox_endpoint: Optional[str] = None,
) -> Dict[str, Any]:
    """Discover MCP server configs from ``mcp.json`` and an optional toolbox endpoint.

    Sources (merged in order, later wins on key collision):

    1. ``mcp.json`` in the project root — static config checked into the repo.
    2. *toolbox_endpoint* — an explicit URL for the Foundry toolbox MCP
       server.  When provided and ``mcp.json`` does not already define a
       ``"foundry-toolbox"`` entry, one is added automatically with the
       required ``Foundry-Features`` header and ``_auto_auth`` marker.

    For servers without an explicit ``Authorization`` header, the adapter
    will inject a fresh token automatically before each session.  The
    ``_auto_auth`` flag on the ``headers`` dict opts the server in to this
    behaviour.

    :param project_root: Agent project root directory (contains ``mcp.json``).
    :param toolbox_endpoint: Optional Foundry toolbox MCP endpoint URL.
    :returns: A dict of ``{server_name: server_config}``.
    """
    servers: Dict[str, Any] = {}

    # 1. Load from mcp.json
    mcp_path = project_root / "mcp.json"
    if mcp_path.exists():
        try:
            with open(mcp_path) as f:
                servers.update(json.load(f))
            logger.info("Loaded MCP servers from mcp.json: %s", list(servers.keys()))
        except Exception:
            logger.warning("Failed to load mcp.json", exc_info=True)

    # 2. Explicit toolbox endpoint
    if toolbox_endpoint and _FOUNDRY_TOOLBOX_SERVER_KEY not in servers:
        servers[_FOUNDRY_TOOLBOX_SERVER_KEY] = {
            "type": "http",
            "url": toolbox_endpoint,
            "tools": ["*"],
            "headers": {
                "Foundry-Features": _FOUNDRY_TOOLBOX_FEATURE_HEADER,
                "_auto_auth": True,
            },
        }
        logger.info("Added toolbox MCP server: %s", toolbox_endpoint)

    # Auto-inject headers for toolbox endpoints
    for server in servers.values():
        if not isinstance(server, dict):
            continue
        headers = server.setdefault("headers", {})
        if "Authorization" not in headers:
            headers["_auto_auth"] = True
        url = server.get("url", "").strip()
        server["url"] = url
        if "/toolboxes/" in url and "Foundry-Features" not in headers:
            headers["Foundry-Features"] = _FOUNDRY_TOOLBOX_FEATURE_HEADER

    return servers


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def refresh_mcp_auth(servers: Dict[str, Any], credential: Any) -> None:
    """Refresh ``Authorization`` headers on MCP servers that opted in to auto-auth.

    :param servers: The ``mcp_servers`` dict from session config (mutated in place).
    :param credential: An Azure credential with a ``get_token()`` method.
    """
    token = credential.get_token(_FOUNDRY_SCOPE).token
    for server in servers.values():
        if not isinstance(server, dict):
            continue
        headers = server.get("headers", {})
        if headers.get("_auto_auth"):
            headers["Authorization"] = f"Bearer {token}"


# ---------------------------------------------------------------------------
# Tool name sanitisation
# ---------------------------------------------------------------------------

def _sanitize_tool_name(name: str) -> str:
    """Make a tool name safe for the Copilot SDK / LLM function-call API.

    Replaces dots, hyphens, and other non-alphanumeric/underscore characters
    with underscores, then strips the common ``FoundryMCPServerpreview.``
    prefix to keep names short and readable.
    """
    # Strip the verbose server prefix
    name = re.sub(r"^FoundryMCPServerpreview\.", "", name)
    # Also strip any other "ServerName." prefix pattern
    name = re.sub(r"^[A-Za-z0-9]+\.", "", name)
    # Replace invalid chars with underscores
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)


# ---------------------------------------------------------------------------
# MCP Bridge — HTTP JSON-RPC client for Foundry toolbox endpoints
# ---------------------------------------------------------------------------

class McpBridge:
    """HTTP-based MCP client that connects to a Foundry toolbox MCP endpoint.

    Handles the MCP lifecycle: ``initialize`` → ``notifications/initialized``
    → ``tools/list`` → ``tools/call``.

    When *credential* is provided, the ``Authorization`` header is refreshed
    automatically before each ``call_tool`` request.
    """

    def __init__(self, endpoint: str, headers: Dict[str, str], credential: Any = None):
        self._endpoint = endpoint
        self._headers = dict(headers)
        self._session_id: Optional[str] = None
        self._req_id = 0
        self._credential = credential
        # Single persistent client for connection affinity through load balancers.
        self._client = httpx.AsyncClient(timeout=60.0)

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def _request_headers(self) -> Dict[str, str]:
        headers = dict(self._headers)
        if self._credential:
            try:
                token = self._credential.get_token(_FOUNDRY_SCOPE).token
                headers["Authorization"] = f"Bearer {token}"
            except Exception:
                logger.warning("Failed to refresh token for MCP bridge", exc_info=True)
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        return headers

    async def initialize(self) -> str:
        """Send MCP ``initialize`` + ``notifications/initialized``.

        :returns: The server name from the MCP ``initialize`` response.
        """
        auth_method = "credential" if self._credential else "static-header"
        has_auth = "Authorization" in self._headers
        logger.info(
            "MCP initialize: endpoint=%r (len=%d) auth_method=%s has_auth=%s",
            self._endpoint, len(self._endpoint), auth_method, has_auth,
        )

        resp = await self._client.post(
            self._endpoint,
            headers=self._headers,
            json={
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "agentserver-toolbox-bridge",
                        "version": "1.0.0",
                    },
                },
            },
        )
        diag_keys = ("x-ms-request-id", "x-ms-client-request-id", "x-request-id", "apim-request-id")
        diag = {k: resp.headers[k] for k in diag_keys if k in resp.headers}
        logger.info(
            "MCP initialize response: status=%d diagnostics=%s",
            resp.status_code, diag,
        )
        resp.raise_for_status()
        data = resp.json()
        self._session_id = resp.headers.get("mcp-session-id")

        # Send initialized notification
        await self._client.post(
            self._endpoint,
            headers=self._request_headers(),
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        )

        return data.get("result", {}).get("serverInfo", {}).get("name", "unknown")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Call ``tools/list`` and return the tools array."""
        req_headers = self._request_headers()
        auth_method = "credential" if self._credential else "static-header"
        has_auth = "Authorization" in req_headers

        resp = await self._client.post(
            self._endpoint,
            headers=req_headers,
            json={
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/list",
                "params": {},
            },
        )
        # Capture diagnostic headers before raising
        diag_keys = ("x-ms-request-id", "x-ms-client-request-id", "x-request-id", "apim-request-id")
        diag = {k: resp.headers[k] for k in diag_keys if k in resp.headers}
        logger.info(
            "MCP tools/list response: status=%d auth_method=%s has_auth=%s "
            "session_id=%s diagnostics=%s",
            resp.status_code, auth_method, has_auth,
            self._session_id, diag,
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            logger.warning("MCP tools/list error: %s diagnostics=%s", data["error"], diag)
        tools = data.get("result", {}).get("tools", [])
        if not tools:
            logger.warning(
                "MCP tools/list returned 0 tools. url=%s "
                "Response keys: %s, result keys: %s, "
                "full_response=%s, all_response_headers=%s, "
                "diagnostics=%s",
                self._endpoint,
                list(data.keys()),
                list(data.get("result", {}).keys()),
                json.dumps(data),
                dict(resp.headers),
                diag,
            )
        return tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Call ``tools/call`` and return the text result.

        :param name: The original MCP tool name (not sanitised).
        :param arguments: Tool arguments dict.
        :returns: Formatted text result.
        """
        logger.info("MCP tools/call: %s args=%s", name, list(arguments.keys()))
        resp = await self._client.post(
            self._endpoint,
            headers=self._request_headers(),
            json={
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            },
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            err = data["error"]
            logger.warning("MCP tools/call error for %s: %s", name, err)
            return f"Error: {err.get('message', err)}"
        result = data.get("result", {})
        return _format_tool_result(result)

    async def close(self) -> None:
        """Close the persistent HTTP client."""
        await self._client.aclose()


# ---------------------------------------------------------------------------
# Result formatting
# ---------------------------------------------------------------------------

def _format_tool_result(result: Dict[str, Any]) -> str:
    """Extract text from an MCP ``tools/call`` result."""
    content = result.get("content", [])
    texts = [
        c.get("text", "")
        for c in content
        if isinstance(c, dict) and c.get("type") == "text"
    ]
    base_text = "\n".join(t for t in texts if t).strip()

    # Append citation metadata when present (Azure AI Search pattern)
    citations = _extract_citations(result)
    if not citations:
        return base_text or json.dumps(result)

    lines = ["", "Sources:"]
    for idx, c in enumerate(citations, start=1):
        title = c.get("title", "source")
        url = c.get("url", "")
        score = c.get("score")
        if score is not None:
            lines.append(f"{idx}. {title} (score: {score})")
        else:
            lines.append(f"{idx}. {title}")
        if url:
            lines.append(f"   {url}")

    citation_block = "\n".join(lines)
    if base_text:
        return f"{base_text}\n{citation_block}"
    return citation_block.lstrip()


def _extract_citations(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract citation metadata from ``structuredContent.documents[]``."""
    structured = result.get("structuredContent")
    if not isinstance(structured, dict):
        return []
    docs = structured.get("documents")
    if not isinstance(docs, list):
        return []

    citations: List[Dict[str, Any]] = []
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        citations.append({
            "title": doc.get("title") or doc.get("id") or "source",
            "url": doc.get("url"),
            "score": doc.get("score"),
        })
    return citations


# ---------------------------------------------------------------------------
# Copilot SDK Tool wrappers
# ---------------------------------------------------------------------------

def _make_copilot_tools(bridge: McpBridge, mcp_tools: List[Dict[str, Any]]) -> List[Tool]:
    """Convert MCP tool definitions into Copilot SDK ``Tool`` objects.

    Tool names are sanitised (stripped of server prefixes, dots/hyphens →
    underscores) because the Copilot API rejects names with those characters.
    The original MCP name is preserved for the ``tools/call`` RPC.
    """
    tools = []
    seen_names: Dict[str, int] = {}

    for mcp_tool in mcp_tools:
        mcp_name = mcp_tool["name"]
        sdk_name = _sanitize_tool_name(mcp_name)

        # Deduplicate names (e.g. two servers with same tool base name)
        if sdk_name in seen_names:
            seen_names[sdk_name] += 1
            sdk_name = f"{sdk_name}_{seen_names[sdk_name]}"
        else:
            seen_names[sdk_name] = 0

        desc = mcp_tool.get("description", f"MCP tool: {mcp_name}")
        schema = mcp_tool.get("inputSchema", {"type": "object", "properties": {}})

        def _make_handler(original_name: str):
            async def async_handler(invocation):
                args = getattr(invocation, "arguments", None) or {}
                if not isinstance(args, dict):
                    args = {}
                try:
                    result_text = await bridge.call_tool(original_name, args)
                    return ToolResult(text_result_for_llm=result_text)
                except Exception as e:
                    logger.warning("Tool %s failed: %s", original_name, e)
                    return ToolResult(
                        text_result_for_llm=f"Error calling {original_name}: {e}",
                        result_type="failure",
                        error=str(e),
                    )

            return async_handler

        tools.append(Tool(
            name=sdk_name,
            description=desc,
            parameters=schema,
            handler=_make_handler(mcp_name),
        ))

    return tools


# ---------------------------------------------------------------------------
# High-level: connect to toolbox and return SDK tools
# ---------------------------------------------------------------------------

async def connect_toolbox(
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    credential: Any = None,
    name: Optional[str] = None,
) -> tuple["McpBridge", List[Tool]]:
    """Connect to a Foundry toolbox MCP endpoint and return SDK-ready tools.

    1. Builds auth headers from *headers* or *credential*
    2. Initialises the MCP session
    3. Discovers tools via ``tools/list``
    4. Creates Copilot SDK ``Tool`` wrappers

    :param endpoint: Toolbox MCP endpoint URL.
    :param headers: Pre-built headers dict (including Authorization).
    :param credential: Azure credential with ``get_token()`` method (used
        when *headers* is not provided or has no Authorization).
    :param name: Display name for logging.
    :returns: ``(bridge, tools)`` — caller must ``await bridge.close()`` on shutdown.
    """
    h = dict(headers or {})
    h.setdefault("Content-Type", "application/json")
    endpoint = endpoint.strip()

    # Auto-inject auth from credential if not already set
    if "Authorization" not in h and credential is not None:
        token = credential.get_token(_FOUNDRY_SCOPE).token
        h["Authorization"] = f"Bearer {token}"

    # Auto-inject toolbox feature header
    if "/toolboxes/" in endpoint:
        h.setdefault("Foundry-Features", _FOUNDRY_TOOLBOX_FEATURE_HEADER)

    bridge = McpBridge(endpoint, h, credential=credential)
    server_name = await bridge.initialize()
    mcp_tools = await bridge.list_tools()
    sdk_tools = _make_copilot_tools(bridge, mcp_tools)

    display = name or server_name
    logger.info(
        "Toolbox '%s' connected: %d tools discovered (%s)",
        display,
        len(sdk_tools),
        ", ".join(t.name for t in sdk_tools[:10])
        + ("..." if len(sdk_tools) > 10 else ""),
    )

    return bridge, sdk_tools
