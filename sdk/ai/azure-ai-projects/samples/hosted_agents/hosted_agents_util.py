import asyncio
import logging
from typing import Optional

from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.models import (
    AgentVersionDetails,
)


async def wait_for_agent_version_active_async(
    project_client: AsyncAIProjectClient,
    agent_name: str,
    agent_version: str,
    *,
    logger: Optional[logging.Logger] = None,
    max_attempts: int = 60,
    poll_interval_seconds: int = 10,
) -> None:
    if logger:
        logger.info("Waiting for agent version to become active...")

    for attempt in range(max_attempts):
        await asyncio.sleep(poll_interval_seconds)
        version_details = await project_client.agents.get_version(agent_name=agent_name, agent_version=agent_version)
        status = version_details["status"]

        if logger:
            logger.debug(f"Agent version status: {status} (attempt {attempt + 1}/{max_attempts})")
        print(f"Agent version status: {status} (attempt {attempt + 1})")

        if status == "active":
            if logger:
                logger.info("Agent version is now active")
            return

        if status == "failed":
            if logger:
                logger.error(f"Agent version provisioning failed: {dict(version_details)}")
            raise RuntimeError(f"Agent version provisioning failed: {dict(version_details)}")

    if logger:
        logger.error("Timed out waiting for agent version to become active")
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
