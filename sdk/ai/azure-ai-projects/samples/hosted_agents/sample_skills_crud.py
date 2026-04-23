# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on Skills
    using the synchronous AIProjectClient.

    Skills are a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.skills`.

USAGE:
    python sample_skills_crud.py

    Before running the sample:

    pip install "azure-ai-projects>=2.1.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
"""

import os

from dotenv import load_dotenv

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
):
    skills_client = project_client.beta.skills

    skill_name = "product_support_skill"

    try:
        skills_client.delete(skill_name)
        print(f"Skill `{skill_name}` deleted")
    except ResourceNotFoundError:
        pass

    created = skills_client.create(
        name=skill_name,
        description="Example skill created by the azure-ai-projects sample.",
        instructions="You help answer product support questions using company policy and product guidance.",
        metadata={"status": "created", "domain": "support"},
    )
    print(
        f"Created skill: {created.name} ({created.skill_id}) "
        f"has_blob={created.has_blob} metadata={created.metadata}"
    )

    fetched = skills_client.get(skill_name)
    print(f"Retrieved skill: {fetched.name} ({fetched.skill_id}) " f"description={fetched.description!r}")

    updated = skills_client.update(
        skill_name,
        description="Updated description for the sample skill.",
        metadata={"status": "updated", "domain": "support"},
    )
    print(
        f"Updated skill: {updated.name} ({updated.skill_id}) "
        f"has_blob={updated.has_blob} metadata={updated.metadata}"
    )

    skills = list(skills_client.list())
    print(f"Found {len(skills)} skills or more")

    deleted = skills_client.delete(skill_name)
    print(f"Deleted skill: {deleted}")
