# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on Skills
    using the asynchronous AIProjectClient.

    Skills are a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.skills`.

USAGE:
    python sample_skills_crud_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.1.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
"""

import os

from dotenv import load_dotenv

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential

from azure.ai.projects.aio import AIProjectClient

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        skills_client = project_client.beta.skills

        skill_name = "product_support_skill"

        try:
            await skills_client.delete(skill_name)
            print(f"Skill `{skill_name}` deleted")
        except ResourceNotFoundError:
            pass

        created = None
        created = await skills_client.create(
            name=skill_name,
            description="Example skill created by the azure-ai-projects sample.",
            instructions="You help answer product support questions using company policy and product guidance.",
            metadata={"status": "created", "domain": "support"},
        )
        print(
            f"Created skill: {created.name} ({created.skill_id}) "
            f"has_blob={created.has_blob} metadata={created.metadata}"
        )

        fetched = await skills_client.get(skill_name)
        print(f"Retrieved skill: {fetched.name} ({fetched.skill_id}) " f"description={fetched.description!r}")

        updated = await skills_client.update(
            skill_name,
            description="Updated description for the sample skill.",
            instructions="You help answer product support questions and escalate billing issues.",
            metadata={"status": "updated", "domain": "support"},
        )
        print(
            f"Updated skill: {updated.name} ({updated.skill_id}) "
            f"has_blob={updated.has_blob} metadata={updated.metadata}"
        )

        skills = []
        async for skill in skills_client.list():
            skills.append(skill)
        print(f"Found {len(skills)} skills or more")

        deleted = await skills_client.delete(skill_name)
        print(f"Deleted skill: {deleted}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
