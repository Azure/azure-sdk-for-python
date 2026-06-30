import asyncio
import sys
import time
from pathlib import Path
from typing import IO, Tuple

_SAMPLES_DIR = Path(__file__).resolve().parents[1]
if str(_SAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(_SAMPLES_DIR))

from util import zip as zip_directory

from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.models import (
    AgentVersionDetails,
    CodeDependencyResolution,
)

_ASSETS_DIR = Path(__file__).parent / "assets"


def select_echo_agent_code_zip(use_remote_build: bool) -> Tuple[CodeDependencyResolution, IO[bytes]]:
    """Pick the dependency-resolution mode and matching echo-agent zip as ``IO[bytes]``."""
    dependency_resolution = (
        CodeDependencyResolution.REMOTE_BUILD if use_remote_build else CodeDependencyResolution.BUNDLED
    )

    if use_remote_build:
        zip_filename = "echo-agent.zip"
        _, _, zip_path = zip_directory(_ASSETS_DIR / "echo-agent", zip_filename)
    else:
        zip_path = _ASSETS_DIR / "echo-agent-prebuilt.zip"

    return dependency_resolution, zip_path.open("rb")


def wait_for_agent_version_active(
    project_client: AIProjectClient,
    agent_name: str,
    agent_version: str,
    *,
    max_attempts: int = 60,
    poll_interval_seconds: int = 10,
) -> None:
    """Poll until the version becomes ``active``; raise on ``failed`` or timeout."""
    print("Waiting for agent version to become active...")

    for attempt in range(max_attempts):
        time.sleep(poll_interval_seconds)
        version_details = project_client.agents.get_version(agent_name=agent_name, agent_version=agent_version)
        status = version_details["status"]

        print(f"Agent version status: {status} (attempt {attempt + 1}/{max_attempts})")

        if status == "active":
            print("Agent version is now active")
            return

        if status == "failed":
            raise RuntimeError(f"Agent version provisioning failed: {dict(version_details)}")

    raise RuntimeError("Timed out waiting for agent version to become active")


async def wait_for_agent_version_active_async(
    project_client: AsyncAIProjectClient,
    agent_name: str,
    agent_version: str,
    *,
    max_attempts: int = 60,
    poll_interval_seconds: int = 10,
) -> None:
    """Async variant of :func:`wait_for_agent_version_active`."""
    print("Waiting for agent version to become active...")

    for attempt in range(max_attempts):
        await asyncio.sleep(poll_interval_seconds)
        version_details = await project_client.agents.get_version(agent_name=agent_name, agent_version=agent_version)
        status = version_details["status"]

        print(f"Agent version status: {status} (attempt {attempt + 1}/{max_attempts})")

        if status == "active":
            print("Agent version is now active")
            return

        if status == "failed":
            raise RuntimeError(f"Agent version provisioning failed: {dict(version_details)}")

    raise RuntimeError("Timed out waiting for agent version to become active")


def get_latest_active_agent_version(
    project_client: AIProjectClient,
    agent_name: str,
) -> AgentVersionDetails:
    for version in project_client.agents.list_versions(agent_name=agent_name, order="desc"):
        if version.status == "active":
            return version

    raise RuntimeError(
        f"No active version found for hosted agent '{agent_name}'. "
        "Create or activate a version before running this sample."
    )


async def get_latest_active_agent_version_async(
    project_client: AsyncAIProjectClient,
    agent_name: str,
) -> AgentVersionDetails:
    async for version in project_client.agents.list_versions(agent_name=agent_name, order="desc"):
        if version.status == "active":
            return version

    raise RuntimeError(
        f"No active version found for hosted agent '{agent_name}'. "
        "Create or activate a version before running this sample."
    )
