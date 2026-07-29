# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to stream hosted agent session logs
    using `project_client.agents.get_session_log_stream` with the
    synchronous AIProjectClient.

    Sessions only work with Hosted Agents.

USAGE:
    python sample_session_log_stream.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.
    3) FOUNDRY_HOSTED_AGENT_NAME - Optional. The Hosted Agent name. Defaults to
        `MyHostedAgent`.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    CodeDependencyResolution,
    HostedAgentDefinition,
    ProtocolVersionRecord,
    VersionRefIndicator,
)
from hosted_agents_util import create_version_from_code
from util import zip_directory

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME", "MyHostedAgent")
model_name = os.environ["FOUNDRY_MODEL_NAME"]
hosted_agent_source_dir = Path(__file__).parent / "assets" / "basic-agent"

zip_path = zip_directory(hosted_agent_source_dir, "basic-agent.zip")[2]


def _iter_sse_frames(stream, max_log_events: int):
    event_count = 0
    buffer = ""

    for chunk in stream:
        buffer += chunk.decode("utf-8", errors="replace")

        while "\n\n" in buffer:
            frame, buffer = buffer.split("\n\n", 1)
            event_name = None
            data_lines = []

            for line in frame.splitlines():
                if line.startswith("event: "):
                    event_name = line[7:]
                elif line.startswith("data: "):
                    data_lines.append(line[6:])

            if data_lines or event_name:
                event_count += 1
                yield {
                    "event": event_name,
                    "data": "\n".join(data_lines),
                }

                if event_count >= max_log_events:
                    return


with (
    zip_path.open("rb") as code_stream,
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
    ) as project_client,
    create_version_from_code(
        project_client=project_client,
        agent_name=agent_name,
        description="Session log stream hosted agent uploaded from assets/basic-agent.",
        definition=HostedAgentDefinition(
            cpu="0.5",
            memory="1Gi",
            code_configuration=CodeConfiguration(
                runtime="python_3_14",
                entry_point=["python", "main.py"],
                dependency_resolution=CodeDependencyResolution.REMOTE_BUILD,
            ),
            environment_variables={
                "FOUNDRY_PROJECT_ENDPOINT": endpoint,
                "FOUNDRY_MODEL_NAME": model_name,
            },
            protocol_versions=[ProtocolVersionRecord(protocol="responses", version="2.0.0")],
        ),
        code=code_stream,
    ) as created,
    project_client.get_openai_client(agent_name=agent_name) as openai_client,
):
    session = project_client.agents.create_session(
        agent_name=agent_name,
        version_indicator=VersionRefIndicator(agent_version=created.version),
    )
    print(f"Session created (id: {session.agent_session_id}, status: {session.status})")
    try:
        input_text = "Say hello in one short sentence."

        response = openai_client.responses.create(
            input=input_text,
            extra_body={
                "agent_session_id": session.agent_session_id,
            },
        )
        print(f"Response output: {response.output_text}")

        print("Streaming session logs...")
        raw_stream = project_client.agents.get_session_log_stream(
            agent_name=agent_name,
            agent_version=created.version,
            session_id=session.agent_session_id,
        )
        for frame in _iter_sse_frames(raw_stream, max_log_events=30):
            print(f"SSE event: {frame.get('event')}")
            print(f"SSE data: {frame.get('data')}\n")
    finally:
        project_client.agents.delete_session(
            agent_name=agent_name,
            session_id=session.agent_session_id,
        )
        print(f"Session deleted (id: {session.agent_session_id})")
