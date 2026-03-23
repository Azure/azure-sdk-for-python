#!/usr/bin/env python3
"""Invoke the integration test agent.

Usage:
    python tests/integration/invoke.py --name pkg-test-01 --message "hello"
    python tests/integration/invoke.py --name pkg-test-01 --message "use hello skill" --session s1

Environment (from .env or shell):
    AZURE_AI_PROJECT_ENDPOINT  — Foundry project endpoint
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

INTEGRATION_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = INTEGRATION_DIR.parent.parent
TEST_AGENT_DIR = INTEGRATION_DIR / "test_agent"


def run_az(args: list[str]) -> subprocess.CompletedProcess:
    cmd = ["az"] + args
    if sys.platform == "win32":
        return subprocess.run(
            cmd, capture_output=True, encoding="utf-8", errors="replace", shell=True,
        )
    return subprocess.run(cmd, capture_output=True, text=True)


def generate_session_id() -> str:
    return f"session-{uuid.uuid4().hex[:16]}"


def invoke_agent(endpoint: str, name: str, message: str, session_id: str | None = None) -> None:
    api_version = "2025-05-15-preview"
    url = f"{endpoint}/openai/responses?api-version={api_version}"

    sid = session_id or generate_session_id()

    body: dict = {
        "input": message,
        "agent": {"name": name, "type": "agent_reference"},
        "session_id": sid,
        "store": True,
    }

    print(f"Invoking agent '{name}'...")
    print(f"  Session: {sid}")
    print(f"  Message: {message}")
    print()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(body, f)
        body_file = f.name

    try:
        result = run_az([
            "rest", "--method", "POST", "--url", url,
            "--body", f"@{body_file}",
            "--headers", "Content-Type=application/json",
            "--resource", "https://ai.azure.com",
        ])
    finally:
        os.unlink(body_file)

    if result.returncode != 0:
        print(f"Invocation failed.", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    response = json.loads(result.stdout)

    output = response.get("output", [])
    for item in output:
        if item.get("type") == "message":
            content = item.get("content", [])
            for part in content:
                if part.get("type") == "output_text":
                    print(part.get("text", ""))

    resp_session = response.get("session_id")
    if resp_session:
        print(f"\n[session_id: {resp_session}]")


def main():
    parser = argparse.ArgumentParser(description="Invoke integration test agent")
    parser.add_argument("--name", required=True, help="Agent name")
    parser.add_argument("--message", "-m", required=True, help="Message to send")
    parser.add_argument("--session", help="Session ID for multi-turn")
    args = parser.parse_args()

    for env_path in [TEST_AGENT_DIR / ".env", INTEGRATION_DIR / ".env", PACKAGE_ROOT / ".env"]:
        if env_path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
            except ImportError:
                pass
            break

    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("AZURE_AI_PROJECT_ENDPOINT not set.", file=sys.stderr)
        sys.exit(1)

    invoke_agent(endpoint, args.name, args.message, args.session)


if __name__ == "__main__":
    main()
