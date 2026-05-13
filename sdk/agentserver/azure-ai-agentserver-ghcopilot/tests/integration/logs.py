#!/usr/bin/env python3
"""Stream live container console logs from a deployed hosted agent.

Usage:
    python tests/integration/logs.py --name my-agent --session <session-id>

Environment (from .env or shell):
    AZURE_AI_PROJECT_ENDPOINT  — Foundry project endpoint
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

INTEGRATION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = INTEGRATION_DIR.parent.parent  # azure-ai-agentserver-ghcopilot/

# Add integration dir to path for _token_cache import
sys.path.insert(0, str(INTEGRATION_DIR))
from _token_cache import get_access_token

API_VERSION = "2025-05-15-preview"
FOUNDRY_FEATURES = "HostedAgents=V1Preview"


def get_agent_version(endpoint: str, name: str, token: str) -> str:
    url = f"{endpoint}/agents/{name}?api-version={API_VERSION}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
    })
    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        version = data.get("versions", {}).get("latest", {}).get("version", "")
        if not version:
            print(f"No version found for agent '{name}'.", file=sys.stderr)
            sys.exit(1)
        return version
    except urllib.error.HTTPError as e:
        print(f"Failed to get agent '{name}': HTTP {e.code}", file=sys.stderr)
        sys.exit(1)


def stream_logs(endpoint: str, name: str, version: str, session_id: str, token: str):
    url = (
        f"{endpoint}/agents/{name}/versions/{version}"
        f"/sessions/{session_id}:logstream?api-version={API_VERSION}"
    )
    req = urllib.request.Request(url, method="GET", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "text/event-stream",
        "Foundry-Features": FOUNDRY_FEATURES,
    })

    print(f"\nStreaming console logs for {name} v{version} session {session_id}")
    print("Press Ctrl-C to stop.\n")

    try:
        resp = urllib.request.urlopen(req, timeout=300)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        try:
            body = e.read().decode("utf-8", errors="replace")
            if body:
                print(body, file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection failed: {e.reason}", file=sys.stderr)
        sys.exit(1)

    try:
        current_event = "log"
        for raw_line in resp:
            line = raw_line.decode("utf-8", errors="replace").rstrip("\n\r")
            if not line:
                current_event = "log"
                continue
            if line.startswith("event:"):
                current_event = line[6:].strip()
                continue
            if line.startswith("data:"):
                data = line[5:].strip()
                print(f"{current_event}: {data}")
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        resp.close()


def main():
    parser = argparse.ArgumentParser(description="Stream container console logs from a deployed agent")
    parser.add_argument("--name", required=True, help="Agent name")
    parser.add_argument("--session", required=True, help="Session ID (from invoke output)")
    args = parser.parse_args()

    for env_path in [INTEGRATION_DIR / ".env", PROJECT_ROOT / ".env"]:
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

    token = get_access_token()
    version = get_agent_version(endpoint, args.name, token)
    stream_logs(endpoint, args.name, version, args.session, token)


if __name__ == "__main__":
    main()
