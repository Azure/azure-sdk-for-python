# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
"""GitHub Copilot SDK adapter for Azure AI Agent Server.

Bridges the GitHub Copilot SDK to the Azure AI Foundry hosted agent
platform, translating between the Copilot SDK's event model and the
Foundry Responses API (RAPI) protocol.

Usage::

    from azure.ai.agentserver.github import GitHubCopilotAdapter

    adapter = GitHubCopilotAdapter.from_project(".")
    adapter.run()
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._copilot_adapter import CopilotAdapter, GitHubCopilotAdapter
from ._tool_acl import ToolAcl
from ._version import VERSION

__all__ = [
    "CopilotAdapter",
    "GitHubCopilotAdapter",
    "ToolAcl",
]
__version__ = VERSION
