# mypy: ignore-errors
"""simple_invoke_agent — /invoke only, with stream and non-stream modes.

This sample shows how to implement :meth:`~azure.ai.agentserver.core.FoundryCBAgent.agent_invoke`
for the ``/invoke`` endpoint. Stream vs non-stream mode is chosen by the caller via the
``Content-Type`` request header:

* ``Content-Type: application/json``     → JSON response
* ``Content-Type: text/event-stream``    → SSE (server-sent events) streaming response

The ``/runs`` and ``/responses`` endpoints are intentionally **not** used in this sample.

Run the server::

    python main.py

Then use the companion test script::

    python test_invoke_client.py

Or send requests manually with ``curl``:

Non-streaming::

    curl -s -X POST http://localhost:8088/invoke \\
        -H "Content-Type: application/json" \\
        -d '{"message": "Hello world"}'

Streaming::

    curl -s -X POST http://localhost:8088/invoke \\
        -H "Content-Type: text/event-stream" \\
        -d '{"message": "Hello world"}'
"""

import json

from starlette.responses import JSONResponse, StreamingResponse

from azure.ai.agentserver.core import AgentInvokeContext, AgentRunContext, FoundryCBAgent


# ---------------------------------------------------------------------------
# Streaming helper
# ---------------------------------------------------------------------------


async def _sse_stream(message: str):
    """Async generator that yields SSE-formatted chunks for *message*, one word per event.

    Each event has the form::

        data: {"delta": "<word> "}\n\n

    The final event is::

        data: [DONE]\n\n

    :param message: The full message text to stream token by token.
    :type message: str
    """
    tokens = message.split(" ")
    for i, token in enumerate(tokens):
        piece = token if i == len(tokens) - 1 else token + " "
        yield f"data: {json.dumps({'delta': piece})}\n\n"
    yield "data: [DONE]\n\n"


# ---------------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------------


class SimpleInvokeAgent(FoundryCBAgent):
    """A :class:`FoundryCBAgent` focused exclusively on the ``/invoke`` endpoint.

    :meth:`agent_invoke` inspects the ``Content-Type`` request header to choose
    between a plain JSON response and an SSE streaming response:

    * ``Content-Type: application/json``  → :class:`~starlette.responses.JSONResponse`
    * ``Content-Type: text/event-stream`` → :class:`~starlette.responses.StreamingResponse`

    ``/runs`` and ``/responses`` are not used; :meth:`agent_run` raises
    :class:`NotImplementedError` to signal this clearly.
    """

    async def agent_run(self, context: AgentRunContext):
        """Not used in this sample.

        :param context: The agent run context (unused).
        :type context: AgentRunContext
        :raises NotImplementedError: Always. Use ``POST /invoke`` instead.
        """
        raise NotImplementedError(
            "This sample focuses on /invoke. Use POST /invoke instead of /runs or /responses."
        )

    async def agent_invoke(self, context: AgentInvokeContext):
        """Handle ``/invoke`` requests in streaming or non-streaming mode.

        The ``Content-Type`` request header selects the response mode:

        * ``text/event-stream`` → SSE stream (one word per ``data`` event, ends with ``[DONE]``)
        * anything else         → single JSON object

        :param context: Invocation context carrying HTTP headers and the parsed JSON payload.
        :type context: AgentInvokeContext
        :return: A :class:`~starlette.responses.JSONResponse` for non-streaming mode, or a
            :class:`~starlette.responses.StreamingResponse` (SSE) for streaming mode.
        :rtype: starlette.responses.Response
        """
        content_type = context.headers.get("content-type", "")
        is_stream = "text/event-stream" in content_type
        message = context.payload.get("message", "Hello from SimpleInvokeAgent.")

        print(f"[agent_invoke] stream={is_stream}, message={message!r}")

        if is_stream:
            return StreamingResponse(
                _sse_stream(message),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            )

        return JSONResponse(
            {
                "status": "ok",
                "mode": "non-stream",
                "message": message,
            }
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

agent = SimpleInvokeAgent(project_endpoint="mock-endpoint")

if __name__ == "__main__":
    agent.run()
