# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""JSON serialization helpers for Foundry storage envelope payloads."""

from __future__ import annotations

import json
from typing import Any, Iterable

from ..models._wire import to_wire_dict
from ..models import OutputItem, ResponseObject


def serialize_create_request(
    response: ResponseObject,
    input_items: Iterable[OutputItem] | None,
    history_item_ids: Iterable[str] | None,
) -> bytes:
    """Serialize a create-response request envelope to JSON bytes.

    :param response: The initial response snapshot.
    :type response: ResponseObject
    :param input_items: Resolved output items to store alongside the response.
    :type input_items: Iterable[OutputItem] | None
    :param history_item_ids: Item IDs drawn from a prior conversation turn.
    :type history_item_ids: Iterable[str] | None
    :returns: UTF-8 encoded JSON body.
    :rtype: bytes
    """
    payload: dict[str, Any] = {
        "response": to_wire_dict(response),
        "input_items": [to_wire_dict(item) for item in (input_items or [])],
        "history_item_ids": list(history_item_ids or []),
    }
    return json.dumps(payload).encode("utf-8")


def serialize_response(response: ResponseObject) -> bytes:
    """Serialize a single :class:`ResponseObject` wire snapshot to JSON bytes.

    :param response: The response model to encode.
    :type response: ResponseObject
    :returns: UTF-8 encoded JSON body.
    :rtype: bytes
    """
    return json.dumps(to_wire_dict(response)).encode("utf-8")


def serialize_batch_request(item_ids: list[str]) -> bytes:
    """Serialize a batch-retrieve request to JSON bytes.

    :param item_ids: Ordered list of item IDs to retrieve.
    :type item_ids: list[str]
    :returns: UTF-8 encoded JSON body.
    :rtype: bytes
    """
    return json.dumps({"item_ids": item_ids}).encode("utf-8")


def deserialize_response(body: str) -> ResponseObject:
    """Deserialize a JSON response body into a response wire payload.

    :param body: The raw JSON response text from the storage API.
    :type body: str
    :returns: A response wire payload.
    :rtype: ResponseObject
    """
    return json.loads(body)


def deserialize_paged_items(body: str) -> list[OutputItem]:
    """Deserialize a paged-response JSON body, extracting the ``data`` array.

    Items are returned as dict-native ``OutputItem`` wire payloads.

    :param body: The raw JSON response text from the storage API.
    :type body: str
    :returns: A list of deserialized :class:`OutputItem` instances.
    :rtype: list[OutputItem]
    """
    data = json.loads(body)
    return list(data.get("data", []))


def deserialize_items_array(body: str) -> list[OutputItem | None]:
    """Deserialize a JSON array of items, preserving ``null`` gaps.

    Null entries in the array indicate that no item was found for the
    corresponding ID in a batch-retrieve response.

    :param body: The raw JSON response text from the storage API.
    :type body: str
    :returns: A list of deserialized :class:`OutputItem` instances or ``None`` for missing items.
    :rtype: list[OutputItem | None]
    """
    raw_items: list[dict | None] = json.loads(body)
    result: list[OutputItem | None] = []
    for item in raw_items:
        if item is None:
            result.append(None)
        else:
            result.append(item)  # type: ignore[arg-type]
    return result


def deserialize_history_ids(body: str) -> list[str]:
    """Deserialize a JSON array of history item ID strings.

    :param body: The raw JSON response text from the storage API.
    :type body: str
    :returns: List of item ID strings.
    :rtype: list[str]
    """
    return list(json.loads(body))
