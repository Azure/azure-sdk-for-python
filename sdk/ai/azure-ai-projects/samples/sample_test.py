"""
Comprehensive SDK samples for Azure AI Foundry toolbox CRUD operations.

Tested with azure-ai-projects 2.1.0a20260408001.

API: client.beta.toolboxes  (renamed from client.beta.toolsets)
  - create_version(toolbox_name, tools=[], description=..., metadata=..., policies=...)
  - get(toolbox_name)                -> ToolboxObject (id, name, default_version)
  - get_version(toolbox_name, ver)   -> ToolboxVersionObject
  - list()                           -> ItemPaged[ToolboxObject]
  - list_versions(toolbox_name)      -> ItemPaged[ToolboxVersionObject]
  - update(toolbox_name, default_version=ver) -> promote a version to default
  - delete_version(toolbox_name, ver)
  - delete(toolbox_name)

All tool types demonstrated:
  - MCPTool (no-auth, key-auth, OAuth, 1P OBO/UserEntraToken, filtered)
  - OpenApiTool (anonymous, project-connection auth)
  - A2APreviewTool (agent-to-agent)
  - FileSearchTool
  - AzureAISearchTool
  - WebSearchTool / BingCustomSearchConfiguration
  - BingGroundingTool
  - CodeInterpreterTool
  - WorkIQPreviewTool (1P OBO — Outlook mail)
  - Multi-tool combinations

Prerequisites:
  pip install azure-identity python-dotenv
  pip install azure-ai-projects --extra-index-url \\
    https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple --pre
  Set environment variables in .env (see bottom of file).
"""

import json
import os
import sys
import traceback
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MCPTool,
    FileSearchTool,
    OpenApiTool,
    OpenApiFunctionDefinition,
    A2APreviewTool,
    AzureAISearchTool,
    AzureAISearchToolResource,
    AISearchIndexResource,
    CodeInterpreterTool,
    OpenApiAnonymousAuthDetails,
    OpenApiProjectConnectionAuthDetails,
    OpenApiProjectConnectionSecurityScheme,
    WebSearchTool,
    WebSearchConfiguration,
)

load_dotenv()

ENDPOINT = "https://zhuoqunli-ncus.services.ai.azure.com/api/projects/proj1"

credential = DefaultAzureCredential()
client = AIProjectClient(endpoint=ENDPOINT, credential=credential)


# ═══════════════════════════════════════════════════════════════════════════
# Helper: MCP tools/list + tools/call via REST (validates toolbox is live)
# ═══════════════════════════════════════════════════════════════════════════
def _toolbox_mcp_endpoint(toolbox_name: str) -> str:
    """Build the MCP gateway URL for a toolbox."""
    return f"{ENDPOINT}/toolboxes/{toolbox_name}/mcp?api-version=v1"


_MCP_SCOPE = "https://ai.azure.com/.default"
_MCP_FEATURE_HEADER = "Toolboxes=V1Preview"


def _mcp_headers() -> dict:
    token = credential.get_token(_MCP_SCOPE).token
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Foundry-Features": _MCP_FEATURE_HEADER,
    }


