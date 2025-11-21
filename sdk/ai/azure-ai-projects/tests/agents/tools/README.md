# Azure AI Agent Tools Tests

This directory contains comprehensive tests for Azure AI Agents with various tool capabilities. These tests demonstrate how agents can be enhanced with different tools to perform specialized tasks like searching documents, executing code, calling custom functions, and more.

## 📁 Directory Structure

```
tests/agents/tools/
├── README.md                                    # This file
├── test_agent_*.py                              # Single-tool tests
├── test_agent_tools_with_conversations.py       # Single tools + conversations
└── multitool/                                   # Multi-tool combinations
    ├── test_agent_*_and_*.py                    # Dual-tool tests
    ├── test_agent_*_*_*.py                      # Three-tool tests
    └── test_multitool_with_conversations.py     # Multi-tools + conversations
```

## 🔧 Tool Types & Architecture

### Server-Side Tools (Automatic Execution)
These tools are executed entirely on the server. No client-side dispatch loop required.

| Tool | Test File | What It Does |
|------|-----------|--------------|
| **FileSearchTool** | `test_agent_file_search.py` | Searches uploaded documents using vector stores |
| **CodeInterpreterTool** | `test_agent_code_interpreter.py` | Executes Python code in sandboxed environment |
| **AzureAISearchAgentTool** | `test_agent_ai_search.py` | Queries Azure AI Search indexes |
| **BingGroundingTool** | `test_agent_bing_grounding.py` | Searches the web using Bing API |
| **WebSearchTool** | `test_agent_web_search.py` | Performs web searches |
| **MCPTool** | `test_agent_mcp.py` | Model Context Protocol integrations |

**Usage Pattern:**
```python
# Server-side tools - just create and go!
response = openai_client.responses.create(
    input="Search for information about...",
    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
)
# Server handles everything - no loop needed
print(response.output_text)
```

### Client-Side Tools (Manual Dispatch Loop)
These tools require client-side execution logic. You must implement a dispatch loop.

| Tool | Test File | What It Does |
|------|-----------|--------------|
| **FunctionTool** | `test_agent_function_tool.py` | Calls custom Python functions defined in your code |

**Usage Pattern:**
```python
# Client-side tools - requires dispatch loop
response = openai_client.responses.create(
    input="Calculate 15 plus 27",
    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
)

# Check for function calls
for item in response.output:
    if item.type == "function_call":
        # Execute function locally
        result = my_function(json.loads(item.arguments))
        
        # Send result back
        response = openai_client.responses.create(
            input=[FunctionCallOutput(
                call_id=item.call_id,
                output=json.dumps(result)
            )],
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
        )
```

## 📝 Test Categories

### 1. Single-Tool Tests
Each test focuses on one tool type:

- **`test_agent_file_search.py`** - Vector store document search
  - Upload files to vector store
  - Search across multiple documents
  - Citation handling
  - Stream vs non-stream responses

- **`test_agent_code_interpreter.py`** - Python code execution
  - Execute Python calculations
  - Generate data files (CSV, images)
  - File upload and download
  - Error handling

- **`test_agent_function_tool.py`** - Custom function calling
  - Define function schemas
  - Client-side execution loop
  - Multi-turn function calls
  - JSON parameter handling

- **`test_agent_ai_search.py`** - Azure AI Search integration
  - Connect to existing indexes
  - Query with citations
  - Multiple index support

- **`test_agent_bing_grounding.py`** - Bing web search
  - Real-time web queries
  - URL citations
  - Grounding with web sources

- **`test_agent_mcp.py`** - Model Context Protocol
  - GitHub integration
  - Custom MCP servers
  - Tool discovery

- **`test_agent_web_search.py`** - Web search capabilities
- **`test_agent_image_generation.py`** - DALL-E image generation

### 2. Multi-Tool Tests (`multitool/`)
Tests combining multiple tools in a single agent:

- **`test_agent_file_search_and_function.py`**
  - Search documents, then save results via function
  - 4 comprehensive tests demonstrating different workflows

- **`test_agent_code_interpreter_and_function.py`**
  - Generate data with code, save via function
  - Calculate and persist results

- **`test_agent_file_search_and_code_interpreter.py`**
  - Search docs, analyze with Python code
  - Data extraction and processing

- **`test_agent_file_search_code_interpreter_function.py`**
  - All three tools working together
  - Complete analysis workflows

### 3. Conversation State Management
Tests demonstrating multi-turn interactions with state preservation:

#### Single-Tool Conversations (`test_agent_tools_with_conversations.py`)
- **`test_function_tool_with_conversation`**
  - Multiple function calls in one conversation
  - Context preservation (agent remembers previous results)
  - Conversation state verification

