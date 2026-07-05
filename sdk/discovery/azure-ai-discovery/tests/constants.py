# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Constants used across Discovery SDK tests.

Values are loaded from environment variables with sensible defaults.
Set these in the .env file (loaded by conftest.py via load_dotenv()).
"""
import os

# Workspace
WORKSPACE_ENDPOINT = os.environ.get(
    "AZURE_DISCOVERY_WORKSPACE_ENDPOINT", "https://test-wkspc.workspace.discovery.azure.com"
)
PROJECT_NAME = os.environ.get("AZURE_DISCOVERY_PROJECT_NAME", "test-project")
INVESTIGATION_NAME = os.environ.get("AZURE_DISCOVERY_INVESTIGATION_NAME", "test-invst")

# Bookshelf
BOOKSHELF_ENDPOINT = os.environ.get(
    "AZURE_DISCOVERY_BOOKSHELF_ENDPOINT", "https://test-bkshlf.bookshelf.discovery.azure.com"
)
KNOWLEDGE_BASE_NAME = os.environ.get("KNOWLEDGE_BASE_NAME", "test-kb")
KNOWLEDGE_BASE_VERSION = os.environ.get("KNOWLEDGE_BASE_VERSION", "v1")
KNOWLEDGE_BASE_CREATE_NAME = os.environ.get("KNOWLEDGE_BASE_CREATE_NAME", "test-kb-create")
KNOWLEDGE_BASE_DESCRIPTION = os.environ.get(
    "KNOWLEDGE_BASE_DESCRIPTION",
    "Use this tool to query information about immersion cooling systems or liquid cooling technologies.",
)
KNOWLEDGE_BASE_COPILOT_INSTRUCTION = os.environ.get(
    "KNOWLEDGE_BASE_COPILOT_INSTRUCTION",
    "Use this tool to query information about immersion cooling systems or liquid cooling technologies.",
)
STORAGE_ASSET_ID = os.environ.get(
    "STORAGE_ASSET_ID",
    "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/test-rg/providers/microsoft.discovery/storagecontainers/test-storage/storageassets/test-sa",
)
USER_ASSIGNED_IDENTITY = os.environ.get(
    "USER_ASSIGNED_IDENTITY",
    "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/test-mi",
)

# Agent
AGENT_NAME = os.environ.get("AGENT_NAME", "test-agent")

# Tools
TOOL_ID = os.environ.get(
    "TOOL_ID",
    "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/providers/Microsoft.Discovery/tools/testtool",
)
NODE_POOL_ID = os.environ.get(
    "NODE_POOL_ID",
    "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/providers/Microsoft.Discovery/supercomputers/test-sc/nodePools/nodepool1",
)
BOOKSHELF_NODE_POOL_ID = os.environ.get(
    "BOOKSHELF_NODE_POOL_ID",
    "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/providers/Microsoft.Discovery/supercomputers/test-sc/nodepools/test-pool",
)
OPERATION_ID = os.environ.get("OPERATION_ID", "test-operation-id")

PROJECT_ARM_ID = os.environ.get(
    "PROJECT_ARM_ID",
    "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/providers/Microsoft.Discovery/workspaces/test-wkspc/projects/test-project",
)

# Auth
DISCOVERY_SCOPE = "https://discovery.azure.com/.default"


def investigation_path(project_name: str = PROJECT_NAME, investigation_name: str = INVESTIGATION_NAME) -> str:
    """Return the full resource path for an investigation."""
    return f"/projects/{project_name}/investigations/{investigation_name}"
