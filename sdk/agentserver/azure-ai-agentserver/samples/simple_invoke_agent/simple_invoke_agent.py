"""Simple invoke agent example.

Accepts JSON requests, echoes back with a greeting.

Usage::

    # Start the agent
    python simple_invoke_agent.py

    # Send a greeting request
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"name": "Alice"}'
    # -> {"greeting": "Hello, Alice!"}
"""
import json

from azure.ai.agentserver import AgentServer, InvokeRequest


class GreetingAgent(AgentServer):
    """Minimal agent that echoes a greeting."""

    async def invoke(self, request: InvokeRequest) -> bytes:
        """Process the invocation by echoing a greeting.

        :param request: The invocation request.
        :type request: InvokeRequest
        :return: JSON-encoded greeting response.
        :rtype: bytes
        """
        data = json.loads(request.body)
        greeting = f"Hello, {data['name']}!"
        return json.dumps({"greeting": greeting}).encode()


if __name__ == "__main__":
    GreetingAgent().run()
