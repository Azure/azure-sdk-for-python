# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_delete_tags_async.py

DESCRIPTION:
    This sample demonstrates deleting all but the most recent three tags for each repository.

USAGE:
    python sample_delete_tags_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of your Container Registry account

    This sample assumes your registry has at least one repository with more than three tags,
    run load_registry() if you don't have.
    Set the environment variables with your own values before running load_registry():
    1) CONTAINERREGISTRY_ENDPOINT - The URL of your Container Registry account
    2) CONTAINERREGISTRY_TENANT_ID - The service principal's tenant ID
    3) CONTAINERREGISTRY_CLIENT_ID - The service principal's client ID
    4) CONTAINERREGISTRY_CLIENT_SECRET - The service principal's client secret
    5) CONTAINERREGISTRY_RESOURCE_GROUP - The resource group name
    6) CONTAINERREGISTRY_REGISTRY_NAME - The registry name
"""
import asyncio
import os
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry import ArtifactTagOrder
from azure.containerregistry.aio import ContainerRegistryClient
from utilities import load_registry, get_authority, get_credential


class DeleteTagsAsync(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ.get("CONTAINERREGISTRY_ENDPOINT")
        self.authority = get_authority(self.endpoint)
        self.credential = get_credential(self.authority, is_async=True)

    async def delete_tags(self):
        load_registry()
        # [START list_repository_names]
        async with ContainerRegistryClient(self.endpoint, self.credential) as client:
            # Iterate through all the repositories
            async for repository_name in client.list_repository_names():
                print(repository_name)
                # [END list_repository_names]

                # Keep the three most recent tags, delete everything else
                tag_count = 0
                async for tag in client.list_tag_properties(
                    repository_name, order_by=ArtifactTagOrder.LAST_UPDATED_ON_DESCENDING
                ):
                    tag_count += 1
                    if tag_count > 3:                        
                        print(f"Deleting {repository_name}:{tag.name}")
                        await client.delete_tag(repository_name, tag.name)


async def main():
    sample = DeleteTagsAsync()
    await sample.delete_tags()


if __name__ == "__main__":
    asyncio.run(main())
