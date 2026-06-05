# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates uploading and downloading a skill package using the
    synchronous AIProjectClient.

    1) Delete an existing skill with the same name (if it exists).
    2) Upload a package with `create_from_files(...)`.
    3) Retrieve the uploaded skill with `get(...)`.
    4) Download the package with `download(...)` to the temp folder.
    5) Delete the uploaded skill.

    Skills are a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.skills`.

USAGE:
    python sample_skills_upload_and_download.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.

    This sample uploads `samples/hosted_agents/assets/canvas-design.zip`.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CreateSkillVersionFromFilesBody

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
download_folder = Path(tempfile.gettempdir()).resolve()
skill_name = "canvas-design"
skill_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets/canvas-design.zip"))

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
):

    try:
        project_client.beta.skills.delete(skill_name)
        print(f"Skill `{skill_name}` deleted")
    except ResourceNotFoundError:
        pass

    skill_path = Path(skill_file_path)
    # The ``files`` field accepts any variant of the SDK's ``FileType`` union.
    # All four forms below produce an equivalent multipart request body; pick
    # whichever fits your call site. The 3-tuple form (used here) is the most
    # explicit — it pins both the filename and the content type.
    #
    #   # 1) bare IO[bytes] — filename derived from the file handle's `.name`
    #   files=[skill_path.open("rb")]
    #
    #   # 2) (filename, bytes)
    #   files=[(skill_path.name, skill_path.read_bytes())]
    #
    #   # 3) (filename, IO[bytes])
    #   files=[(skill_path.name, skill_path.open("rb"))]
    #
    #   # 4) (filename, bytes, content_type)
    #   files=[(skill_path.name, skill_path.read_bytes(), "application/zip")]
    imported = project_client.beta.skills.create_from_files(
        skill_name,
        content=CreateSkillVersionFromFilesBody(files=[(skill_path.name, skill_path.read_bytes(), "application/zip")]),
    )
    imported_skill_name = imported.name
    print(f"Imported skill from package: {imported.name} ({imported.skill_id}) version={imported.version}")

    fetched = project_client.beta.skills.get(imported.name)
    print(f"Fetched imported skill: {fetched.name} ({fetched.id}) default_version={fetched.default_version}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_path = download_folder / f"{fetched.name}_{timestamp}.zip"
    download_path.write_bytes(b"".join(project_client.beta.skills.download(fetched.name)))
    print(f"Downloaded skill package path: {download_path}")

    deleted = project_client.beta.skills.delete(fetched.name)
    print(f"Deleted imported skill: {deleted}")
