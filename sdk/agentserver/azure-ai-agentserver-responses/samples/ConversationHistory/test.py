# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Requests-based test client for the ConversationHistory sample.

Usage:
    python samples/ConversationHistory/test.py
"""

from __future__ import annotations

import json
from typing import Any

import requests

BASE_URL = "http://127.0.0.1:5103"


def _print_header(title: str) -> None:
    print(f"\n--- {title} ---")


def _pretty_print(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _assert_ok(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(f"HTTP request failed: {response.status_code} {response.text}") from exc


def _create(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{BASE_URL}/responses", json=payload, timeout=10)
    _assert_ok(response)
    body = response.json()
    _pretty_print(body)
    return body


def _turn_1() -> str:
    _print_header("Turn 1: Initial message (no history)")
    body = _create({"model": "test", "input": "Hello, I am Alice."})
    response_id = body.get("id")
    if not isinstance(response_id, str) or not response_id:
        raise RuntimeError("Turn 1 did not return a valid response id")
    print(f"Response 1 ID: {response_id}")
    return response_id


def _turn_2(previous_response_id: str) -> str:
    _print_header("Turn 2: Chain via previous_response_id")
    body = _create(
        {
            "model": "test",
            "input": "What is 2 + 2?",
            "previous_response_id": previous_response_id,
        }
    )
    response_id = body.get("id")
    if not isinstance(response_id, str) or not response_id:
        raise RuntimeError("Turn 2 did not return a valid response id")
    print(f"Response 2 ID: {response_id}")
    return response_id


def _turn_3(previous_response_id: str) -> str:
    _print_header("Turn 3: Chain again")
    body = _create(
        {
            "model": "test",
            "input": "Thanks for the help!",
            "previous_response_id": previous_response_id,
        }
    )
    response_id = body.get("id")
    if not isinstance(response_id, str) or not response_id:
        raise RuntimeError("Turn 3 did not return a valid response id")
    print(f"Response 3 ID: {response_id}")
    return response_id


def _turn_4_stream(previous_response_id: str) -> None:
    _print_header("Turn 4: Streaming with chained history")
    payload = {
        "model": "test",
        "stream": True,
        "input": "One more thing.",
        "previous_response_id": previous_response_id,
    }
    with requests.post(f"{BASE_URL}/responses", json=payload, stream=True, timeout=30) as response:
        _assert_ok(response)
        for line in response.iter_lines(decode_unicode=True):
            if line:
                print(line)


def main() -> None:
    response_1_id = _turn_1()
    response_2_id = _turn_2(response_1_id)
    response_3_id = _turn_3(response_2_id)
    _turn_4_stream(response_3_id)


if __name__ == "__main__":
    main()
