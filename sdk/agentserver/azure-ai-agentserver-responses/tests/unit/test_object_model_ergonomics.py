# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Object-model ergonomics for response payloads."""

from __future__ import annotations

import json

from azure.ai.agentserver.responses.models import (
    CreateResponse,
    ItemMessage,
    MessageContentInputTextContent,
    ResponseModel,
    ResponseObject,
)
from azure.ai.agentserver.responses.models._wire import to_wire_dict


def test_create_response_remains_dict_native_request_payload() -> None:
    request = CreateResponse(model="test-model", input="hello")

    assert type(request) is dict
    assert request["model"] == "test-model"


def test_response_models_support_attribute_access_and_to_dict() -> None:
    response = ResponseObject(
        id="resp_123",
        status="completed",
        output=[
            ItemMessage(
                type="message",
                role="assistant",
                content=[MessageContentInputTextContent(type="input_text", text="hello")],
            )
        ],
    )

    assert isinstance(response, ResponseModel)
    assert response.output[0].content[0].text == "hello"
    assert response.to_dict() == {
        "id": "resp_123",
        "status": "completed",
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "input_text", "text": "hello"}],
            }
        ],
    }


def test_response_models_remain_wire_serializable() -> None:
    message = ItemMessage(
        type="message",
        role="user",
        content=[MessageContentInputTextContent(type="input_text", text="hi")],
    )

    wire = to_wire_dict(message)

    assert wire == {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "hi"}]}
    assert json.dumps(wire)


def test_response_models_can_be_reused_as_later_request_input() -> None:
    response = ResponseObject(
        id="resp_123",
        status="completed",
        output=[
            ItemMessage(
                type="message",
                role="assistant",
                content=[MessageContentInputTextContent(type="input_text", text="previous answer")],
            )
        ],
    )
    request = CreateResponse(model="test-model", input=response.output)

    wire = to_wire_dict(request)

    assert wire == {
        "model": "test-model",
        "input": [
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "input_text", "text": "previous answer"}],
            }
        ],
    }