def _mcp_tools_list(toolbox_name: str) -> list:
    """Call tools/list on the toolbox MCP endpoint."""
    import httpx

    url = _toolbox_mcp_endpoint(toolbox_name)
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    resp = httpx.post(url, json=payload, headers=_mcp_headers(), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    tools = data.get("result", {}).get("tools", [])
    print(f"  tools/list → {len(tools)} tool(s)")
    for t in tools[:5]:
        print(f"    - {t.get('name', '?')}")
    return tools


def _mcp_tools_call(toolbox_name: str, tool_name: str, arguments: dict) -> dict:
    """Call tools/call on the toolbox MCP endpoint."""
    import httpx

    url = _toolbox_mcp_endpoint(toolbox_name)
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    resp = httpx.post(url, json=payload, headers=_mcp_headers(), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    result = data.get("result", {})
    content = result.get("content", [])
    print(f"  tools/call({tool_name}) → {len(content)} content block(s)")
    if content:
        first = content[0]
        text = first.get("text", "")
        print(f"    preview: {text[:200]}...")
    return result


# ═══════════════════════════════════════════════════════════════════════════
# Lifecycle helpers: create → list versions → new version → promote → delete
# ═══════════════════════════════════════════════════════════════════════════
def _full_lifecycle(toolbox_name: str, tools: list, *, validate_call=None):
    """Run the full CRUD lifecycle for a toolbox.

    1. create_version  (v1)
    2. get
    3. tools/list  (MCP validation)
    4. optional tools/call
    5. create_version  (v2 — same tools, new description)
    6. list_versions
    7. update → promote v2 to default
    8. get_version v2
    9. delete_version v1
    10. delete toolbox
    """
    print(f"\n{'='*60}")
    print(f"LIFECYCLE: {toolbox_name}")
    print(f"{'='*60}")

    # 1. create v1
    v1 = client.beta.toolboxes.create_version(
        toolbox_name=toolbox_name,
        tools=tools,
        description=f"{toolbox_name} v1",
    )
    print(f"  1. create_version → version={v1.version}, name={v1.name}")

    # 2. get toolbox
    tb = client.beta.toolboxes.get(toolbox_name=toolbox_name)
    print(f"  2. get → name={tb.name}, default_version={tb.default_version}")

    # 3. tools/list
    listed_tools = _mcp_tools_list(toolbox_name)

    # 4. optional tools/call
    if validate_call:
        tool_name, args = validate_call
        # find match
        matching = [t for t in listed_tools if t.get("name") == tool_name]
        if matching:
            _mcp_tools_call(toolbox_name, tool_name, args)
        else:
            print(f"  ⚠ tool '{tool_name}' not found in tools/list — skipping call")

    # 5. create v2
    v2 = client.beta.toolboxes.create_version(
        toolbox_name=toolbox_name,
        tools=tools,
        description=f"{toolbox_name} v2 (promoted)",
    )
    print(f"  5. create_version → version={v2.version}")

    # 6. list versions
    versions = list(client.beta.toolboxes.list_versions(toolbox_name=toolbox_name))
    print(f"  6. list_versions → {len(versions)} version(s): {[v.version for v in versions]}")

    # 7. promote v2
    updated = client.beta.toolboxes.update(toolbox_name=toolbox_name, default_version=v2.version)
    print(f"  7. update (promote) → default_version={updated.default_version}")

    # 8. get version v2
    v2_detail = client.beta.toolboxes.get_version(toolbox_name=toolbox_name, version=v2.version)
    print(f"  8. get_version → version={v2_detail.version}, desc={v2_detail.description}")

    # 9. delete v1
    client.beta.toolboxes.delete_version(toolbox_name=toolbox_name, version=v1.version)
    print(f"  9. delete_version v1 → OK")

    # 10. delete toolbox
    client.beta.toolboxes.delete(toolbox_name=toolbox_name)
    print(f" 10. delete → OK")

    return True


# ═══════════════════════════════════════════════════════════════════════════
# Individual tool samples
# ═══════════════════════════════════════════════════════════════════════════


# ---------------------------------------------------------------------------
# 1. MCP — No Auth (public server, e.g. gitmcp.io)
# ---------------------------------------------------------------------------
def sample_mcp_no_auth():
    return _full_lifecycle(
        "mcp-noauth-sample",
        [
            MCPTool(
                server_label="gitmcp",
                server_url="https://gitmcp.io/Azure-Samples/agent-openai-python-prompty",
            )
        ],
    )


def sample_full_lifecycle():
    return _full_lifecycle(
        "full-lifecycle-sample",
        [
            MCPTool(
                server_label="gitmcp",
                server_url="https://gitmcp.io/Azure-Samples/agent-openai-python-prompty",
            )
        ],
    )


# ---------------------------------------------------------------------------
# 2. MCP — Key Auth
# ---------------------------------------------------------------------------
def sample_mcp_key_auth():
    return _full_lifecycle(
        "mcp-keyauth-sample",
        [
            MCPTool(
                server_label="github",
                server_url="https://api.githubcopilot.com/mcp",
                project_connection_id=os.environ["MCP_CONNECTION_ID"],
            )
        ],
    )


# ---------------------------------------------------------------------------
# 3. MCP — OAuth
# ---------------------------------------------------------------------------
def sample_mcp_oauth():
    return _full_lifecycle(
        "mcp-oauth-sample",
        [
            MCPTool(
                server_label="github-oauth",
                server_url="https://api.githubcopilot.com/mcp",
                project_connection_id=os.environ["MCP_OAUTH_CONNECTION_ID"],
            )
        ],
    )


# ---------------------------------------------------------------------------
# 4. MCP — 1P OBO (WorkIQ Mail — UserEntraToken)
# ---------------------------------------------------------------------------
def sample_mcp_workiq_mail():
    return _full_lifecycle(
        "mcp-workiq-mail-sample",
        [
            MCPTool(
                server_label="workiq-mail",
                server_url="https://agent365.svc.cloud.microsoft/agents/servers/mcp_MailTools",
                project_connection_id=os.environ["WORKIQ_MAIL_CONNECTION_ID"],
            )
        ],
    )


# ---------------------------------------------------------------------------
# 5. MCP — Filtered tools
# ---------------------------------------------------------------------------
def sample_mcp_filtered():
    return _full_lifecycle(
        "mcp-filtered-sample",
        [
            MCPTool(
                server_label="github-filtered",
                server_url="https://api.githubcopilot.com/mcp",
                project_connection_id=os.environ["MCP_CONNECTION_ID"],
                allowed_tools=["search_repositories", "get_file_contents"],
                headers={"Accept": "application/json"},
            )
        ],
    )


# ---------------------------------------------------------------------------
# 6. OpenAPI — No Auth (anonymous)
# ---------------------------------------------------------------------------
def sample_openapi_no_auth():
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "JSON Placeholder", "version": "1.0"},
        "servers": [{"url": "https://jsonplaceholder.typicode.com"}],
        "paths": {
            "/posts/{id}": {
                "get": {
                    "operationId": "getPost",
                    "summary": "Get a post by ID",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {"200": {"description": "A post object"}},
                }
            }
        },
    }
    return _full_lifecycle(
        "openapi-noauth-sample",
        [
            OpenApiTool(
                openapi=OpenApiFunctionDefinition(
                    name="jsonplaceholder",
                    spec=spec,
                    auth=OpenApiAnonymousAuthDetails(),
                )
            )
        ],
        validate_call=("getPost", {"id": 1}),
    )


