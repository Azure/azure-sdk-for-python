#!/usr/bin/env python
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Repair hosted-agent sample recordings with unsanitized multipart metadata.

This script rewrites existing asset recordings in place. It targets the
`agents.create_version_from_code(...)` multipart request shape used by hosted
agent code-upload samples:

1. Find request entries whose multipart body contains a `metadata` part.
2. Decode the `b64:`-encoded JSON payload for that part.
3. Sanitize hosted-agent environment variable values and related fields.
4. Re-encode the payload and update the recorded `Content-Length` header.

The repair is intended for cases where a recording is already bad and you want
to salvage it without doing a fresh live re-record.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

SANITIZED_ACCOUNT_NAME = "sanitized-account-name"
SANITIZED_PROJECT_NAME = "sanitized-project-name"
SANITIZED_HOSTED_AGENT_NAME = "sanitized-hosted-agent-name"
SANITIZED_MODEL_DEPLOYMENT_NAME = "sanitized-model-deployment-name"
SANITIZED_PROJECT_ENDPOINT = (
    f"https://{SANITIZED_ACCOUNT_NAME}.services.ai.azure.com/api/projects/{SANITIZED_PROJECT_NAME}"
)
SANITIZED_MODEL_ENDPOINT = f"https://{SANITIZED_ACCOUNT_NAME}.services.ai.azure.com"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _recordings_roots() -> list[Path]:
    package_relative_path = _package_root().relative_to(_repo_root())
    recordings_roots = []
    for asset_dir in sorted((_repo_root() / ".assets").glob("*")):
        recordings_root = asset_dir / "python" / package_relative_path / "tests" / "recordings" / "samples"
        if recordings_root.is_dir():
            recordings_roots.append(recordings_root)
    return recordings_roots


def _node_id_to_recording_filename(node_id: str) -> str:
    node_parts = node_id.split("::")
    if len(node_parts) < 2:
        raise ValueError(
            "Test id must be a pytest node id like " "'path/to/test_file.py::TestClass::test_method[param]'"
        )

    file_name = Path(node_parts[0]).name
    return f"{file_name}{''.join(node_parts[1:])}.json"


def _resolve_recording_target(target: str) -> Path:
    candidate_path = Path(target)
    if candidate_path.is_file():
        return candidate_path

    if "::" not in target:
        raise FileNotFoundError(f"Recording file not found: {target}")

    recording_filename = _node_id_to_recording_filename(target)
    matches = [root / recording_filename for root in _recordings_roots() if (root / recording_filename).is_file()]

    if not matches:
        raise FileNotFoundError(
            f"Could not resolve pytest node id to a recording file: {target}\n"
            f"Expected filename: {recording_filename}"
        )

    if len(matches) > 1:
        matches_text = "\n".join(str(match) for match in matches)
        raise FileExistsError(f"Pytest node id matched multiple recording files for {target}:\n{matches_text}")

    return matches[0]


def _sanitize_string(value: str) -> str:
    """Normalize hosted-agent values commonly leaked into sample recordings."""
    if not value:
        return value

    if re.fullmatch(r"https?://[^/]+\.services\.ai\.azure\.com/api/projects/[^/?#]+", value):
        return SANITIZED_PROJECT_ENDPOINT

    if re.fullmatch(r"https?://[^/]+\.services\.ai\.azure\.com/?", value):
        return SANITIZED_MODEL_ENDPOINT

    if "/api/projects/" in value and "/toolboxes/" in value and "/mcp" in value:
        return re.sub(
            r"https?://[^/]+\.services\.ai\.azure\.com/api/projects/[^/?#]+",
            SANITIZED_PROJECT_ENDPOINT,
            value,
        )

    if value.startswith("gpt-"):
        return SANITIZED_MODEL_DEPLOYMENT_NAME

    if value.startswith("hosted-") or value.startswith("sanitized-hosted-agent-name"):
        return SANITIZED_HOSTED_AGENT_NAME

    return value


def _sanitize_env_vars(environment_variables: dict[str, Any]) -> bool:
    changed = False
    replacements = {
        "FOUNDRY_PROJECT_ENDPOINT": SANITIZED_PROJECT_ENDPOINT,
        "MODEL_ENDPOINT": SANITIZED_MODEL_ENDPOINT,
        "FOUNDRY_MODEL_NAME": SANITIZED_MODEL_DEPLOYMENT_NAME,
        "MODEL_DEPLOYMENT_NAME": SANITIZED_MODEL_DEPLOYMENT_NAME,
        "AZURE_AI_MODEL_DEPLOYMENT_NAME": SANITIZED_MODEL_DEPLOYMENT_NAME,
        "AGENT_NAME": SANITIZED_HOSTED_AGENT_NAME,
    }

    for key, replacement in replacements.items():
        if key in environment_variables and environment_variables[key] != replacement:
            environment_variables[key] = replacement
            changed = True

    if "MCP_SERVER_URL" in environment_variables:
        sanitized_value = _sanitize_string(str(environment_variables["MCP_SERVER_URL"]))
        if environment_variables["MCP_SERVER_URL"] != sanitized_value:
            environment_variables["MCP_SERVER_URL"] = sanitized_value
            changed = True

    return changed


