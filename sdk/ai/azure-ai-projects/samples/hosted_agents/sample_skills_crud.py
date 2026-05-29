# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on Skills
    using the synchronous AIProjectClient.

    It creates two skill versions with different inline content (different
    `description` values), switches the default version, and prints the
    description from the fetched default version to show that the default
    version pointer changes which content is returned.

    Skills are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.skills`.

USAGE:
    python sample_skills_crud.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
"""

import os

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import SkillInlineContent, SkillVersion

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]


def print_skill_version_description(version: SkillVersion) -> None:
    print(f"  - version `{version.version}` description: {version.description!r}")


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
):

    skill_name = "product-support-skill"

    try:
        project_client.beta.skills.delete(skill_name)
        print(f"Skill `{skill_name}` deleted")
    except ResourceNotFoundError:
        pass

    inline_content_v1 = SkillInlineContent(
        description="Product support skill, revision 1 (concise replies).",
        instructions="You are revision 1. Answer product support questions concisely.",
        metadata={"revision": "1"},
    )

    inline_content_v2 = SkillInlineContent(
        description="Product support skill, revision 2 (detailed replies with citations).",
        instructions="You are revision 2. Answer product support questions in detail and cite sources.",
        metadata={"revision": "2"},
    )

    created = project_client.beta.skills.create(
        name=skill_name,
        inline_content=inline_content_v1,
    )
    print(f"Created skill: {created.name} revision 1 in version {created.version}")

    created = project_client.beta.skills.create(
        name=skill_name,
        inline_content=inline_content_v2,
    )
    print(f"Created skill: {created.name} revision 2 in version {created.version}")

    updated = project_client.beta.skills.update(
        skill_name,
        default_version="2",
    )
    print(f"Updated skill: {updated.name} default version is now {updated.default_version}")

    fetched = project_client.beta.skills.get(name=skill_name)
    print(f"Retrieved skill with default version: {fetched.default_version}")
    fetched_version = project_client.beta.skills.get_version(
        name=skill_name,
        version=fetched.default_version,
    )
    print_skill_version_description(fetched_version)

    updated = project_client.beta.skills.update(
        skill_name,
        default_version="1",
    )
    print(f"Updated skill: {updated.name} default version is now {updated.default_version}")

    fetched = project_client.beta.skills.get(name=skill_name)
    print(f"Retrieved skill with default version: {fetched.default_version}")
    fetched_version = project_client.beta.skills.get_version(
        name=skill_name,
        version=fetched.default_version,
    )
    print_skill_version_description(fetched_version)

    skills = list(project_client.beta.skills.list())
    print(f"Found {len(skills)} skills")
    for item in skills:
        print(f"  - {item.name} ({item.id})")

    project_client.beta.skills.delete(name=skill_name)
    print("Skill deleted")
