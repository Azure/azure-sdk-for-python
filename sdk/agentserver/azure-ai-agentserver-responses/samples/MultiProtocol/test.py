# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Smoke-test script for the MultiProtocol sample.

Exercises both the Invocations and Responses protocol endpoints
on the same AgentHost instance.

Usage:
    python samples/MultiProtocol/test.py
"""

from __future__ import annotations

import json
import time
from typing import Any

import requests

BASE_URL = "http://127.0.0.1:8088"


def _print_header(title: str) -> None:
    print(f"\n--- {title} ---")


def _pretty_print(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _assert_ok(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(f"HTTP request failed: {response.status_code} {response.text}") from exc


# =====================================================================
# Health check
# =====================================================================


def _health_check() -> None:
    _print_header("Health check (GET /readiness)")
    response = requests.get(f"{BASE_URL}/readiness", timeout=10)
    _assert_ok(response)
    print(f"Status: {response.status_code}")
    print(response.text)


# =====================================================================
# Invocation protocol
# =====================================================================


def _invocation_echo() -> None:
    _print_header("Invocation protocol — echo")
    payload = {"message": "Hello from invocations!"}
    response = requests.post(f"{BASE_URL}/invocations", json=payload, timeout=10)
    _assert_ok(response)
    body = response.json()
    _pretty_print(body)

    if body.get("status") != "completed":
        raise RuntimeError(f"Expected status 'completed', got '{body.get('status')}'")

    output = body.get("output", "")
    if "Hello from invocations!" not in output:
        raise RuntimeError(f"Echo output missing input text: {output}")

    print(f"Invocation ID: {body.get('invocation_id')}")


# =====================================================================
# Responses protocol
# =====================================================================


def _responses_default_mode() -> None:
    _print_header("Responses protocol — default mode (JSON)")
    payload = {"model": "echo", "input": "Hello from responses!", "stream": False, "store": True}
    response = requests.post(f"{BASE_URL}/responses", json=payload, timeout=10)
    _assert_ok(response)
    body = response.json()
    _pretty_print(body)

    response_id = body.get("id")
    if not isinstance(response_id, str) or not response_id:
        raise RuntimeError("Response does not include a valid id")

    status = body.get("status")
    if status not in {"completed", "in_progress", "queued"}:
        raise RuntimeError(f"Unexpected status: {status}")


def _responses_stream_mode() -> None:
    _print_header("Responses protocol — streaming mode (SSE)")
    payload = {"model": "echo", "input": "Hello from responses!", "stream": True, "store": True}
    with requests.post(f"{BASE_URL}/responses", json=payload, stream=True, timeout=30) as response:
        _assert_ok(response)
        saw_event = False
        for line in response.iter_lines(decode_unicode=True):
            if line:
                saw_event = True
                print(line)

        if not saw_event:
            raise RuntimeError("Streaming response returned no SSE lines")


def _responses_background_mode() -> None:
    _print_header("Responses protocol — background mode (POST then GET)")
    payload = {"model": "echo", "input": "Hello from responses!", "background": True}
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


def _responses_background_stream_mode() -> None:
    _print_header("Responses protocol — background + streaming (SSE then GET)")
    payload = {"model": "echo", "input": "Hello from responses!", "background": True, "stream": True}
    with requests.post(f"{BASE_URL}/responses", json=payload, stream=True, timeout=30) as response:
        _assert_ok(response)
        response_id: str | None = None

        for line in response.iter_lines(decode_unicode=True):
            if line is None:
                continue
            if line:
                print(line)

                if response_id is None and line.startswith("data:"):
                    data_str = line.split(":", 1)[1].strip()
                    try:
                        data_payload = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    candidate = data_payload.get("response", {}).get("id")
                    if isinstance(candidate, str) and candidate:
                        response_id = candidate

    if response_id is None:
        raise RuntimeError("Could not extract response id from background+stream SSE output")

    get_response = requests.get(f"{BASE_URL}/responses/{response_id}", timeout=10)
    _assert_ok(get_response)
    _pretty_print(get_response.json())


def main() -> None:
    _health_check()
    _invocation_echo()
    _responses_default_mode()
    _responses_stream_mode()
    _responses_background_mode()
    _responses_background_stream_mode()


if __name__ == "__main__":
    main()
