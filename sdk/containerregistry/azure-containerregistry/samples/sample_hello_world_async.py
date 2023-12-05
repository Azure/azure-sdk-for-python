# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_hello_world_async.py

DESCRIPTION:
    This sample demonstrate creating a ContainerRegistryClient and iterating
    through the collection of tags in the repository with anonymous access.

USAGE:
    python sample_hello_world_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of your Container Registry account

    This sample assumes your registry has a repository "library/hello-world", run load_registry() if you don't have.
    Set the environment variables with your own values before running load_registry():
    1) CONTAINERREGISTRY_ENDPOINT - The URL of your Container Registry account
    2) CONTAINERREGISTRY_TENANT_ID - The service principal's tenant ID
    3) CONTAINERREGISTRY_CLIENT_ID - The service principal's client ID
    4) CONTAINERREGISTRY_CLIENT_SECRET - The service principal's client secret
"""
import asyncio
import os
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry.aio import ContainerRegistryClient
from utilities import load_registry, get_authority, get_credential


class HelloWorldAsync(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
        self.authority = get_authority(self.endpoint)
        self.credential = get_credential(self.authority, is_async=True)

    async def basic_sample(self):
        load_registry(self.endpoint)
        # Instantiate an instance of ContainerRegistryClient
        # [START create_registry_client]
        async with ContainerRegistryClient(self.endpoint, self.credential) as client:
            # [END create_registry_client]
            # Iterate through all the repositories
            async for repository_name in client.list_repository_names():
                print(repository_name)
                if repository_name == "library/hello-world":
                    print("Tags of repository library/hello-world:")
                    async for tag in client.list_tag_properties(repository_name):
                        print(tag.name)

                        # Make sure will have the permission to delete the repository later
                        await client.update_manifest_properties(
                            repository_name, tag.name, can_write=True, can_delete=True
                        )

                    print("Deleting " + repository_name)
                    # [START delete_repository]
                    await client.delete_repository(repository_name)
                    # [END delete_repository]


async def main():
    sample = HelloWorldAsync()
    await sample.basic_sample()


if __name__ == "__main__":
    asyncio.run(main())
