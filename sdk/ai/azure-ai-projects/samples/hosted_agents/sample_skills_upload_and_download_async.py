# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates uploading and downloading a skill package using the
    asynchronous AIProjectClient.

    1) Delete an existing skill with the same name (if it exists).
    2) Upload a package with `create_from_package(...)`.
    3) Retrieve the uploaded skill with `get(...)`.
    4) Download the package with `download(...)` to the temp folder.
    5) Delete the uploaded skill.

    Skills are a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.skills`.

USAGE:
    python sample_skills_upload_and_download_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.1.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.

    This sample uploads `samples/hosted_agents/assets/canvas-design.zip`.
"""

import asyncio
import os
import tempfile
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential

from azure.ai.projects.aio import AIProjectClient

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
download_folder = Path(tempfile.gettempdir()).resolve()
skill_name = "canvas-design"
skill_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets/canvas-design.zip"))


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):

        try:
            await project_client.beta.skills.delete(skill_name)
            print(f"Skill `{skill_name}` deleted")
        except ResourceNotFoundError:
            pass

        imported = await project_client.beta.skills.create_from_package(Path(skill_file_path).read_bytes())
        imported_skill_name = imported.name
        print(f"Imported skill from package: {imported.name} ({imported.skill_id}) has_blob={imported.has_blob}")

        fetched = await project_client.beta.skills.get(imported.name)
        print(f"Fetched imported skill: {fetched.name} ({fetched.skill_id}) has_blob={fetched.has_blob}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_path = download_folder / f"{fetched.name}_{timestamp}.zip"
        download_stream = await project_client.beta.skills.download(fetched.name)
        download_path.write_bytes(b"".join([chunk async for chunk in download_stream]))
        print(f"Downloaded skill package path: {download_path}")

        deleted = await project_client.beta.skills.delete(fetched.name)
        print(f"Deleted imported skill: {deleted}")


if __name__ == "__main__":
    asyncio.run(main())
