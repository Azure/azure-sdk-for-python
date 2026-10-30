# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Run resolved sample pytest nodes against the Bicep-created project, without recording."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

REQUIRED_BINDINGS = {"AZURE_SUBSCRIPTION_ID", "AZURE_TENANT_ID", "AZURE_RESOURCE_GROUP"}
SECRET_NAME_SEGMENTS = {"PAT", "SECRET", "KEY", "TOKEN", "PASSWORD", "CREDENTIAL", "CREDENTIALS"}


def allowed_environment_names(plan: dict) -> set[str]:
    """Names the plan declared for the saved state; they become pytest CLI options."""
    names = plan.get("environmentBindings")
    if (
        not isinstance(names, list)
        or not REQUIRED_BINDINGS <= set(names)
        or any(not isinstance(name, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*", name) for name in names)
    ):
        raise ValueError("The deployment plan must list its environment bindings.")
    if any(SECRET_NAME_SEGMENTS & set(name.split("_")) for name in names):
        raise ValueError("The deployment plan must not list secret-looking environment bindings.")
    return set(names)


def require_validation_endpoint() -> str:
    """Read the existing validation project only from the task environment."""
    endpoint = os.environ.get("LLM_VALIDATION_PROJECT_ENDPOINT", "")
    if not re.fullmatch(r"https://[A-Za-z0-9-]+\.services\.ai\.azure\.com/api/projects/[A-Za-z0-9._-]+/?", endpoint):
        raise ValueError(
            "Set LLM_VALIDATION_PROJECT_ENDPOINT as a pipeline environment variable containing an existing Foundry project endpoint. "
            "The value was suppressed; no validator will be provisioned."
        )
    return endpoint


def build_command(state: dict, junit_path: Path) -> list[str]:
    if state.get("schemaVersion") != 1 or state.get("status") != "Ready":
        raise ValueError("Bicep provisioning must complete before tests can run.")
    if state.get("plan", {}).get("queueName") not in {"q1", "q2", "q3", "q4"}:
        raise ValueError("Deployment state must identify one of the four test queues.")
    environment = state.get("environment", {})
    allowed = allowed_environment_names(state.get("plan", {}))
    if set(environment) - allowed or any(not environment.get(name) for name in allowed):
        raise ValueError("Deployment state must contain only the expected non-secret environment bindings.")
    for environment_name, state_key, label in (
        ("AZURE_SUBSCRIPTION_ID", "subscriptionId", "subscription"),
        ("AZURE_TENANT_ID", "tenantId", "tenant"),
    ):
        value = state.get(state_key, "")
        planned_value = state.get("plan", {}).get(state_key, "")
        environment_value = environment[environment_name]
        if (
            not isinstance(value, str)
            or not re.fullmatch(r"[a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}", value)
            or not isinstance(planned_value, str)
            or planned_value.lower() != value.lower()
            or not isinstance(environment_value, str)
            or environment_value.lower() != value.lower()
        ):
            raise ValueError(f"Deployment state, plan and {environment_name} must identify the same explicit {label}.")
    tests = state.get("plan", {}).get("selectedTests", [])
    nodes = [test["node_id"] for test in tests]
    if not nodes or any(
        not re.fullmatch(r"tests/samples/test_samples(?:_async)?\.py::TestSamples(?:Async)?::\w+\[[^\r\n]+\]", node)
        for node in nodes
    ):
        raise ValueError("Only collected sync/async sample test nodes may be executed.")
    arguments = [
        sys.executable,
        "-m",
        "pytest",
        *nodes,
        "-p",
        "sample_ci_attachments",
        f"--sample-attachments-dir={junit_path.resolve().parent / 'attachments'}",
        "-o",
        "junit_logging=system-out",
        "-o",
        "junit_log_passing_tests=true",
        "-o",
        "log_cli=false",
        "-o",
        "addopts=",
        "-v",
        "--capture=fd",
        "--tb=short",
        f"--junitxml={junit_path}",
        "--azure-test-run-live=true",
        "--azure-skip-live-recording=true",
    ]
    # Supplying CLI environment options prevents conftest from replacing live values with .env/defaults.
    for name, value in sorted(environment.items()):
        if not isinstance(value, str):
            raise ValueError("Deployment environment bindings must be strings.")
        # The harness has no tenant CLI option; preserve this authentication setting in the environment only.
        if value and name != "AZURE_TENANT_ID":
            arguments.append(f"--{name.lower().replace('_', '-')}={value}")
    return arguments


def wait_for_project(endpoint: str, timeout: float = 600) -> None:
    from azure.core.exceptions import HttpResponseError  # pylint: disable=import-outside-toplevel
    from azure.identity import AzureCliCredential  # pylint: disable=import-outside-toplevel
    from azure.ai.projects import AIProjectClient  # pylint: disable=import-outside-toplevel

    deadline = time.monotonic() + timeout
    with AzureCliCredential() as credential, AIProjectClient(endpoint, credential) as client:
        while True:
            try:
                next(iter(client.agents.list(limit=1, connection_timeout=10, read_timeout=30, retry_total=0)), None)
                print("Project/RBAC readiness succeeded; selected sample tests may now start.")
                return
            except HttpResponseError as error:
                remaining = deadline - time.monotonic()
                # A freshly provisioned Standard project can return this specific index timeout as
                # invalid_configuration rather than a 5xx. Do not retry other configuration errors.
                agent_index_timeout = getattr(error.error, "code", None) == "invalid_configuration" and re.match(
                    r"^Listing agents timed out after \d+(?:\.\d+)?s while reading the agent index\.",
                    getattr(error.error, "message", "") or "",
                )
                if error.status_code not in {403, 404, 409, 429, 500, 502, 503, 504} and not agent_index_timeout:
                    raise
                reason = "agent-index-timeout" if agent_index_timeout else "propagation-or-service-error"
                if remaining <= 0:
                    raise TimeoutError(
                        f"Project readiness did not succeed within {timeout:g}s "
                        f"(HTTP {error.status_code}, {reason}); sample not started."
                    ) from None
                print(
                    f"Waiting for project/RBAC readiness (HTTP {error.status_code}, {reason}); "
                    "sample not yet started."
                )
                time.sleep(min(10, remaining))
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        f"Project readiness did not succeed within {timeout:g}s "
                        f"(HTTP {error.status_code}, {reason}); sample not started."
                    ) from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path)
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--check-validation-config", action="store_true")
    parser.add_argument("--package-root", type=Path, default=Path(__file__).resolve().parents[3])
    arguments = parser.parse_args()
    require_validation_endpoint()
    if arguments.check_validation_config:
        print(
            "External validation project environment variable is configured; no Azure resources were queried or changed."
        )
        return 0
    if arguments.state is None or arguments.junit is None:
        parser.error("--state and --junit are required when running samples")
    state = json.loads(arguments.state.read_text(encoding="utf-8-sig"))
    command = build_command(state, arguments.junit)
    if os.environ.get("SAMPLE_QUEUE_NAME", "") != state["plan"]["queueName"]:
        raise ValueError("The task SAMPLE_QUEUE_NAME does not match the deployment state; sample not started.")
    for environment_name, state_key in (("AZURE_SUBSCRIPTION_ID", "subscriptionId"), ("AZURE_TENANT_ID", "tenantId")):
        if os.environ.get(environment_name, "").lower() != state[state_key].lower():
            raise ValueError(f"The task {environment_name} does not match the deployment state; sample not started.")
    environment = os.environ.copy()
    environment.update(state["environment"])
    environment.update(
        PYTHON_DOTENV_DISABLED="true",
        AZURE_TEST_RUN_LIVE="true",
        AZURE_SKIP_LIVE_RECORDING="true",
        AZURE_TEST_USE_CLI_AUTH="true",
        AZURE_TOKEN_CREDENTIALS="AzureCliCredential",
        PYTEST_ADDOPTS="",
        PYTHONIOENCODING="utf-8",
    )
    environment.pop("MCP_GITHUB_PAT", None)
    environment.pop("SYSTEM_ACCESSTOKEN", None)
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(arguments.package_root), str(Path(__file__).resolve().parent), environment.get("PYTHONPATH", ""))
    )
    # Readiness is read-only; retry propagation errors, never retry a partially executed sample.
    os.environ["PYTHON_DOTENV_DISABLED"] = "true"
    wait_for_project(state["environment"]["FOUNDRY_PROJECT_ENDPOINT"])
    arguments.junit.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.run(command, cwd=arguments.package_root, env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
