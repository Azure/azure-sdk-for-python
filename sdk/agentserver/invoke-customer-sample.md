# Customer Sample: Implementing `/invoke`

How to build an agent container that handles the `/invoke` route using `FoundryCBAgent`.

---

## 1. Minimal echo agent

The simplest possible agent — receives JSON, echoes it back.

```python
# echo_agent.py
import json
from azure.ai.agentserver.core import FoundryCBAgent, InvocationContext, InvocationResponse


class EchoAgent(FoundryCBAgent):
    """Echoes back whatever the caller sends."""

    async def agent_run(self, context):
        raise NotImplementedError("This agent only supports /invoke")

    async def agent_invoke(self, context: InvocationContext) -> InvocationResponse:
        body = json.loads(context.body)
        reply = {"output": f"You said: {body.get('input', '')}"}
        return InvocationResponse(
            body=json.dumps(reply).encode(),
            content_type="application/json",
        )


if __name__ == "__main__":
    EchoAgent().run(port=8080)
```

```bash
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": "hello"}'

# → {"output": "You said: hello"}
```

---

## 2. Streaming agent (SSE)

Returns a `text/event-stream` response using an async generator.

```python
# streaming_agent.py
import json
from azure.ai.agentserver.core import FoundryCBAgent, InvocationContext, InvocationResponse


class StreamingAgent(FoundryCBAgent):
    """Streams response tokens as SSE events."""

    async def agent_run(self, context):
        raise NotImplementedError("This agent only supports /invoke")

    async def agent_invoke(self, context: InvocationContext) -> InvocationResponse:
        body = json.loads(context.body)
        user_input = body.get("input", "")

        async def generate():
            # Simulate token-by-token streaming
            words = f"You asked about: {user_input}".split()
            for word in words:
                chunk = json.dumps({"delta": word + " "})
                yield f"data: {chunk}\n\n".encode()
            yield b"data: [DONE]\n\n"

        return InvocationResponse(
            body=generate(),
            content_type="text/event-stream",
        )


if __name__ == "__main__":
    StreamingAgent().run(port=8080)
```

```bash
curl -N -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": "quarterly earnings"}'

# data: {"delta": "You "}
# data: {"delta": "asked "}
# data: {"delta": "about: "}
# data: {"delta": "quarterly "}
# data: {"delta": "earnings "}
# data: [DONE]
```

---

## 3. LangGraph agent with `/invoke`

A LangGraph agent that supports **both** `/runs` (OpenAI Responses API) and `/invoke` (raw bytes).
Subclass `LangGraphAdapter` — it already handles `agent_run()` for `/runs` + `/responses`.
Override `agent_invoke()` to add the invoke route.

```python
# langgraph_invoke_agent.py
import json
from typing import Annotated

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState, add_messages

from azure.ai.agentserver.langgraph import LangGraphAdapter
from azure.ai.agentserver.core import InvocationContext, InvocationResponse


# --- Define a LangGraph graph ---

class State(MessagesState):
    messages: Annotated[list, add_messages]


llm = ChatOpenAI(model="gpt-4o")


async def chat_node(state: State):
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}


graph = StateGraph(State)
graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)
compiled = graph.compile()


# --- Serve it ---

class MyAgent(LangGraphAdapter):
    def __init__(self):
        super().__init__(graph=compiled)

    async def agent_invoke(self, context: InvocationContext) -> InvocationResponse:
        """Handle /invoke: parse raw bytes, run the graph, return raw bytes."""
        body = json.loads(context.body)
        user_input = body.get("input", "")

        # Call the graph directly — no adapter conversion needed
        result = await self.graph.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )

        last_message = result["messages"][-1]
        reply = {"output": last_message.content}
        return InvocationResponse(
            body=json.dumps(reply).encode(),
            content_type="application/json",
        )


if __name__ == "__main__":
    MyAgent().run(port=8080)
```

```bash
# /invoke route (raw bytes)
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": "What is the capital of France?"}'

# → {"output": "The capital of France is Paris."}

# /responses route still works (OpenAI Responses API)
curl -X POST http://localhost:8080/responses \
  -H "Content-Type: application/json" \
  -d '{"input": "What is 2+2?", "model": "gpt-4o"}'
```

> **Key point:** `LangGraphAdapter` provides `agent_run()` for free — you only add
> `agent_invoke()`. Both routes serve the same underlying graph, but with different
> wire formats.

---

## 4. Agent Framework agent with `/invoke`

An Agent Framework agent that supports **both** `/runs` and `/invoke`.
Subclass `AgentFrameworkCBAgent` — it already handles `agent_run()`.
Override `agent_invoke()` to add the invoke route.

```python
# af_invoke_agent.py
import json

from agent_framework import AgentProtocol, Message

from azure.ai.agentserver.agentframework import AgentFrameworkCBAgent
from azure.ai.agentserver.core import InvocationContext, InvocationResponse


# --- Define an Agent Framework agent ---

class MyFrameworkAgent(AgentProtocol):
    async def run(self, message: Message) -> Message:
        return Message(content=f"Processed: {message.content}")

    async def run_stream(self, message: Message):
        yield Message(content=f"Processed: {message.content}")


# --- Serve it ---

class MyAgent(AgentFrameworkCBAgent):
    def __init__(self):
        super().__init__(agent=MyFrameworkAgent())

    async def agent_invoke(self, context: InvocationContext) -> InvocationResponse:
        """Handle /invoke: parse raw bytes, call the framework agent, return raw bytes."""
        body = json.loads(context.body)
        user_input = body.get("input", "")

        # Call the framework agent directly
        result = await self.agent.run(Message(content=user_input))

        reply = {"output": result.content}
        return InvocationResponse(
            body=json.dumps(reply).encode(),
            content_type="application/json",
        )


if __name__ == "__main__":
    MyAgent().run(port=8080)
```

```bash
# /invoke route (raw bytes)
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": "Summarize this document"}'

# → {"output": "Processed: Summarize this document"}

# /responses route still works (OpenAI Responses API)
curl -X POST http://localhost:8080/responses \
  -H "Content-Type: application/json" \
  -d '{"input": "Summarize this document", "model": "gpt-4o"}'
```

> **Key point:** `AgentFrameworkCBAgent` provides `agent_run()` for free. Adding
> `agent_invoke()` lets the same container serve both protocols side-by-side.
