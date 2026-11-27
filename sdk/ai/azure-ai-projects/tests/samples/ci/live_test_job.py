# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Validate one queue's deployment state for the shared Python live-test job."""

import argparse
import json
import os
from pathlib import Path

from run_samples import require_validation_endpoint, validate_deployment_state, wait_for_project


def load_live_test_state(path: Path) -> dict:
    if any(os.environ.get(name) != "true" for name in ("AZURE_TEST_RUN_LIVE", "AZURE_SKIP_LIVE_RECORDING")):
        raise ValueError("The live-test job requires live tests with recording disabled.")
    validator = require_validation_endpoint()
    state = json.loads(path.read_text(encoding="utf-8-sig"))
    nodes = validate_deployment_state(state)
    if len(nodes) != len(set(nodes)):
        raise ValueError("The queue deployment plan contains duplicate sample tests.")
    if os.environ.get("SAMPLE_QUEUE_NAME") != state["plan"]["queueName"]:
        raise ValueError("The task queue does not match the deployment state.")
    for name, key in (
        ("AZURE_SUBSCRIPTION_ID", "subscriptionId"),
        ("AZURE_TENANT_ID", "tenantId"),
    ):
        if os.environ.get(name, "").lower() != state[key].lower():
            raise ValueError(f"{name} must match the deployment state.")
    endpoint = state["environment"]["FOUNDRY_PROJECT_ENDPOINT"]
    if endpoint.rstrip("/").lower() == validator.rstrip("/").lower():
        raise ValueError("The output-validation project must be separate from the sample project.")
    return state


def normalize_collected_node(path: Path, node_id: str, package_root: Path) -> str:
    try:
        relative_path = path.resolve().relative_to(package_root.resolve()).as_posix()
    except ValueError:
        return ""
    _, separator, suffix = node_id.partition("::")
    return f"{relative_path}::{suffix}" if separator else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--check-ready", action="store_true")
    arguments = parser.parse_args()
    if not arguments.check_ready:
        parser.error("--check-ready is required.")
    state = load_live_test_state(arguments.state)
    wait_for_project(state["environment"]["FOUNDRY_PROJECT_ENDPOINT"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