# ---------------------------------------------------------------------------
# 7. OpenAPI — With Project Connection Auth
# ---------------------------------------------------------------------------
def sample_openapi_with_connection():
    spec = {
        "openapi": "3.0.1",
        "info": {"title": "TripAdvisor API", "version": "1.0"},
        "servers": [{"url": "https://api.content.tripadvisor.com/api/v1"}],
        "paths": {
            "/location/search": {
                "get": {
                    "operationId": "searchLocations",
                    "summary": "Search for locations",
                    "parameters": [
                        {
                            "name": "searchQuery",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "language",
                            "in": "query",
                            "schema": {"type": "string", "default": "en"},
                        },
                    ],
                    "responses": {"200": {"description": "Search results"}},
                    "security": [{"apiKeyAuth": []}],
                }
            }
        },
        "components": {
            "securitySchemes": {
                "apiKeyAuth": {
                    "type": "apiKey",
                    "name": "key",
                    "in": "query",
                }
            }
        },
    }
    return _full_lifecycle(
        "openapi-tripadvisor-sample",
        [
            OpenApiTool(
                openapi=OpenApiFunctionDefinition(
                    name="tripadvisor",
                    spec=spec,
                    auth=OpenApiProjectConnectionAuthDetails(
                        security_scheme=OpenApiProjectConnectionSecurityScheme(
                            project_connection_id=os.environ["TRIPADVISOR_CONNECTION_ID"],
                        ),
                    ),
                )
            )
        ],
    )


# ---------------------------------------------------------------------------
# 8. A2A — Agent-to-Agent
# ---------------------------------------------------------------------------
def sample_a2a():
    return _full_lifecycle(
        "a2a-sample",
        [
            A2APreviewTool(
                project_connection_id=os.environ.get("A2A_CONNECTION_ID", ""),
            )
        ],
    )


# ---------------------------------------------------------------------------
# 9. File Search
# ---------------------------------------------------------------------------
def sample_file_search():
    return _full_lifecycle(
        "filesearch-sample",
        [
            FileSearchTool(
                name="filesearch_docs",
                vector_store_ids=[os.environ["FILE_SEARCH_VECTOR_STORE_ID"]],
                description="Search uploaded files for grounded passages.",
            )
        ],
    )


# ---------------------------------------------------------------------------
# 10. Azure AI Search
# ---------------------------------------------------------------------------
def sample_azure_ai_search():
    return _full_lifecycle(
        "aisearch-sample",
        [
            AzureAISearchTool(
                azure_ai_search=AzureAISearchToolResource(
                    indexes=[
                        AISearchIndexResource(
                            index_name=os.environ["AI_SEARCH_INDEX_NAME"],
                            project_connection_id=os.environ["AI_SEARCH_CONNECTION_ID"],
                        )
                    ]
                )
            )
        ],
    )


# ---------------------------------------------------------------------------
# 11. Code Interpreter
# ---------------------------------------------------------------------------
def sample_code_interpreter():
    return _full_lifecycle(
        "codeinterp-sample",
        [CodeInterpreterTool()],
    )


# ---------------------------------------------------------------------------
# 12. Web Search
# ---------------------------------------------------------------------------
def sample_websearch_tool():
    return _full_lifecycle(
        "websearch-sample",
        [WebSearchTool()],
    )


# ---------------------------------------------------------------------------
# 13. Web Search — Bing Custom Search
# ---------------------------------------------------------------------------
def sample_websearch_custom():
    return _full_lifecycle(
        "websearch-customsearch-sample",
        [
            WebSearchTool(
                custom_search_configuration=WebSearchConfiguration(
                    project_connection_id=os.environ["BING_SEARCH_CONNECTION_ID"],
                    instance_name=os.environ["BING_SEARCH_INSTANCE_NAME"],
                )
            )
        ],
    )


