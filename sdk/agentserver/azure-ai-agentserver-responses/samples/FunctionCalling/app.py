# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""FunctionCalling sample for azure-ai-agentserver-responses.

Run:
    python samples/FunctionCalling/app.py
"""

import asyncio
import json
from collections.abc import AsyncIterable
from typing import Any

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponseContext, ResponseEventStream, get_input_expanded
from azure.ai.agentserver.responses.models import CreateResponse, ItemType


def _extract_function_call_output(request_payload: CreateResponse) -> str | None:
    items = get_input_expanded(request_payload)

    for item in items:
        if isinstance(item, str):
            continue
        if item.get("type") == ItemType.FUNCTION_CALL_OUTPUT:
            return item.get("content", {}).get("output")

    return None


server = ResponsesAgentServerHost(log_level="debug")


@server.create_handler
def weather_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event) -> AsyncIterable[dict[str, Any]]:
    """Two-turn function-calling sample handler."""
    tool_output = _extract_function_call_output(request)

    stream = ResponseEventStream(response_id=context.response_id, model=request.model)

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


def main() -> None:
    server.run(host="127.0.0.1", port=5101)


if __name__ == "__main__":
    main()