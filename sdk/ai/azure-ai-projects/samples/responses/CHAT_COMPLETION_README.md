# Chat Completion Samples for AIProjectClient

This directory contains samples demonstrating various chat completion scenarios using the Azure AI Projects SDK.

## Overview

These samples show how to use the `AIProjectClient` with OpenAI's Responses API to perform chat completions. The Responses API provides a modern interface for conversational AI interactions.

## Available Samples

### Basic Samples

1. **[sample_chat_completion_basic.py](sample_chat_completion_basic.py)**
   - Basic single-turn chat completions
   - Using system instructions
   - Multi-turn conversations with `previous_response_id`
   - **Synchronous version**

2. **[sample_chat_completion_basic_async.py](sample_chat_completion_basic_async.py)**
   - Same functionality as the basic sample
   - **Asynchronous version** using `async/await`

### Streaming

3. **[sample_chat_completion_streaming.py](sample_chat_completion_streaming.py)**
   - Streaming responses for real-time output
   - Handling streaming events
   - Streaming with conversation history

### Conversation Management

4. **[sample_chat_completion_conversation.py](sample_chat_completion_conversation.py)**
   - Multi-turn conversation management
   - Context preservation across turns
   - Using system instructions consistently
   - Helper function for conversation turns

5. **[sample_chat_completion_with_messages.py](sample_chat_completion_with_messages.py)**
   - Explicit message history management
   - Working with message arrays
   - Role-based conversations
   - Building complex conversation flows

### Advanced Features

6. **[sample_chat_completion_advanced.py](sample_chat_completion_advanced.py)**
   - Temperature control (deterministic vs. creative)
   - Token limits with `max_output_tokens`
   - Top-p (nucleus sampling)
   - Presence and frequency penalties
   - Metadata for request tracking
   - Combining multiple parameters

## Prerequisites

Before running any sample:

```bash
pip install "azure-ai-projects>=2.0.0" python-dotenv
```

For async samples, also install:
```bash
pip install aiohttp
```

## Environment Variables

Set these environment variables (e.g., in a `.env` file):

```bash
# Required for all samples
FOUNDRY_PROJECT_ENDPOINT=https://<your-ai-services-account-name>.services.ai.azure.com/api/projects/<your-project-name>
FOUNDRY_MODEL_NAME=<your-model-deployment-name>
```

You can find:
- **FOUNDRY_PROJECT_ENDPOINT**: In the Overview page of your Microsoft Foundry portal
- **FOUNDRY_MODEL_NAME**: Under the "Name" column in the "Models + endpoints" tab

## Key Concepts

### AIProjectClient

The `AIProjectClient` is the main entry point for interacting with your Azure AI Foundry project:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

with AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
) as project_client:
    # Use the client
    pass
```

### OpenAI Client

Get an authenticated OpenAI client from the project client:

```python
with project_client.get_openai_client() as openai_client:
    # Use responses API
    response = openai_client.responses.create(...)
```

### Responses API

The Responses API provides chat completion functionality:

```python
response = openai_client.responses.create(
    model="gpt-4",
    input="Your prompt here",
    instructions="System instructions",  # Optional
    previous_response_id=response_id,    # For multi-turn
)
```

### Conversation Continuity

To maintain context across turns, use `previous_response_id`:

```python
# First turn
response1 = openai_client.responses.create(
    model=model,
    input="What is Python?",
)

# Second turn (maintains context)
response2 = openai_client.responses.create(
    model=model,
    input="What are its advantages?",
    previous_response_id=response1.id,
)
```

### Streaming

For real-time response streaming:

```python
with openai_client.responses.stream(
    model=model,
    input="Tell me a story",
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
```

## Common Parameters

- **model**: The deployment name of your AI model
- **input**: User message (string or array of messages)
- **instructions**: System-level instructions (optional)
- **previous_response_id**: ID from previous response for context
- **temperature**: 0.0-2.0 (lower = deterministic, higher = creative)
- **max_output_tokens**: Maximum tokens in response
- **top_p**: Nucleus sampling parameter (0.0-1.0)
- **presence_penalty**: -2.0 to 2.0 (encourage new topics)
- **frequency_penalty**: -2.0 to 2.0 (reduce repetition)
- **metadata**: Custom metadata for tracking

## Running the Samples

```bash
# Basic sample
python sample_chat_completion_basic.py

# Async sample
python sample_chat_completion_basic_async.py

# Streaming
python sample_chat_completion_streaming.py

# Conversation management
python sample_chat_completion_conversation.py

# Message history
python sample_chat_completion_with_messages.py

# Advanced parameters
python sample_chat_completion_advanced.py
```

## Additional Resources

- [Azure AI Projects SDK Documentation](https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme)
- [OpenAI Responses API Reference](https://platform.openai.com/docs/api-reference/responses/create?lang=python)
- [Azure AI Foundry Portal](https://ai.azure.com/)

## Tips

1. **Start with basic samples** to understand the flow
2. **Use streaming** for better user experience in interactive applications
3. **Maintain conversation context** with `previous_response_id` for coherent multi-turn conversations
4. **Experiment with temperature** to find the right balance for your use case
5. **Use async versions** for better performance in concurrent scenarios
6. **Add metadata** to track and analyze your API usage
