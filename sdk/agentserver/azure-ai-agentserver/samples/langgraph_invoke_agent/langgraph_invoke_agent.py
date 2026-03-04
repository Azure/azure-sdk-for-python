"""LangGraph agent served via /invoke.

Customer owns the LangGraph <-> invoke conversion logic.
This replaces the need for azure-ai-agentserver-langgraph.

Usage::

    # Start the agent
    python langgraph_invoke_agent.py

    # Non-streaming request
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"message": "What is the capital of France?"}'
    # -> {"reply": "The capital of France is Paris."}

    # Streaming request
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"message": "Tell me a joke", "stream": true}'
    # -> {"delta": "Why did..."}
    #    {"delta": " the chicken..."}
"""
import json
import os
from typing import AsyncGenerator

from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import END, START, MessagesState, StateGraph
from langchain_openai import AzureChatOpenAI

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver import AgentServer


def build_graph() -> StateGraph:
    """Customer builds their LangGraph agent as usual."""
    llm = AzureChatOpenAI(
        model=os.environ["AZURE_OPENAI_MODEL"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
    )

    def chatbot(state: MessagesState):
        return {"messages": [llm.invoke(state["messages"])]}

    graph = StateGraph(MessagesState)
    graph.add_node("chatbot", chatbot)
    graph.add_edge(START, "chatbot")
    graph.add_edge("chatbot", END)
    return graph.compile()


class LangGraphInvokeAgent(AgentServer):
    """Customer-managed adapter: LangGraph <-> /invoke protocol."""

    def __init__(self):
        super().__init__()
        self.graph = build_graph()

    async def invoke(self, request: Request) -> Response:
        """Process the invocation via LangGraph.

        :param request: The raw Starlette request.
        :type request: starlette.requests.Request
        :return: JSON response or streaming response.
        :rtype: starlette.responses.Response
        """
        data = await request.json()
        user_message = data["message"]
        stream = data.get("stream", False)

        if stream:
            return StreamingResponse(self._stream_response(user_message))

        result = await self.graph.ainvoke(
            {"messages": [{"role": "user", "content": user_message}]}
        )
        last_message = result["messages"][-1]
        return JSONResponse({"reply": last_message.content})

    async def _stream_response(self, user_message: str) -> AsyncGenerator[bytes, None]:
        """Async generator that yields response chunks.

        :param user_message: The user message to process.
        :type user_message: str
        :return: An async generator yielding JSON-encoded byte chunks.
        :rtype: AsyncGenerator[bytes, None]
        """
        async for event in self.graph.astream_events(
            {"messages": [{"role": "user", "content": user_message}]},
            version="v2",
        ):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:
                    yield json.dumps({"delta": chunk}).encode() + b"\n"


if __name__ == "__main__":
    LangGraphInvokeAgent().run()
