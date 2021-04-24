# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_client_async.py

DESCRIPTION:
    These samples demonstrate creating a ContainerRegistryClient and a ContainerRepositoryClient

USAGE:
    python sample_create_client_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTAINERREGISTRY_URL - The URL of you Container Registry account
"""

from dotenv import find_dotenv, load_dotenv
import os


class CreateClients(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]

    def create_registry_client(self):
        # Instantiate the ContainerRegistryClient
        # [START create_registry_client]
        from azure.containerregistry.aio import ContainerRegistryClient
        from azure.identity.aio import DefaultAzureCredential

        client = ContainerRegistryClient(self.account_url, DefaultAzureCredential())
        # [END create_registry_client]

    def create_repository_client(self):
        # Instantiate the ContainerRegistryClient
        # [START create_repository_client]
        from azure.containerregistry.aio import ContainerRepositoryClient
        from azure.identity.aio import DefaultAzureCredential

        client = ContainerRepositoryClient(self.account_url, "my_repository", DefaultAzureCredential())
        # [END create_repository_client]

    async def basic_sample(self):

        from azure.containerregistry.aio import ContainerRegistryClient
        from azure.identity.aio import DefaultAzureCredential

        # Instantiate the client
        client = ContainerRegistryClient(self.account_url, DefaultAzureCredential())
        async with client:
            # Iterate through all the repositories
            async for repository_name in client.list_repositories():
                if repository_name == "hello-world":
                    # Create a repository client from the registry client
                    repository_client = client.get_repository_client(repository_name)

                    async with repository_client:
                        # Show all tags
                        async for tag in repository_client.list_tags():
                            print(tag.digest)


if __name__ == "__main__":
    sample = CreateClients()
    sample.create_registry_client()
    sample.create_repository_client()
