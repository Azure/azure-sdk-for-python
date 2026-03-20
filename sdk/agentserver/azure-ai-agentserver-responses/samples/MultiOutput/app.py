"""MultiOutput sample for azure-ai-agentserver-responses.

Run:
    python samples/MultiOutput/app.py
"""

from __future__ import annotations

from collections.abc import AsyncIterable
from typing import Any

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from azure.ai.agentserver.responses.hosting import map_responses_server


class MultiOutputHandler:
    """Produces reasoning plus final message output in one response."""

    def create_async(self, request: Any, context: Any, cancellation_signal: Any) -> AsyncIterable[dict[str, Any]]:
        async def _events() -> AsyncIterable[dict[str, Any]]:
            stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))

            yield stream.emit_created()
            yield stream.emit_in_progress()

            reasoning_item = stream.add_output_item_reasoning_item()
            yield reasoning_item.emit_added()

            summary_part = reasoning_item.add_summary_part()
            yield summary_part.emit_added()
            yield summary_part.emit_text_delta("Let me think about this...")
            yield summary_part.emit_text_done("Let me think about this...")
            yield summary_part.emit_done()
            reasoning_item.emit_summary_part_done(summary_part)
            yield reasoning_item.emit_done()

            message_item = stream.add_output_item_message()
            yield message_item.emit_added()

            text_content = message_item.add_text_content()
            yield text_content.emit_added()
            yield text_content.emit_delta("Here is my answer.")
            yield text_content.emit_done("Here is my answer.")
            yield message_item.emit_content_done(text_content)
            yield message_item.emit_done()

            yield stream.emit_completed()

        return _events()


def create_app() -> Starlette:
    app = Starlette()
    app.add_route("/ready", lambda request: JSONResponse({"status": "ready"}), methods=["GET"])
    map_responses_server(app, MultiOutputHandler())
    return app


def main() -> None:
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=5102)


if __name__ == "__main__":
    main()