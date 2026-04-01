# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Requests-based test client for the MultiOutput sample.

Usage:
    python samples/MultiOutput/test.py
"""

from __future__ import annotations

import json
from typing import Any

import requests

BASE_URL = "http://127.0.0.1:5102"


def _print_header(title: str) -> None:
    print(f"\n--- {title} ---")


def _pretty_print(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _assert_ok(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(f"HTTP request failed: {response.status_code} {response.text}") from exc


def _default_mode() -> None:
    _print_header("Default mode (JSON) - reasoning + message")
    payload = {"model": "test"}
    response = requests.post(f"{BASE_URL}/responses", json=payload, timeout=10)
    _assert_ok(response)
    body = response.json()
    _pretty_print(body)

    output = body.get("output")
    if not isinstance(output, list) or len(output) < 2:
        raise RuntimeError("Expected at least two output items (reasoning + message)")


def _stream_mode() -> None:
    _print_header("Streaming mode (SSE)")
    payload = {"model": "test", "stream": True}
    with requests.post(f"{BASE_URL}/responses", json=payload, stream=True, timeout=30) as response:
        _assert_ok(response)
        for line in response.iter_lines(decode_unicode=True):
            if line:
                print(line)


def main() -> None:
    _default_mode()
    _stream_mode()


if __name__ == "__main__":
    main()
