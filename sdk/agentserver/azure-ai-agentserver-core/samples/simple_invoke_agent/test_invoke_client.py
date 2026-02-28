"""Test client for simple_invoke_agent.

Sends a non-streaming and a streaming request to ``POST /invoke`` and prints
the results. Start the server before running this script::

    # terminal 1
    python main.py

    # terminal 2
    python test_invoke_client.py

Requirements::

    pip install requests
"""

import json

import requests

BASE_URL = "http://localhost:8088"
PAYLOAD = {"message": "The quick brown fox jumps over the lazy dog"}


# ---------------------------------------------------------------------------
# Non-streaming request
# ---------------------------------------------------------------------------


def test_non_stream() -> None:
    """Send a non-streaming request with ``Content-Type: application/json``."""
    print("=" * 60)
    print("Non-streaming  (Content-Type: application/json)")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/invoke",
        json=PAYLOAD,
        headers={"Content-Type": "application/json"},
    )

    print(f"HTTP status : {response.status_code}")
    print(f"Response    : {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    print()


# ---------------------------------------------------------------------------
# Streaming request
# ---------------------------------------------------------------------------


def test_stream() -> None:
    """Send a streaming request with ``Content-Type: text/event-stream``."""
    print("=" * 60)
    print("Streaming  (Content-Type: text/event-stream)")
    print("=" * 60)

    with requests.post(
        f"{BASE_URL}/invoke",
        data=json.dumps(PAYLOAD).encode(),
        headers={"Content-Type": "text/event-stream"},
        stream=True,
        timeout=30.0,
    ) as response:
        print(f"HTTP status : {response.status_code}")
        print("Deltas      : ")

        for raw_line in response.iter_lines():
            line = raw_line.decode() if isinstance(raw_line, bytes) else raw_line
            line = line.strip()
            if not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if data == "[DONE]":
                print()
                print("[stream complete]")
                break
            chunk = json.loads(data)
            print("\t\t" + chunk["delta"])

    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    test_non_stream()
    test_stream()
