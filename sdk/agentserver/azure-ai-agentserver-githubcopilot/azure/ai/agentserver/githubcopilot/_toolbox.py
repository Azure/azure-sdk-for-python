# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
"""Foundry toolbox MCP discovery and auth helpers.

Centralises all toolbox-related logic: discovering MCP servers from
``mcp.json``, adding an explicit toolbox endpoint, injecting auth
headers, and preparing SDK-safe config dicts.
"""
import copy
import json
import logging
import pathlib
from typing import Any, Dict, Optional

logger = logging.getLogger("azure.ai.agentserver.githubcopilot")

_FOUNDRY_TOOLBOX_FEATURE_HEADER = "Toolboxes=V1Preview"
_FOUNDRY_TOOLBOX_SERVER_KEY = "foundry-toolbox"
_FOUNDRY_SCOPE = "https://ai.azure.com/.default"


# ---------------------------------------------------------------------------
# Discovery
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

    # 2. Explicit toolbox endpoint (takes precedence over mcp.json only when
    #    the key is absent — callers that want to override should remove the
    #    key from their mcp.json).
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

    # Ensure any server loaded from mcp.json that already declares
    # "Foundry-Features" gets auto-auth stamped too, and any server
    # without an explicit Authorization header gets _auto_auth.
    # Also inject the Foundry-Features header for toolbox endpoints
    # (URLs containing /toolboxes/) that don't already have it.
    for server in servers.values():
        headers = server.setdefault("headers", {})
        if "Authorization" not in headers:
            headers["_auto_auth"] = True
        # Auto-inject Foundry-Features for toolbox endpoints
        url = server.get("url", "")
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
        headers = server.get("headers", {})
        if headers.get("_auto_auth"):
            headers["Authorization"] = f"Bearer {token}"


def make_sdk_safe_mcp_config(servers: Dict[str, Any]) -> Dict[str, Any]:
    """Return a deep copy of *servers* with internal flags stripped.

    The Copilot SDK does not understand ``_auto_auth`` or other internal
    flags (keys starting with ``_``).  This helper produces a clean copy
    safe for ``create_session(**sdk_config)``.
    """
    clean = copy.deepcopy(servers)
    for server in clean.values():
        headers = server.get("headers", {})
        # Remove all internal flags
        for key in [k for k in headers if k.startswith("_")]:
            del headers[key]
    return clean
