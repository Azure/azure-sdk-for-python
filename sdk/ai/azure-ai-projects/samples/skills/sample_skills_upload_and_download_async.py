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
    2) Upload a package with `create_from_files(...)`.
    3) Retrieve the uploaded skill with `get(...)`.
    4) Download the package with `download(...)` to the temp folder.
    5) Delete the uploaded skill.

    Skills are a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.skills`.

USAGE:
    python sample_skills_upload_and_download_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.

    This sample builds and uploads `samples/skills/assets/team-status-update/`.
"""

import asyncio
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

_SAMPLES_DIR = Path(__file__).resolve().parents[1]
if str(_SAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(_SAMPLES_DIR))

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import CreateSkillVersionFromFilesBody

from util import zip

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
download_folder = Path(tempfile.gettempdir()).resolve()
skill_name = "team-status-update"
skill_zip_filename = "team-status-update.zip"
skill_source_dir = Path(__file__).parent / "assets/team-status-update"


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        try:
            await project_client.beta.skills.delete(skill_name)
            print(f"Skill `{skill_name}` deleted")
        except ResourceNotFoundError:
            pass

        skill_zip_bytes, _, skill_zip_path = zip(skill_source_dir, skill_zip_filename)
        uploaded_skill_zip_filename = skill_zip_path.name
        # The ``files`` field accepts any variant of the SDK's ``FileType`` union.
        # The 2-tuple form used here pins the filename while letting the transport
        # choose the multipart part headers.
        #
        #   # 1) bare IO[bytes] - filename derived from the file handle's `.name`
        #   files=[skill_zip_path.open("rb")]
        #
        #   # 2) (filename, bytes)
        #   files=[(skill_zip_filename, skill_zip_bytes)]
        #
        #   # 3) (filename, IO[bytes])
        #   files=[(skill_zip_filename, skill_zip_path.open("rb"))]
        #
        #   # 4) (filename, bytes, content_type)
        #   files=[(skill_zip_filename, skill_zip_bytes, "application/zip")]
        #
        imported = await project_client.beta.skills.create_from_files(
            skill_name,
            content=CreateSkillVersionFromFilesBody(files=[(uploaded_skill_zip_filename, skill_zip_bytes)]),
        )
        imported_skill_name = imported.name
        print(f"Imported skill from package: {imported.name} ({imported.skill_id}) version={imported.version}")

        fetched = await project_client.beta.skills.get(imported.name)
        print(f"Fetched imported skill: {fetched.name} ({fetched.id}) default_version={fetched.default_version}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_path = download_folder / f"{fetched.name}_{timestamp}.zip"
        download_stream = await project_client.beta.skills.download(fetched.name)
        download_path.write_bytes(b"".join([chunk async for chunk in download_stream]))
        print(f"Downloaded skill package path: {download_path}")

        deleted = await project_client.beta.skills.delete(fetched.name)
        print(f"Deleted imported skill: {deleted}")


if __name__ == "__main__":
    asyncio.run(main())
