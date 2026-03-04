"""Simple invoke agent example.

Accepts JSON requests, echoes back with a greeting.

Usage::

    # Start the agent
    python simple_invoke_agent.py

    # Send a greeting request
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"name": "Alice"}'
    # -> {"greeting": "Hello, Alice!"}
"""
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver import AgentServer


class GreetingAgent(AgentServer):
    """Minimal agent that echoes a greeting."""

    async def invoke(self, request: Request) -> Response:
        """Process the invocation by echoing a greeting.

        :param request: The raw Starlette request.
        :type request: starlette.requests.Request
        :return: JSON greeting response.
        :rtype: starlette.responses.JSONResponse
        """
        data = await request.json()
        greeting = f"Hello, {data['name']}!"
        return JSONResponse({"greeting": greeting})


if __name__ == "__main__":
    GreetingAgent().run()
