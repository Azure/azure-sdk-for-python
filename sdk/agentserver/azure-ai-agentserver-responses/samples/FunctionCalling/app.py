"""FunctionCalling sample for azure-ai-agentserver-responses.

Run:
    python samples/FunctionCalling/app.py
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterable
from typing import Any

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from azure.ai.agentserver.responses.hosting import map_responses_server


def _request_mapping(request: Any) -> dict[str, Any]:
    if hasattr(request, "as_dict"):
        candidate = request.as_dict()
        if isinstance(candidate, dict):
            return candidate
    if isinstance(request, dict):
        return request
    return {}


def _extract_function_call_output(request_payload: dict[str, Any]) -> str | None:
    raw_input = request_payload.get("input")
    if not isinstance(raw_input, list):
        return None

    for item in raw_input:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "function_call_output":
            continue

        output_value = item.get("output")
        if isinstance(output_value, str):
            return output_value

        if isinstance(output_value, (dict, list)):
            return json.dumps(output_value)

        return "{}"

    return None


class WeatherHandler:
    """Two-turn function-calling sample handler."""

    def create_async(self, request: Any, context: Any, cancellation_signal: Any) -> AsyncIterable[dict[str, Any]]:
        async def _events() -> AsyncIterable[dict[str, Any]]:
            payload = _request_mapping(request)
            tool_output = _extract_function_call_output(payload)

            stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))

            yield stream.emit_created()
            yield stream.emit_in_progress()

            if tool_output is not None:
                message_item = stream.add_output_item_message()
                yield message_item.emit_added()

                text_content = message_item.add_text_content()
                yield text_content.emit_added()

                reply = f"The weather is: {tool_output}"
                yield text_content.emit_delta(reply)
                yield text_content.emit_done(reply)
                yield message_item.emit_content_done(text_content)
                yield message_item.emit_done()
            else:
                function_call = stream.add_output_item_function_call("get_weather", "call_weather_1")
                yield function_call.emit_added()

                arguments = json.dumps({"location": "Seattle", "unit": "fahrenheit"})
                yield function_call.emit_arguments_delta(arguments)
                yield function_call.emit_arguments_done(arguments)
                yield function_call.emit_done()

            yield stream.emit_completed()

        return _events()


def create_app() -> Starlette:
    app = Starlette()
    app.add_route("/ready", lambda request: JSONResponse({"status": "ready"}), methods=["GET"])
    map_responses_server(app, WeatherHandler())
    return app


def main() -> None:
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=5101)


if __name__ == "__main__":
    main()