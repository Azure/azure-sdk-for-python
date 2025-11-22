# Tool Client Example

This example demonstrates how to use the `ToolClient` with Agent Framework to dynamically access tools from Azure AI Tool Client.

## Overview

The `ToolClient` provides a bridge between Azure AI Tool Client and Agent Framework, allowing agents to access tools configured in your Azure AI project. This example shows how to use a factory function pattern to create agents dynamically with access to tools at runtime.

## Features

- **Dynamic Tool Access**: Agents can list and invoke tools from Azure AI Tool Client
- **Factory Pattern**: Create fresh agent instances per request to avoid concurrency issues
- **Tool Integration**: Seamlessly integrate Azure AI tools with Agent Framework agents

## Prerequisites

- Python 3.10 or later
- Azure AI project with configured tools
- Azure credentials (DefaultAzureCredential)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```
AZURE_AI_PROJECT_ENDPOINT=https://<your-account>.services.ai.azure.com/api/projects/<your-project>
```

3. Ensure your Azure AI project has tools configured (e.g., MCP connections)

## Running the Example

```bash
python agent_factory_example.py
```

## How It Works

1. **Factory Function**: The example creates a factory function that:
   - Receives a `ToolClient` instance
   - Lists available tools from Azure AI Tool Client
   - Creates an Agent Framework agent with those tools
   - Returns the agent instance

2. **Dynamic Agent Creation**: The factory is called for each request, ensuring:
   - Fresh agent instances per request
   - Latest tool configurations
   - No concurrency issues

3. **Tool Access**: The agent can use tools like:
   - MCP (Model Context Protocol) connections
   - Function tools
   - Other Azure AI configured tools

## Key Code Patterns

### Creating a Factory Function

```python
async def agent_factory(tool_client: ToolClient):
    # List tools from Azure AI
    tools = await tool_client.list_tools()
    
    # Create agent with tools
    agent = Agent(
        name="MyAgent",
        model="gpt-4o",
        instructions="You are a helpful assistant.",
        tools=tools
    )
    return agent
```

### Using the Factory

```python
from azure.ai.agentserver.agentframework import from_agent_framework

adapter = from_agent_framework(
    agent_factory,
    credentials=credential,
    tools=[{"type": "mcp", "project_connection_id": "my-mcp"}]
)
```

## Alternative: Direct Agent Usage

You can also use a pre-created agent instead of a factory:

```python
agent = Agent(
    name="MyAgent",
    model="gpt-4o",
    instructions="You are a helpful assistant."
)

adapter = from_agent_framework(agent, credentials=credential)
```

## Troubleshooting

- **No tools found**: Ensure your Azure AI project has tools configured
- **Authentication errors**: Check your Azure credentials and project endpoint
- **Import errors**: Verify all dependencies are installed

## Learn More

- [Azure AI Agent Service Documentation](https://learn.microsoft.com/azure/ai-services/agents/)
- [Agent Framework Documentation](https://github.com/microsoft/agent-framework)
