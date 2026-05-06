#!/usr/bin/env python3
"""Deploy the integration test agent to Azure AI Foundry ADC.

Stages the test_agent/ directory + the package source into a build context,
builds via ACR Tasks, and creates/updates the agent.

Usage:
    python tests/integration/deploy.py --name pkg-test-01 --acr hav2ncusacr

Environment (from .env or shell):
    AZURE_AI_PROJECT_ENDPOINT  — Foundry project endpoint
    GITHUB_TOKEN               — Fine-grained PAT with Copilot Requests Read-only
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

INTEGRATION_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = INTEGRATION_DIR.parent.parent  # azure-ai-agentserver-githubcopilot/
TEST_AGENT_DIR = INTEGRATION_DIR / "test_agent"


def run_az(args: list[str], *, capture: bool = True) -> subprocess.CompletedProcess:
    cmd = ["az"] + args
    is_win = sys.platform == "win32"
    if is_win:
        child_env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
        return subprocess.run(
            cmd, capture_output=True, encoding="utf-8", errors="replace",
            shell=True, env=child_env,
        )
    return subprocess.run(cmd, capture_output=capture, text=True)


def get_access_token(resource: str = "https://ai.azure.com") -> str:
    result = run_az(["account", "get-access-token", "--resource", resource, "--query", "accessToken", "-o", "tsv"])
    if result.returncode != 0:
        print("Failed to get access token. Run 'az login' first.", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def stage_build_context(staging_dir: Path) -> None:
    """Assemble staging directory with test agent + package source."""
    # Copy test agent files
    shutil.copytree(TEST_AGENT_DIR, staging_dir, dirs_exist_ok=True)

    # Copy the package source so Dockerfile can pip install it locally
    pkg_dest = staging_dir / "_package"
    # Copy only the package files (not tests/ or samples/)
    for item in ["azure", "pyproject.toml", "README.md", "LICENSE"]:
        src = PACKAGE_ROOT / item
        dst = pkg_dest / item
        if src.is_dir():
            shutil.copytree(src, dst)
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def build_image(staging_dir: Path, acr: str, name: str, tag: str) -> str:
    full_image = f"{acr}.azurecr.io/{name}:{tag}"
    print(f"Building {full_image} via ACR Tasks...")

    is_win = sys.platform == "win32"

    cmd = ["az", "acr", "build",
           "--registry", acr,
           "--image", f"{name}:{tag}",
           "--platform", "linux/amd64",
           "--file", str(staging_dir / "Dockerfile"),
           str(staging_dir)]

    if is_win:
        # Skip log streaming on Windows to avoid colorama + cp1252 encoding crash.
        cmd.insert(3, "--no-logs")
        print("  (Windows: using --no-logs to avoid encoding issues)")
        env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
        result = subprocess.run(
            cmd, capture_output=True, encoding="utf-8", errors="replace",
            shell=True, env=env,
        )
        if result.stdout:
            sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)
        returncode = result.returncode
    else:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            encoding="utf-8", errors="replace",
        )
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
        returncode = proc.wait()

    if returncode != 0:
        print("\nWarning: az acr build returned non-zero exit code.", file=sys.stderr)
        verify = run_az(["acr", "repository", "show-tags", "--name", acr, "--repository", name, "-o", "tsv"])
        if tag in (verify.stdout or ""):
            print(f"Image {full_image} exists in ACR -- build succeeded despite exit code.")
        else:
            print(f"Image not found in ACR. Build failed.", file=sys.stderr)
            sys.exit(1)

    return full_image


def create_agent(endpoint: str, name: str, image: str, env_vars: dict) -> dict:
    api_version = "2025-05-15-preview"
    url = f"{endpoint}/agents?api-version={api_version}"

    body = {
        "name": name,
        "definition": {
            "kind": "hosted",
            "image": image,
            "cpu": "1",
            "memory": "2Gi",
            "container_protocol_versions": [
                {"protocol": "responses", "version": "v1"}
            ],
            "environment_variables": env_vars,
        },
        "metadata": {"enableVnextExperience": "true"},
    }

    print(f"\nCreating agent '{name}'...")
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
        print(f"Failed to create agent.", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    response = json.loads(result.stdout)
    print(f"Agent created: {response.get('name', name)}")
    return response


def wait_for_ready(endpoint: str, name: str, timeout: int = 60) -> bool:
    api_version = "2025-05-15-preview"
    url = f"{endpoint}/agents/{name}?api-version={api_version}"
    start = time.time()
    print(f"\nWaiting for agent to be ready (timeout: {timeout}s)...")
    while time.time() - start < timeout:
        result = run_az(["rest", "--method", "GET", "--url", url, "--resource", "https://ai.azure.com"])
        if result.returncode == 0:
            data = json.loads(result.stdout)
            latest = data.get("versions", {}).get("latest", {})
            if latest.get("version"):
                print(f"  Agent ready: version {latest['version']}")
                return True
        time.sleep(5)
    print(f"Timeout waiting for agent.", file=sys.stderr)
    return False


def main():
    parser = argparse.ArgumentParser(description="Deploy integration test agent")
    parser.add_argument("--name", required=True, help="Agent name on Foundry")
    parser.add_argument("--acr", required=True, help="ACR name")
    args = parser.parse_args()

    # Load .env from test_agent dir or integration dir
    for env_path in [TEST_AGENT_DIR / ".env", INTEGRATION_DIR / ".env", PACKAGE_ROOT / ".env"]:
        if env_path.exists():
            from dotenv import load_dotenv
            load_dotenv(env_path)
            break

    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("AZURE_AI_PROJECT_ENDPOINT not set.", file=sys.stderr)
        sys.exit(1)

    image_tag = time.strftime("%Y%m%d%H%M")

    staging_dir = Path(tempfile.mkdtemp(prefix="pkg-test-"))
    try:
        print(f"Staging build context...")
        stage_build_context(staging_dir)
        full_image = build_image(staging_dir, args.acr, args.name, image_tag)
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)

    env_vars = {}
    for key in ["AZURE_AI_PROJECT_ENDPOINT", "GITHUB_TOKEN"]:
        val = os.environ.get(key)
        if val:
            env_vars[key] = val
    # Enable SSE keepalive to prevent platform proxy from closing streaming connections
    env_vars["SSE_KEEPALIVE_INTERVAL"] = "5"

    create_agent(endpoint, args.name, full_image, env_vars)
    wait_for_ready(endpoint, args.name)

    print(f"\nDone. Test with:")
    print(f"  python tests/integration/invoke.py --name {args.name} --message \"hello\"")


if __name__ == "__main__":
    main()