# ---------------------------------------------------------------------------
# 14. Multi-Tool (MCP + MCP)
# ---------------------------------------------------------------------------
def sample_multi_tool():
    return _full_lifecycle(
        "multi-tool-sample",
        [
            MCPTool(
                server_label="gitmcp",
                server_url="https://gitmcp.io/Azure-Samples/agent-openai-python-prompty",
            ),
            MCPTool(
                server_label="github",
                server_url="https://api.githubcopilot.com/mcp",
                project_connection_id=os.environ["MCP_CONNECTION_ID"],
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 15. Multi-Tool (file search + MCP)
# ---------------------------------------------------------------------------
def sample_multi_filesearch_mcp():
    return _full_lifecycle(
        "multi-filesearch-mcp-sample",
        [
            FileSearchTool(
                name="filesearch_project_docs",
                vector_store_ids=[os.environ["FILE_SEARCH_VECTOR_STORE_ID"]],
                description="Find relevant passages from uploaded project files.",
            ),
            MCPTool(
                server_label="gitmcp-files",
                server_url="https://gitmcp.io/Azure-Samples/agent-openai-python-prompty",
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 16. Multi-Tool (web search + MCP)
# ---------------------------------------------------------------------------
def sample_multi_websearch_mcp():
    return _full_lifecycle(
        "multi-websearch-mcp-sample",
        [
            WebSearchTool(),
            MCPTool(
                server_label="gitmcp-web",
                server_url="https://gitmcp.io/Azure-Samples/agent-openai-python-prompty",
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 17. Multi-Tool (AI Search + MCP)
# ---------------------------------------------------------------------------
def sample_multi_aisearch_mcp():
    return _full_lifecycle(
        "multi-aisearch-mcp-sample",
        [
            AzureAISearchTool(
                azure_ai_search=AzureAISearchToolResource(
                    indexes=[
                        AISearchIndexResource(
                            index_name=os.environ["AI_SEARCH_INDEX_NAME"],
                            project_connection_id=os.environ["AI_SEARCH_CONNECTION_ID"],
                        )
                    ]
                ),
            ),
            MCPTool(
                server_label="gitmcp-aisearch",
                server_url="https://gitmcp.io/Azure-Samples/agent-openai-python-prompty",
            ),
        ],
    )


# ---------------------------------------------------------------------------
# 18. List all toolboxes
# ---------------------------------------------------------------------------
def sample_list_all():
    toolboxes = list(client.beta.toolboxes.list())
    print(f"\n{len(toolboxes)} toolbox(es):")
    for tb in toolboxes:
        print(f"  {tb.name}  default_version={tb.default_version}")
    return toolboxes


# ═══════════════════════════════════════════════════════════════════════════
# Runner
# ═══════════════════════════════════════════════════════════════════════════
SAMPLES = {
    "full-lifecycle": sample_full_lifecycle,
    "mcp-noauth": sample_mcp_no_auth,
    "mcp-keyauth": sample_mcp_key_auth,
    "mcp-oauth": sample_mcp_oauth,
    "mcp-workiq-mail": sample_mcp_workiq_mail,
    "mcp-filtered": sample_mcp_filtered,
    "openapi-noauth": sample_openapi_no_auth,
    "openapi-conn": sample_openapi_with_connection,
    "a2a": sample_a2a,
    "filesearch": sample_file_search,
    "aisearch": sample_azure_ai_search,
    "codeinterp": sample_code_interpreter,
    "websearch": sample_websearch_tool,
    "websearch-custom": sample_websearch_custom,
    "multi": sample_multi_tool,
    "multi-filesearch-mcp": sample_multi_filesearch_mcp,
    "multi-websearch-mcp": sample_multi_websearch_mcp,
    "multi-aisearch-mcp": sample_multi_aisearch_mcp,
    "list": sample_list_all,
}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) >= 2 else os.getenv("SAMPLE_NAME", "full-lifecycle")

    if target == "all":
        # Run all samples, collect pass/fail report
        results = {}
        for name, fn in SAMPLES.items():
            if name == "list":
                continue
            try:
                fn()
                results[name] = "PASS"
            except Exception as exc:
                results[name] = f"FAIL: {exc}"
                traceback.print_exc()
        print("\n" + "=" * 60)
        print("CRUD TEST REPORT")
        print("=" * 60)
        for name, status in results.items():
            mark = "✓" if status == "PASS" else "✗"
            print(f"  {mark} {name}: {status}")
        passed = sum(1 for v in results.values() if v == "PASS")
        print(f"\n  {passed}/{len(results)} passed")
    elif target in SAMPLES:
        print(f"Running sample: {target}")
        SAMPLES[target]()
    else:
        print(f"Usage: python {sys.argv[0]} <sample|all>")
        print(f"Samples: {', '.join(SAMPLES.keys())}")
        sys.exit(1)
