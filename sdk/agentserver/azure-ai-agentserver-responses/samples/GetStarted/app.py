"""GettingStarted sample for azure-ai-agentserver-responses.

Run:
    python samples/GetStarted/app.py
"""

from __future__ import annotations

from collections.abc import AsyncIterable
from typing import Any

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from azure.ai.agentserver.responses._event_stream import ResponseEventStream
from azure.ai.agentserver.responses._hosting import map_responses_server


class EchoHandler:
    """Simple handler that yields a deterministic response lifecycle."""

    def create_async(self, request: Any, context: Any, cancellation_signal: Any) -> AsyncIterable[dict[str, Any]]:
        async def _events() -> AsyncIterable[dict[str, Any]]:
            stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))

            yield stream.emit_created(status="in_progress")
            yield stream.emit_in_progress()

            output_item = stream.add_output_item(output_index=0)
            yield output_item.emit_added(item={"id": "item-1", "type": "message", "status": "in_progress"})
            yield output_item.emit_delta(item={"delta": "Hello from the Python GettingStarted sample!"})
            yield output_item.emit_done(item={"id": "item-1", "type": "message", "status": "completed"})

            yield stream.emit_completed()

        return _events()


def create_app() -> Starlette:
    app = Starlette()
    app.add_route("/ready", lambda request: JSONResponse({"status": "ready"}), methods=["GET"])
    map_responses_server(app, EchoHandler())
    return app


app = create_app()


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=5100)


if __name__ == "__main__":
    main()
