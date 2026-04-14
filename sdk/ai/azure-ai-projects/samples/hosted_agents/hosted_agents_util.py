import logging
import time
from contextlib import contextmanager
from typing import Optional, Any

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import HostedAgentDefinition, ProtocolVersionRecord, VersionRefIndicator


def wait_for_agent_version_active(
    project_client: AIProjectClient,
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
        time.sleep(poll_interval_seconds)
        version_details = project_client.agents.get_version(agent_name=agent_name, agent_version=agent_version)
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


@contextmanager
def create_agent_and_session(
    project_client: AIProjectClient,
    agent_name: str,
    image: str,
    isolation_key: str = "sample-isolation-key",
):
    agent = project_client.agents.create_version(
        agent_name=agent_name,
        definition=HostedAgentDefinition(
            cpu="0.5",
            memory="1Gi",
            image=image,
            container_protocol_versions=[
                ProtocolVersionRecord(protocol="responses", version="1.0.0"),
            ],
        ),
        metadata={"enableVnextExperience": "true"},
    )
    print(f"Agent created (name: {agent.name}, version: {agent.version})")

    wait_for_agent_version_active(
        project_client=project_client,
        agent_name=agent_name,
        agent_version=agent.version,
    )

    session = project_client.beta.agents.create_session(
        agent_name=agent_name,
        isolation_key=isolation_key,
        version_indicator=VersionRefIndicator(agent_version=agent.version),
    )
    print(f"Session created (id: {session.agent_session_id}, status: {session.status})")

    try:
        yield agent, session
    finally:
        project_client.beta.agents.delete_session(
            agent_name=agent_name,
            session_id=session.agent_session_id,
            isolation_key=isolation_key,
        )
        print(f"Session with id: {session.agent_session_id} deleted.")

        project_client.agents.delete_version(agent_name=agent_name, agent_version=agent.version)
        print(f"Agent version {agent.version} deleted.")
