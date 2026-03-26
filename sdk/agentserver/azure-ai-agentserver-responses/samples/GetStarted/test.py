# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Smoke-test script for the GetStarted sample.

Usage:
    python samples/GetStarted/test.py
"""

from __future__ import annotations

import json
import time
from typing import Any

import requests

BASE_URL = "http://127.0.0.1:5100"


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
    _print_header("Default mode (JSON)")
    payload = {"model": "gpt-4o-mini", "input": "hello"}
    response = requests.post(f"{BASE_URL}/responses", json=payload, timeout=10)
    _assert_ok(response)
    _pretty_print(response.json())


def _stream_mode() -> None:
    _print_header("Streaming mode (SSE)")
    payload = {"model": "gpt-4o-mini", "input": "hello", "stream": True}
    with requests.post(f"{BASE_URL}/responses", json=payload, stream=True, timeout=30) as response:
        _assert_ok(response)
        for line in response.iter_lines(decode_unicode=True):
            if line:
                print(line)


def _background_mode() -> None:
    _print_header("Background mode (POST then GET)")
    payload = {"model": "gpt-4o-mini", "input": "hello", "background": True}
    create_response = requests.post(f"{BASE_URL}/responses", json=payload, timeout=10)
    _assert_ok(create_response)
    created_payload = create_response.json()
    _pretty_print(created_payload)

    response_id = created_payload.get("id")
    if not isinstance(response_id, str) or not response_id:
        raise RuntimeError("Background response does not include a valid id")

    deadline = time.monotonic() + 5
    while True:
        get_response = requests.get(f"{BASE_URL}/responses/{response_id}", timeout=10)
        _assert_ok(get_response)
        current_payload = get_response.json()
        status = current_payload.get("status")
        if status in {"completed", "failed", "incomplete", "cancelled"}:
            _pretty_print(current_payload)
            return

        if time.monotonic() >= deadline:
            _pretty_print(current_payload)
            raise RuntimeError("Timed out waiting for background response to complete")

        time.sleep(0.2)


def _background_stream_mode() -> None:
    _print_header("Background + Streaming mode (SSE then GET)")
    payload = {"model": "gpt-4o-mini", "input": "hello", "background": True, "stream": True}
    with requests.post(f"{BASE_URL}/responses", json=payload, stream=True, timeout=30) as response:
        _assert_ok(response)
        raw_lines: list[str] = []
        response_id: str | None = None

        for line in response.iter_lines(decode_unicode=True):
            if line is None:
                continue
            if line:
                raw_lines.append(line)
                print(line)

                if response_id is None and line.startswith("data:"):
                    data_str = line.split(":", 1)[1].strip()
                    try:
                        data_payload = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    # Response ID is nested under data_payload["response"]["id"]
                    # (e.g. response.created event), not at the top level.
                    candidate = data_payload.get("response", {}).get("id")
                    if isinstance(candidate, str) and candidate:
                        response_id = candidate

        if response_id is None:
            raise RuntimeError(
                "Could not extract response id from background+stream SSE output. "
                f"Collected lines: {raw_lines}"
            )

    get_response = requests.get(f"{BASE_URL}/responses/{response_id}", timeout=10)
    _assert_ok(get_response)
    _pretty_print(get_response.json())


def _get_replay_mode() -> None:
    _print_header("GET replay mode (background+stream response)")
    payload = {"model": "gpt-4o-mini", "input": "hello", "background": True, "stream": True}

    with requests.post(f"{BASE_URL}/responses", json=payload, stream=True, timeout=30) as create_response:
        _assert_ok(create_response)
        response_id: str | None = None

        for line in create_response.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("data:"):
                data_str = line.split(":", 1)[1].strip()
                try:
                    data_payload = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                candidate = data_payload.get("response", {}).get("id")
                if isinstance(candidate, str) and candidate:
                    response_id = candidate
                    break

    if response_id is None:
        raise RuntimeError("Replay test could not find response id from create stream")

    replay_response = requests.get(f"{BASE_URL}/responses/{response_id}?stream=true", stream=True, timeout=30)
    _assert_ok(replay_response)
    try:
        saw_event = False
        for line in replay_response.iter_lines(decode_unicode=True):
            if line:
                saw_event = True
                print(line)

        if not saw_event:
            raise RuntimeError("Replay stream returned no SSE lines")
    finally:
        replay_response.close()


def main() -> None:
    _default_mode()
    _stream_mode()
    _background_mode()
    _background_stream_mode()
    _get_replay_mode()


if __name__ == "__main__":
    main()
