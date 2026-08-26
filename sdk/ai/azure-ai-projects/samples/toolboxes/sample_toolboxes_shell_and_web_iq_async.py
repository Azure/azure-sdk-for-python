# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a Toolbox containing a shell tool
    backed by an automatically provisioned container and a WebIQ preview tool
    using the asynchronous AIProjectClient.

USAGE:
    python sample_toolboxes_shell_and_web_iq_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.6.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) WEB_IQ_PROJECT_CONNECTION_ID - The fully-qualified resource ID of the WebIQ project connection.
"""

import asyncio
import os

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    ShellToolboxTool,
    ToolboxShellContainerAutoEnvironment,
    ToolboxShellNetworkPolicyDisabled,
    WebIQPreviewToolboxTool,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
toolbox_name = "toolbox_with_shell_and_web_iq"


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        created = None
        try:
            try:
                await project_client.toolboxes.delete(name=toolbox_name)
            except ResourceNotFoundError:
                pass

            created = await project_client.toolboxes.create_version(
                name=toolbox_name,
                description="Toolbox with shell and WebIQ tools.",
                tools=[
                    ShellToolboxTool(
                        name="shell",
                        description="Run shell commands in an automatically provisioned container.",
                        environment=ToolboxShellContainerAutoEnvironment(
                            memory_limit="4g",
                            network_policy=ToolboxShellNetworkPolicyDisabled(),
                        ),
                    ),
                    WebIQPreviewToolboxTool(
                        name="web_iq",
                        description="Use WebIQ through a project connection.",
                        project_connection_id=os.environ["WEB_IQ_PROJECT_CONNECTION_ID"],
                        server_label="web-iq",
                        require_approval="always",
                    ),
                ],
            )
            print(f"Created toolbox `{created.name}` version {created.version}")

            fetched = await project_client.toolboxes.get_version(name=toolbox_name, version=created.version)
            for tool in fetched.tools or []:
                print(f"Tool `{tool.name}` has type `{tool.type}`")
        finally:
            if created is not None:
                await project_client.toolboxes.delete(name=toolbox_name)
                print("Toolbox deleted")


if __name__ == "__main__":
    asyncio.run(main())