def _sanitize_metadata_payload(metadata_payload: dict[str, Any]) -> bool:
    changed = False

    definition = metadata_payload.get("definition")
    if isinstance(definition, dict):
        environment_variables = definition.get("environment_variables")
        if isinstance(environment_variables, dict):
            changed = _sanitize_env_vars(environment_variables) or changed

    description = metadata_payload.get("description")
    if isinstance(description, str):
        sanitized_description = _sanitize_string(description)
        if sanitized_description != description:
            metadata_payload["description"] = sanitized_description
            changed = True

    return changed


def _sanitize_response_body(response_body: Any) -> bool:
    changed = False
    if not isinstance(response_body, dict):
        return changed

    # Only touch hosted-agent version responses. Other sample resources like
    # skills/toolboxes also carry a `name` field, and rewriting them changes
    # later playback request bodies.
    if response_body.get("object") != "agent.version":
        return False

    if isinstance(response_body.get("name"), str) and response_body["name"] != SANITIZED_HOSTED_AGENT_NAME:
        response_body["name"] = SANITIZED_HOSTED_AGENT_NAME
        changed = True

    definition = response_body.get("definition")
    if isinstance(definition, dict):
        environment_variables = definition.get("environment_variables")
        if isinstance(environment_variables, dict):
            changed = _sanitize_env_vars(environment_variables) or changed

    return changed


def _repair_request_body_lines(request_body: list[str]) -> tuple[list[str], bool]:
    lines = list(request_body)
    changed = False

    for index, line in enumerate(lines):
        if not isinstance(line, str) or not line.startswith("b64:"):
            continue

        previous_line = lines[index - 1] if index > 0 else ""
        if previous_line != "\r\n":
            continue

        disposition_line = lines[index - 2] if index > 1 else ""
        if 'name="metadata"' not in disposition_line:
            continue

        decoded = base64.b64decode(line[4:]).decode("utf-8")
        metadata_payload = json.loads(decoded)
        original_payload = deepcopy(metadata_payload)
        payload_changed = _sanitize_metadata_payload(metadata_payload)
        normalized_json = json.dumps(metadata_payload)
        formatting_changed = decoded != normalized_json
        if not payload_changed and not formatting_changed:
            continue

        if payload_changed or formatting_changed or metadata_payload != original_payload:
            # Match the runtime multipart JSON formatting closely so playback
            # body comparison does not fail on whitespace-only differences.
            encoded = base64.b64encode(normalized_json.encode("utf-8")).decode("ascii")
            lines[index] = f"b64:{encoded}"
            changed = True

    return lines, changed


def _update_content_length(entry: dict[str, Any]) -> bool:
    request_body = entry.get("RequestBody")
    request_headers = entry.get("RequestHeaders")
    if not isinstance(request_body, list) or not isinstance(request_headers, dict):
        return False

    content_type = str(request_headers.get("Content-Type", ""))
    if "multipart/form-data" not in content_type:
        return False

    total_length = 0
    for line in request_body:
        if isinstance(line, str) and line.startswith("b64:"):
            total_length += len(base64.b64decode(line[4:]))
        elif isinstance(line, str):
            total_length += len(line.encode("utf-8"))

    content_length = str(total_length)
    if request_headers.get("Content-Length") != content_length:
        request_headers["Content-Length"] = content_length
        return True

    return False


def repair_recording(recording_path: Path) -> tuple[bool, int]:
    payload = json.loads(recording_path.read_text(encoding="utf-8"))
    changed = False
    repaired_entries = 0

    if isinstance(payload, dict) and isinstance(payload.get("Entries"), list):
        entries = payload["Entries"]
    elif isinstance(payload, list):
        entries = payload
    else:
        raise ValueError(f"Recording file does not contain a supported recording entry list: {recording_path}")

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        request_body = entry.get("RequestBody")
        if isinstance(request_body, list):
            repaired_request_body, body_changed = _repair_request_body_lines(request_body)
            if body_changed:
                entry["RequestBody"] = repaired_request_body
                changed = True
                repaired_entries += 1

        response_body = entry.get("ResponseBody")
        if _sanitize_response_body(response_body):
            changed = True

        if _update_content_length(entry):
            changed = True

    if changed:
        recording_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return changed, repaired_entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair bad hosted-agent sample recordings in place.")
    parser.add_argument(
        "recording",
        help=(
            "Path to the recording JSON file to repair, or a pytest node id like "
            "'path/to/test_file.py::TestClass::test_method[param]'"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report whether changes would be made without writing the file.",
    )
    args = parser.parse_args()

    try:
        recording_path = _resolve_recording_target(args.recording)
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))

    original_text = recording_path.read_text(encoding="utf-8")
    changed, repaired_entries = repair_recording(recording_path)

    if args.dry_run:
        recording_path.write_text(original_text, encoding="utf-8")

    if changed:
        action = "Would repair" if args.dry_run else "Repaired"
        repaired_entry_label = "entry" if repaired_entries == 1 else "entries"
        print(f"{action} {repaired_entries} multipart metadata {repaired_entry_label} in {recording_path}")
    else:
        print(f"No hosted-agent multipart metadata changes needed in {recording_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
