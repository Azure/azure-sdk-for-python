# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on Skills
    (including version-scoped operations) using the asynchronous AIProjectClient.

    Every call to `skills.create(name, ...)` (or `create_from_files(...)`)
    appends a new version to the skill. This sample:

    1) Deletes the skill (and all versions) if it already exists.
    2) Creates three inline versions with `skills.create(...)`; the third one
       is promoted to default with `default=True`.
    3) Retrieves the skill with `skills.get(...)` and lists all skills.
    4) Lists all versions with `skills.list_versions(...)` and retrieves a
       specific one with `skills.get_version(name, version)`.
    5) Switches the default version with `skills.update(name, default_version=...)`
       and shows the impact by re-resolving the default's content before/after.
    6) Deletes a specific version with `skills.delete_version(name, version)`.
    7) Deletes the whole skill to clean up.

    Skills are a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.skills`.

USAGE:
    python sample_skills_crud_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
"""

import asyncio
import os

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import SkillInlineContent

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
skill_name = "product-support-skill"


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        skills_client = project_client.beta.skills

        try:
            await skills_client.delete(skill_name)
            print(f"Skill `{skill_name}` deleted")
        except ResourceNotFoundError:
            pass

        created_versions = []
        for index in range(1, 4):
            is_last = index == 3
            version = await skills_client.create(
                name=skill_name,
                inline_content=SkillInlineContent(
                    description=f"Example skill version {index} created by the azure-ai-projects sample.",
                    instructions=(
                        f"You are revision {index}. Help answer product support questions "
                        "using company policy and product guidance."
                    ),
                    metadata={"revision": str(index)},
                ),
                # Promote the final version to the skill's default version.
                default=is_last,
            )
            created_versions.append(version)
            print(f"Created version: {version.version} (skill_id={version.skill_id})")

        fetched = await skills_client.get(skill_name)
        print(f"Retrieved skill: {fetched.name} ({fetched.id}) description={fetched.description!r}")

        skills = []
        async for skill in skills_client.list():
            skills.append(skill)
        print(f"Found {len(skills)} skills or more")

        versions = []
        async for v in skills_client.list_versions(skill_name):
            versions.append(v)
        print(f"Found {len(versions)} version(s) for `{skill_name}`:")
        for v in versions:
            print(f"  - version={v.version} created_at={v.created_at}")

        target_version = created_versions[-1].version
        fetched_version = await skills_client.get_version(skill_name, target_version)
        print(f"Retrieved version: {fetched_version.version} description={fetched_version.description!r}")

        skill_before = await skills_client.get(skill_name)
        default_before = await skills_client.get_version(skill_name, skill_before.default_version)
        print(
            f"Before update -> default_version={skill_before.default_version} "
            f"description={default_before.description!r}"
        )

        second_version = created_versions[1].version
        updated_skill = await skills_client.update(skill_name, default_version=second_version)
        print(f"Updated skill default to version `{second_version}`: default_version={updated_skill.default_version}")

        skill_after = await skills_client.get(skill_name)
        default_after = await skills_client.get_version(skill_name, skill_after.default_version)
        print(
            f"After update  -> default_version={skill_after.default_version} "
            f"description={default_after.description!r}"
        )

        first_version = created_versions[0].version
        deleted_version = await skills_client.delete_version(skill_name, first_version)
        print(f"Deleted version `{first_version}`: {deleted_version}")

        deleted = await skills_client.delete(skill_name)
        print(f"Deleted skill: {deleted}")


if __name__ == "__main__":
    asyncio.run(main())
