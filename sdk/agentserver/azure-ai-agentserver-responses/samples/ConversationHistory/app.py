# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""ConversationHistory sample for azure-ai-agentserver-responses.

Run:
    python samples/ConversationHistory/app.py
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from azure.ai.agentserver.responses.hosting import map_responses_server
from azure.ai.agentserver.responses._options import ResponsesServerOptions


def _request_mapping(request: Any) -> dict[str, Any]:
    if hasattr(request, "as_dict"):
        candidate = request.as_dict()
        if isinstance(candidate, dict):
            return candidate
    if isinstance(request, dict):
        return request
    return {}


def _extract_current_input_text(request: Any) -> str:
    payload = _request_mapping(request)
    raw_input = payload.get("input")
    if isinstance(raw_input, str):
        return raw_input
    if isinstance(raw_input, list):
        for item in raw_input:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "message":
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get("type") in {"input_text", "output_text"}:
                    text = part.get("text")
                    if isinstance(text, str) and text:
                        return text
    return ""


def _to_mapping(item: Any) -> dict[str, Any]:
    if hasattr(item, "as_dict"):
        candidate = item.as_dict()
        if isinstance(candidate, dict):
            return candidate
    if isinstance(item, dict):
        return item
    return {}


def _extract_text_from_output_message(message_item: dict[str, Any] | None) -> str:
    if not isinstance(message_item, dict):
        return "(none)"

    content = message_item.get("content")
    if not isinstance(content, list):
        return "(no text)"

    for part in content:
        if not isinstance(part, dict):
            continue
        if part.get("type") != "output_text":
            continue
        text = part.get("text")
        if isinstance(text, str):
            return text

    return "(no text)"


def _build_reply(current_input: str, history: Sequence[Any], input_items: Sequence[Any]) -> str:
    del input_items

    if len(history) == 0:
        return f"[Turn 1] No history. You said: \"{current_input}\""

    history_messages = [item for item in (_to_mapping(raw) for raw in history) if item.get("type") == "output_message"]
    turn_number = len(history_messages) + 1
    last_message = history_messages[-1] if history_messages else None
    last_text = _extract_text_from_output_message(last_message)

    return (
        f"[Turn {turn_number}] History has {len(history)} item(s). "
        f"Last assistant message: \"{last_text}\". "
        f"You said: \"{current_input}\""
    )


class ConversationHandler:
    """Conversational handler that reads history via context.get_history_async()."""

    async def create_async(self, request: Any, context: Any, cancellation_signal: Any) -> AsyncIterable[dict[str, Any]]:
        del cancellation_signal

        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))

        yield stream.emit_created()
        yield stream.emit_in_progress()

        history = await context.get_history_async()
        input_items = await context.get_input_items_async()
        current_input = _extract_current_input_text(request)
        reply = _build_reply(current_input, history, input_items)

        message_item = stream.add_output_item_message()
        yield message_item.emit_added()

        text_content = message_item.add_text_content()
        yield text_content.emit_added()
        yield text_content.emit_delta(reply)
        yield text_content.emit_done(reply)
        yield message_item.emit_content_done(text_content)
        yield message_item.emit_done()

        yield stream.emit_completed()


def create_app() -> Starlette:
    app = Starlette()
    app.add_route("/ready", lambda request: JSONResponse({"status": "ready"}), methods=["GET"])
    map_responses_server(app, ConversationHandler(), options=ResponsesServerOptions(default_fetch_history_count=20))
    return app


def main() -> None:
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=5103)


if __name__ == "__main__":
    main()
