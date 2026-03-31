# LangGraph Human-in-the-Loop Sample

This sample demonstrates how to create an intelligent agent with human-in-the-loop capabilities using LangGraph and Azure AI Agent Server. The agent can interrupt its execution to ask for human input when needed, making it ideal for scenarios requiring human judgment or additional information.

## Overview

The sample consists of several key components:

- **LangGraph Agent**: An AI agent that can intelligently decide when to ask humans for input during task execution
- **Human Interrupt Mechanism**: Uses LangGraph's `interrupt()` function to pause execution and wait for human feedback
- **Azure AI Agent Server Adapter**: Hosts the LangGraph agent as an HTTP service

## Files Description

- `main.py` - The main LangGraph agent implementation with human-in-the-loop capabilities
- `requirements.txt` - Python dependencies for the sample



## Setup

1. **Environment Configuration**
   
   Create a `.env` file in this directory with your Azure OpenAI configuration:
   ```env
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
   ```
   
   Alternatively, if you're using Azure Identity (without API key), ensure your Azure credentials are configured.

2. **Install Dependencies**
   
   Install the required Python packages:
   ```bash
   pip install python-dotenv
   pip install azure-ai-agentserver[langgraph]
   ```

## Usage

### Running the Agent Server

1. Start the agent server:
   ```bash
   python main.py
   ```
   The server will start on `http://localhost:8088`

### Making Requests

#### Initial Request (Triggering Human Input)

Send a request that will cause the agent to ask for human input:

```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {
      "name": "local_agent",
      "type": "agent_reference"
    },
    "stream": false,
    "input": "Ask the user where they are, then look up the weather there."
  }'
```

**Response Structure:**

The agent will respond with an interrupt request:

```json
{
  "conversation": {
    "id": "conv_abc123..."
  },
  "output": [
    {
      "type": "function_call",
      "name": "__hosted_agent_adapter_interrupt__",
      "call_id": "call_xyz789...",
      "arguments": "{\"question\": \"Where are you located?\"}"
    }
  ]
}
```

#### Providing Human Feedback

Resume the conversation by providing the human's response:

```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {
      "name": "local_agent",
      "type": "agent_reference"
    },
    "stream": false,
    "input": [
      {
        "type": "function_call_output",
        "call_id": "call_xyz789...",
        "output": "{\"resume\": \"San Francisco\"}"
      }
    ],
    "conversation": {
      "id": "conv_abc123..."
    }
  }'
```

**Final Response:**

The agent will continue execution and provide the final result:

```json
{
  "conversation": {
    "id": "conv_abc123..."
  },
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": "I looked up the weather in San Francisco. Result: It's sunny in San Francisco."
    }
  ]
}
```
