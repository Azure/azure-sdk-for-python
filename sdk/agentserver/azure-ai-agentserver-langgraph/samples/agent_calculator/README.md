# LangGraph Agent Calculator Sample

This sample demonstrates how to create a calculator agent using LangGraph and using it with Container Agent Adapter. The agent can perform basic arithmetic operations (addition, multiplication, and division) by utilizing tools and making decisions about when to use them.

## Overview

The sample consists of several key components:

- **LangGraph Agent**: A calculator agent that uses tools to perform arithmetic operations
- **Azure AI Agents Adapter**: Adapters of the LangGraph agents. It hosts the agent as a service on your local machine.


## Files Description

- `langgraph_agent_calculator.py` - The main LangGraph agent implementation with calculator tools
- `main.py` - HTTP server entry point using the agents adapter
- `.env-template` A template of environment variables for Azure OpenAI configuration



## Setup

1. **Environment Configuration**
   Create a `.env` file in this directory with your Azure OpenAI configuration:
   ```
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```
   And install python-dotenv
   ```bash
   cd  container_agents/container_agent_adapter/python
   pip install python-dotenv
   ```

2. **Install Dependencies**
   Required Python packages (install via pip):
   ```bash
   cd  container_agents/container_agent_adapter/python
   pip install -e .[langgraph]
   ```

## Usage

### Running as HTTP Server

1. Start the agent server:
   ```bash
   python main.py
   ```
   The server will start on `http://localhost:8088`

2. Test the agent:
   ```bash
   curl -X POST http://localhost:8088/responses \
     -H "Content-Type: application/json" \
     -d '{
       "agent": {
         "name": "local_agent",
         "type": "agent_reference"
       },
       "stream": false,
       "input": "What is 15 divided by 3?"
     }'
   ```
   
   or 

   ```bash
   curl -X POST http://localhost:8088/responses \
     -H "Content-Type: application/json" \
     -d '{
       "agent": {
         "name": "local_agent",
         "type": "agent_reference"
       },
       "stream": false,
       "input": [{
          "type": "message",
          "role": "user",
          "content": [{"type": "input_text", "text": "What is 3 add 5?"}]
        }]
     }'
   ```