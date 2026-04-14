# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create and update a code-based (Hosted) agent using
    the asynchronous AIProjectClient.

    The sample:
    1. Builds a minimal Python agent zip in memory.
    2. Computes its SHA-256 and calls `create_agent_from_code` to create the agent.
    3. Retrieves the agent with `get`.
    4. Builds a second version of the code zip and calls `update_agent_from_code`.
    5. Deletes the agent.

USAGE:
    python sample_agent_code_based_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
"""

import asyncio
import hashlib
import io
import os
import zipfile

from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    CreateAgentFromCodeContent,
    CreateAgentVersionFromCodeContent,
    CreateAgentVersionFromCodeRequest,
    HostedAgentDefinition,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

# ---------------------------------------------------------------------------
# Helper: create an in-memory zip that contains a minimal Python agent entry
# ---------------------------------------------------------------------------

_AGENT_CODE_V1 = """\
# Minimal hosted agent – version 1
def handle(request):
    return {"response": "Hello from code-based agent v1!"}
"""

_AGENT_CODE_V2 = """\
# Minimal hosted agent – version 2
def handle(request):
    return {"response": "Hello from code-based agent v2!"}
"""


def _make_zip(source_code: str) -> bytes:
    """Package *source_code* as ``main.py`` inside an in-memory zip."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("main.py", source_code)
    return buf.getvalue()


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Main sample
# ---------------------------------------------------------------------------

agent_name = "my-code-based-agent"


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        # [START create_agent_from_code]
        code_zip_v1 = _make_zip(_AGENT_CODE_V1)
        sha256_v1 = _sha256_hex(code_zip_v1)

        agent = await project_client.agents.create_agent_from_code(
            body=CreateAgentFromCodeContent(
                metadata=CreateAgentVersionFromCodeRequest(
                    description="A simple code-based hosted agent (v1).",
                    definition=HostedAgentDefinition(
                        cpu="1.0",
                        memory="1Gi",
                        code_configuration=CodeConfiguration(
                            runtime="python_3_11",
                            entry_point=["python", "main.py"],
                        ),
                    ),
                ),
                code=("agent_v1.zip", code_zip_v1, "application/zip"),
            ),
            agent_name=agent_name,
            code_zip_sha256=sha256_v1,
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name})")
        # [END create_agent_from_code]

        # [START get_agent]
        fetched = await project_client.agents.get(agent_name)
        print(f"Agent retrieved (id: {fetched.id}, name: {fetched.name})")
        # [END get_agent]

        # [START update_agent_from_code]
        code_zip_v2 = _make_zip(_AGENT_CODE_V2)
        sha256_v2 = _sha256_hex(code_zip_v2)

        updated_agent = await project_client.agents.update_agent_from_code(
            agent_name=agent_name,
            body=CreateAgentVersionFromCodeContent(
                metadata=CreateAgentVersionFromCodeRequest(
                    description="A simple code-based hosted agent (v2).",
                    definition=HostedAgentDefinition(
                        cpu="1.0",
                        memory="1Gi",
                        code_configuration=CodeConfiguration(
                            runtime="python_3_11",
                            entry_point=["python", "main.py"],
                        ),
                    ),
                ),
                code=("agent_v2.zip", code_zip_v2, "application/zip"),
            ),
            code_zip_sha256=sha256_v2,
        )
        print(f"Agent updated (id: {updated_agent.id}, name: {updated_agent.name})")
        # [END update_agent_from_code]

        # [START delete_agent]
        result = await project_client.agents.delete(agent_name)
        print(f"Agent deleted: {result}")
        # [END delete_agent]


if __name__ == "__main__":
    asyncio.run(main())
