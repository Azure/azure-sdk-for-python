"""OpenAPI-validated agent example.

Demonstrates how to supply an OpenAPI spec to AgentServer so that
incoming requests are validated automatically. Invalid requests receive
a 400 response before ``invoke`` is called.

The spec is also served at ``GET /invocations/docs/openapi.json`` so
that callers can discover the agent's contract at runtime.

Usage::

    # Start the agent
    python openapi_validated_agent.py

    # Fetch the OpenAPI spec
    curl http://localhost:8088/invocations/docs/openapi.json

    # Valid request (200)
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"name": "Alice", "language": "fr"}'
    # -> {"greeting": "Bonjour, Alice!"}

    # Invalid request — missing required "name" field (400)
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"language": "en"}'
    # -> {"error": ["'name' is a required property"]}
"""
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver import AgentServer

# Define a simple OpenAPI 3.0 spec inline. In production this could be
# loaded from a YAML/JSON file.
OPENAPI_SPEC: dict[str, Any] = {
    "openapi": "3.0.0",
    "info": {"title": "Greeting Agent", "version": "1.0.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "Name of the person to greet.",
                                    },
                                    "language": {
                                        "type": "string",
                                        "enum": ["en", "es", "fr"],
                                        "description": "Language for the greeting.",
                                    },
                                },
                                "additionalProperties": False,
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Greeting response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["greeting"],
                                    "properties": {
                                        "greeting": {"type": "string"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        }
    },
}

GREETINGS = {
    "en": "Hello",
    "es": "Hola",
    "fr": "Bonjour",
}


class GreetingAgent(AgentServer):
    """Agent that greets a user in the requested language.

    The OpenAPI spec enforces that "name" is required, "language" must be
    one of ``en``, ``es``, or ``fr``, and no extra fields are allowed.
    Requests that violate the schema are rejected with 400 before reaching
    ``invoke``.
    """

    def __init__(self) -> None:
        super().__init__(openapi_spec=OPENAPI_SPEC)

    async def invoke(self, request: Request) -> Response:
        """Return a localised greeting.

        :param request: The raw Starlette request.
        :type request: starlette.requests.Request
        :return: JSON greeting response.
        :rtype: starlette.responses.JSONResponse
        """
        data = await request.json()
        language = data.get("language", "en")
        prefix = GREETINGS.get(language, "Hello")
        greeting = f"{prefix}, {data['name']}!"
        return JSONResponse({"greeting": greeting})


if __name__ == "__main__":
    agent = GreetingAgent()
    agent.run()
