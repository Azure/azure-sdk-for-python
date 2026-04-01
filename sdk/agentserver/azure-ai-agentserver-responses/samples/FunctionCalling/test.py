# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Requests-based test client for the FunctionCalling sample.

Usage:
    python samples/FunctionCalling/test.py
"""

from __future__ import annotations

import json
from typing import Any

import requests

BASE_URL = "http://127.0.0.1:5101"
CONVERSATION_ID = "conv_a1b2c3d4e5f6789800WeatherConvSampleDemoRequest0001"


def _print_header(title: str) -> None:
    print(f"\n--- {title} ---")


def _pretty_print(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _assert_ok(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(f"HTTP request failed: {response.status_code} {response.text}") from exc


def _turn_1_request_function_call() -> str:
    _print_header("Turn 1: Request function call")
    payload = {
        "model": "test",
        "conversation": CONVERSATION_ID,
        "input": "What is the weather in Seattle?",
    }
    response = requests.post(f"{BASE_URL}/responses", json=payload, timeout=10)
    _assert_ok(response)
    body = response.json()
    _pretty_print(body)

    output = body.get("output")
    if not isinstance(output, list) or not output:
        raise RuntimeError("Turn 1 response does not include output items")

    call_id = output[0].get("call_id") if isinstance(output[0], dict) else None
    if not isinstance(call_id, str) or not call_id:
        raise RuntimeError("Turn 1 response did not include a function call_id")

    print(f"Extracted call_id: {call_id}")
    return call_id


def _turn_2_submit_function_output(call_id: str) -> None:
    _print_header("Turn 2: Submit function output (JSON)")
    payload = {
        "model": "test",
        "conversation": CONVERSATION_ID,
        "input": [
            {
                "type": "function_call_output",
                "call_id": call_id,
                "output": '{"temperature": 72, "condition": "sunny"}',
            }
        ],
    }
    response = requests.post(f"{BASE_URL}/responses", json=payload, timeout=10)
    _assert_ok(response)
    _pretty_print(response.json())


def _turn_2_submit_function_output_streaming(call_id: str) -> None:
    _print_header("Turn 2: Submit function output (streaming)")
    payload = {
        "model": "test",
        "stream": True,
        "conversation": CONVERSATION_ID,
        "input": [
            {
                "type": "function_call_output",
                "call_id": call_id,
                "output": '{"temperature": 72, "condition": "sunny"}',
            }
        ],
    }
    with requests.post(f"{BASE_URL}/responses", json=payload, stream=True, timeout=30) as response:
        _assert_ok(response)
        for line in response.iter_lines(decode_unicode=True):
            if line:
                print(line)


def main() -> None:
    call_id = _turn_1_request_function_call()
    _turn_2_submit_function_output(call_id)
    _turn_2_submit_function_output_streaming(call_id)


if __name__ == "__main__":
    main()
