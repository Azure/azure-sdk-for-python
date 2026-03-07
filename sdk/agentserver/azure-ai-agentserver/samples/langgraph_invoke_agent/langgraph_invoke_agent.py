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


graph = build_graph()
server = AgentServer(enable_tracing=True, application_insights_connection_string="InstrumentationKey=efbaa4ed-85a7-4f78-bbc2-d95992bb105c;IngestionEndpoint=https://northcentralus-0.in.applicationinsights.azure.com/;LiveEndpoint=https://northcentralus.livediagnostics.monitor.azure.com/;ApplicationId=0dfc87c6-8f2e-40bc-905c-16177a696d73")


async def _stream_response(user_message: str) -> AsyncGenerator[bytes, None]:
    """Async generator that yields response chunks.

    :param user_message: The user message to process.
    :type user_message: str
    :return: An async generator yielding JSON-encoded byte chunks.
    :rtype: AsyncGenerator[bytes, None]
    """
    async for event in graph.astream_events(
        {"messages": [{"role": "user", "content": user_message}]},
        version="v2",
    ):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"].content
            if chunk:
                yield json.dumps({"delta": chunk}).encode() + b"\n"


@server.invoke_handler
async def handle_invoke(request: Request) -> Response:
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
        return StreamingResponse(_stream_response(user_message))

    result = await graph.ainvoke(
        {"messages": [{"role": "user", "content": user_message}]}
    )
    last_message = result["messages"][-1]
    return JSONResponse({"reply": last_message.content})


if __name__ == "__main__":
    server.run()