- **`test_file_search_with_conversation`**
  - Multiple searches in one conversation
  - Follow-up questions with context

- **`test_code_interpreter_with_conversation`**
  - Sequential code executions
  - Variable/state management across turns

#### Multi-Tool Conversations (`multitool/test_multitool_with_conversations.py`)
- **`test_file_search_and_function_with_conversation`**
  - Mix server-side (FileSearch) and client-side (Function) tools
  - Complex workflow: Search → Follow-up → Save report
  - Verifies both tool types tracked in conversation

## 🔄 Conversation Patterns

Tests demonstrate three patterns for multi-turn interactions:

### Pattern 1: Manual History Management
```python
history = [{"role": "user", "content": "first message"}]
response = client.responses.create(input=history)
history += [{"role": el.role, "content": el.content} for el in response.output]
history.append({"role": "user", "content": "follow-up"})
response = client.responses.create(input=history)
```

### Pattern 2: Using `previous_response_id`
```python
response_1 = client.responses.create(input="first message")
response_2 = client.responses.create(
    input="follow-up",
    previous_response_id=response_1.id
)
```

### Pattern 3: Using Conversations API (Recommended)
```python
conversation = client.conversations.create()
response_1 = client.responses.create(
    input="first message",
    conversation=conversation.id
)
response_2 = client.responses.create(
    input="follow-up",
    conversation=conversation.id
)
```

⚠️ **Important:** When using `conversation` parameter, do NOT use `previous_response_id` - they are mutually exclusive.

### Conversation State Verification
Tests verify conversation state by reading back all items:
```python
all_items = list(client.conversations.items.list(conversation.id))
# Verify all user messages, assistant messages, tool calls preserved
```

## ⚙️ Environment Setup

### Required Environment Variables

Tool tests require additional environment variables beyond the basic SDK tests:

```bash
# Core settings (already in base .env)
AZURE_AI_PROJECTS_TESTS_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o

# Tool-specific connections (needed for tool tests)
AZURE_AI_PROJECTS_TESTS_BING_CONNECTION_ID=/subscriptions/.../connections/your-bing-connection
AZURE_AI_PROJECTS_TESTS_AI_SEARCH_CONNECTION_ID=/subscriptions/.../connections/your-search-connection
AZURE_AI_PROJECTS_TESTS_AI_SEARCH_INDEX_NAME=your-index-name
AZURE_AI_PROJECTS_TESTS_MCP_PROJECT_CONNECTION_ID=/subscriptions/.../connections/your-mcp-connection
```

### 🚀 Quick Setup with Auto-Discovery

Use the `generate_env_file.py` script to automatically discover your project's configuration:

```bash
# Navigate to the project directory
cd sdk/ai/azure-ai-projects

# Run the generator with your project endpoint
uv run python scripts/generate_env_file.py \
  "https://your-project.services.ai.azure.com/api/projects/your-project" \
  myproject

# This creates: .env.generated.myproject
```

The script will automatically discover:
- ✅ Available model deployments
- ✅ Bing connection (if configured)
- ✅ AI Search connection (if configured)
- ✅ GitHub/MCP connections (if configured)

**Then copy the discovered values to your main `.env` file:**

```bash
# Review the generated file
cat .env.generated.myproject

# Copy relevant values to your .env
# You may need to manually add the AI Search index name
```

### Manual Setup

If you prefer manual setup or need specific connections:

1. **Go to Azure AI Foundry**: https://ai.azure.com
2. **Open your project**
3. **Navigate to "Connections" tab**
4. **Copy connection IDs** (full resource paths starting with `/subscriptions/...`)
5. **Add to your `.env` file**

For AI Search index name:
1. Go to your AI Search service
2. Navigate to "Indexes" tab
3. Copy the index name

## 🧪 Running Tests

### Run All Tool Tests
```bash
pytest tests/agents/tools/ -v
```

### Run Single-Tool Tests Only
```bash
pytest tests/agents/tools/test_agent_*.py -v
```

### Run Multi-Tool Tests Only
```bash
pytest tests/agents/tools/multitool/ -v
```

### Run Conversation Tests
```bash
# Single-tool conversations
pytest tests/agents/tools/test_agent_tools_with_conversations.py -v

# Multi-tool conversations
pytest tests/agents/tools/multitool/test_multitool_with_conversations.py -v
```

### Run Specific Tool Tests
```bash
# Function tool
pytest tests/agents/tools/test_agent_function_tool.py -v

# File search
pytest tests/agents/tools/test_agent_file_search.py -v

# Code interpreter
pytest tests/agents/tools/test_agent_code_interpreter.py -v
```

### Run Single Test
```bash
pytest tests/agents/tools/test_agent_function_tool.py::TestAgentFunctionTool::test_agent_function_tool -v -s
```