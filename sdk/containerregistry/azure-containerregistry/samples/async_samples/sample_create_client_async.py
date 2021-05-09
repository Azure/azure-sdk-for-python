# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_client_async.py

DESCRIPTION:
    These samples demonstrate creating a ContainerRegistryClient and a ContainerRepository

USAGE:
    python sample_create_client_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTAINERREGISTRY_URL - The URL of you Container Registry account
"""

import asyncio
from dotenv import find_dotenv, load_dotenv
import os


class CreateClients(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]

    async def create_registry_client(self):
        # Instantiate the ContainerRegistryClient
        # [START create_registry_client]
        from azure.containerregistry.aio import ContainerRegistryClient
        from azure.identity.aio import DefaultAzureCredential

        client = ContainerRegistryClient(self.account_url, DefaultAzureCredential())
        # [END create_registry_client]

    async def create_repository_client(self):
        # Instantiate the ContainerRegistryClient
        # [START create_repository_client]
        from azure.containerregistry.aio import ContainerRepository
        from azure.identity.aio import DefaultAzureCredential

        client = ContainerRepository(self.account_url, "my_repository", DefaultAzureCredential())
        # [END create_repository_client]

    async def basic_sample(self):

        from azure.containerregistry.aio import ContainerRegistryClient
        from azure.identity.aio import DefaultAzureCredential

        # Instantiate the client
        client = ContainerRegistryClient(self.account_url, DefaultAzureCredential())
        async with client:
            # Iterate through all the repositories
            async for repository_name in client.list_repository_names():
                if repository_name == "hello-world":
                    # Create a repository client from the registry client
                    repository_client = client.get_repository(repository_name)

                    async with repository_client:
                        # Show all tags
                        async for tag in repository_client.list_tags():
                            print(tag.digest)

                    # [START delete_repository]
                    await client.delete_repository("hello-world")
                    # [END delete_repository]

async def main():
    sample = CreateClients()
    await sample.create_registry_client()
    await sample.create_repository_client()
    await sample.basic_sample()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
