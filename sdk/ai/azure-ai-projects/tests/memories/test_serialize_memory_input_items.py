# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, cast
from openai.types.responses import EasyInputMessageParam
from openai.types.responses.response_input_image_param import ResponseInputImageParam
from azure.ai.projects.operations._patch_memories import _serialize_memory_input_items


def _easy_input_message_param(content: str, role: str = "user") -> EasyInputMessageParam:
    return cast(EasyInputMessageParam, {"role": role, "type": "message", "content": content})


def _response_input_image_param(image_url: str) -> ResponseInputImageParam:
    return cast(ResponseInputImageParam, {"type": "input_image", "detail": "low", "image_url": image_url})


def test_serialize_memory_input_items_with_none() -> None:
    assert _serialize_memory_input_items(None) is None


def test_serialize_memory_input_items_with_str() -> None:
    result = _serialize_memory_input_items("hello")
    assert result == [{"role": "user", "type": "message", "content": "hello"}]


def test_serialize_memory_input_items_with_single_easy_input_message_param() -> None:
    items = [_easy_input_message_param("single message")]
    result = _serialize_memory_input_items(items)
    assert result == [{"role": "user", "type": "message", "content": "single message"}]


def test_serialize_memory_input_items_with_three_easy_input_message_params() -> None:
    items = [
        _easy_input_message_param("first", role="user"),
        _easy_input_message_param("second", role="assistant"),
        _response_input_image_param("https://example.com/cat.png"),
    ]
    result = _serialize_memory_input_items(items)
    assert result == [
        {"role": "user", "type": "message", "content": "first"},
        {"role": "assistant", "type": "message", "content": "second"},
        {"type": "input_image", "detail": "low", "image_url": "https://example.com/cat.png"},
    ]


def test_serialize_memory_input_items_with_list_of_dict_messages() -> None:
    items: list[dict[str, Any]] = [
        {"role": "user", "type": "message", "content": "first"},
        {"role": "assistant", "type": "message", "content": "second"},
        {"type": "input_image", "detail": "low", "image_url": "https://example.com/cat.png"},
    ]
    result = _serialize_memory_input_items(items)
    assert result == items
