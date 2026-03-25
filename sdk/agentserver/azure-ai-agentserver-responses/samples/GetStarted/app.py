# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""GettingStarted sample for azure-ai-agentserver-responses.

Run:
    python samples/GetStarted/app.py
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterable
from typing import Any

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from azure.ai.agentserver.responses import response_handler, ResponseContext
from azure.ai.agentserver.responses.models._generated import CreateResponse
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from azure.ai.agentserver.responses.hosting import map_responses_server


@response_handler
def my_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event) -> AsyncIterable[dict[str, Any]]:
    async def _events() -> AsyncIterable[dict[str, Any]]:
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))

        yield stream.emit_created()
        yield stream.emit_in_progress()

        message_item = stream.add_output_item_message()
        yield message_item.emit_added()

        text_content = message_item.add_text_content()
        yield text_content.emit_added()
        yield text_content.emit_delta("Hello from the Python GettingStarted sample!")
        yield text_content.emit_done()
        yield message_item.emit_content_done(text_content)

        yield message_item.emit_done()

        yield stream.emit_completed()

    return _events()


def create_app() -> Starlette:
    app = Starlette()
    app.add_route("/ready", lambda request: JSONResponse({"status": "ready"}), methods=["GET"])
    map_responses_server(app, my_handler)
    return app


def main() -> None:
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=5100)


if __name__ == "__main__":
    main()
