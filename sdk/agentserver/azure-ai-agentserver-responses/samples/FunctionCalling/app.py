# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""FunctionCalling sample for azure-ai-agentserver-responses.

Run:
    python samples/FunctionCalling/app.py
"""

import asyncio
import json

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
def weather_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Two-turn function-calling sample handler."""
    tool_output = _extract_function_call_output(request)

    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield from stream.start()

    if tool_output is not None:
        yield from stream.text_message(f"The weather is: {tool_output}")
    else:
        arguments = json.dumps({"location": "Seattle", "unit": "fahrenheit"})
        yield from stream.function_call("get_weather", "call_weather_1", arguments)

    yield from stream.complete()


def main() -> None:
    server.run(host="127.0.0.1", port=5101)


if __name__ == "__main__":
    main()