import asyncio
import sys
import time
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import IO, Any, AsyncIterator, Iterator, Tuple

_SAMPLES_DIR = Path(__file__).resolve().parents[1]
if str(_SAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(_SAMPLES_DIR))

from util import zip_directory

from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.models import (
    AgentEndpointConfig,
    AgentVersionDetails,
    CodeDependencyResolution,
    FixedRatioVersionSelectionRule,
    ProtocolConfiguration,
    ResponsesProtocolConfiguration,
    VersionSelector,
)

_ASSETS_DIR = Path(__file__).parent / "assets"


def select_basic_agent_code_zip(use_remote_build: bool) -> Tuple[CodeDependencyResolution, IO[bytes]]:
    """Pick the dependency-resolution mode and matching basic-agent zip as ``IO[bytes]``."""
    dependency_resolution = (
        CodeDependencyResolution.REMOTE_BUILD if use_remote_build else CodeDependencyResolution.BUNDLED
    )

    if use_remote_build:
        zip_filename = "basic-agent.zip"
        _, _, zip_path = zip_directory(_ASSETS_DIR / "basic-agent", zip_filename)
    else:
        zip_path = _ASSETS_DIR / "basic-agent-prebuilt.zip"

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


@contextmanager
def create_version_from_code(
    project_client: AIProjectClient,
    agent_name: str,
    code: IO[bytes],
    *,
    max_attempts: int = 60,
    poll_interval_seconds: int = 10,
    **kwargs: Any,
) -> Iterator[AgentVersionDetails]:
    """Create a version from code, point the agent endpoint to it, then restore and delete on exit."""
    created_version = None
    original_agent_endpoint = None

    try:
        created_version = project_client.agents.create_version_from_code(
            agent_name=agent_name,
            code=code,
            **kwargs,
        )
        print(
            f"Hosted agent version created (id: {created_version.id}, name: {created_version.name}, "
            f"version: {created_version.version})"
        )

        wait_for_agent_version_active(
            project_client,
            agent_name,
            created_version.version,
            max_attempts=max_attempts,
            poll_interval_seconds=poll_interval_seconds,
        )

        original_agent_endpoint = project_client.agents.get(agent_name=agent_name).agent_endpoint
        endpoint_config = AgentEndpointConfig(
            version_selector=VersionSelector(
                version_selection_rules=[
                    FixedRatioVersionSelectionRule(agent_version=created_version.version, traffic_percentage=100),
                ]
            ),
            protocol_configuration=ProtocolConfiguration(responses=ResponsesProtocolConfiguration()),
        )
        project_client.agents.update_details(agent_name=agent_name, agent_endpoint=endpoint_config)
        print(f"Agent endpoint configured for version {created_version.version}")

        yield created_version
    finally:
        if original_agent_endpoint is not None:
            project_client.agents.update_details(agent_name=agent_name, agent_endpoint=original_agent_endpoint)
            print("Agent endpoint restored")

        if created_version is not None:
            project_client.agents.delete_version(
                agent_name=agent_name, agent_version=created_version.version, force=True
            )
            print(f"Hosted agent version {created_version.version} deleted")


@asynccontextmanager
async def create_version_from_code_async(
    project_client: AsyncAIProjectClient,
    agent_name: str,
    code: IO[bytes],
    *,
    max_attempts: int = 60,
    poll_interval_seconds: int = 10,
    **kwargs: Any,
) -> AsyncIterator[AgentVersionDetails]:
    """Async variant of :func:`create_version_from_code`."""
    created_version = None
    original_agent_endpoint = None

    try:
        created_version = await project_client.agents.create_version_from_code(
            agent_name=agent_name,
            code=code,
            **kwargs,
        )
        print(
            f"Hosted agent version created (id: {created_version.id}, name: {created_version.name}, "
            f"version: {created_version.version})"
        )

        await wait_for_agent_version_active_async(
            project_client,
            agent_name,
            created_version.version,
            max_attempts=max_attempts,
            poll_interval_seconds=poll_interval_seconds,
        )

        original_agent_endpoint = (await project_client.agents.get(agent_name=agent_name)).agent_endpoint
        endpoint_config = AgentEndpointConfig(
            version_selector=VersionSelector(
                version_selection_rules=[
                    FixedRatioVersionSelectionRule(agent_version=created_version.version, traffic_percentage=100),
                ]
            ),
            protocol_configuration=ProtocolConfiguration(responses=ResponsesProtocolConfiguration()),
        )
        await project_client.agents.update_details(agent_name=agent_name, agent_endpoint=endpoint_config)
        print(f"Agent endpoint configured for version {created_version.version}")

        yield created_version
    finally:
        if original_agent_endpoint is not None:
            await project_client.agents.update_details(agent_name=agent_name, agent_endpoint=original_agent_endpoint)
            print("Agent endpoint restored")

        if created_version is not None:
            await project_client.agents.delete_version(
                agent_name=agent_name, agent_version=created_version.version, force=True
            )
            print(f"Hosted agent version {created_version.version} deleted")


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
