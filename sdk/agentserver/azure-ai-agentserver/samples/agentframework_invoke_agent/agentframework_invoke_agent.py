"""Agent Framework agent served via /invoke.

Customer owns the AgentFramework <-> invoke conversion logic.
This replaces the need for azure-ai-agentserver-agentframework.

Usage::

    # Start the agent
    python agentframework_invoke_agent.py

    # Send a request
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"input": "What is the weather in Seattle?"}'
    # -> {"result": "The weather in Seattle is sunny with a high of 25°C."}
"""
import asyncio
import os
from random import randint
from typing import Annotated

from dotenv import load_dotenv

load_dotenv()

from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver import AgentServer


# -- Customer defines their tools --

def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


# -- Customer builds their Agent Framework agent --

def build_agent() -> Agent:
    """Create an Agent Framework Agent with tools."""
    client = AzureOpenAIChatClient(credential=DefaultAzureCredential())
    return client.as_agent(
        instructions="You are a helpful weather assistant.",
        tools=get_weather,
    )


# -- Customer-managed adapter: Agent Framework <-> /invoke --

agent = build_agent()
server = AgentServer()


@server.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Process an invocation via Agent Framework.

    :param request: The raw Starlette request.
    :type request: starlette.requests.Request
    :return: JSON response with the agent result.
    :rtype: starlette.responses.JSONResponse
    """
    data = await request.json()
    user_input = data.get("input", "")

    # Run the agent
    response = await agent.run(user_input)
    result = response.content if hasattr(response, "content") else str(response)

    return JSONResponse({"result": result})


if __name__ == "__main__":
    server.run()
