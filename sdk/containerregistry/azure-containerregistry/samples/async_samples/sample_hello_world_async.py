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
    1) AZURE_CONTAINERREGISTRY_URL - The URL of you Container Registry account
"""

import asyncio
from dotenv import find_dotenv, load_dotenv
import os

from azure.containerregistry.aio import ContainerRegistryClient
from azure.identity.aio import DefaultAzureCredential


class HelloWorldAsync(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    async def basic_sample(self):
        # Instantiate an instance of ContainerRegistryClient
        # [START create_registry_client]
        endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
        audience = "https://management.azure.com"
        client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience=audience)
        # [END create_registry_client]
        async with client:
            # Iterate through all the repositories
            async for repository_name in client.list_repository_names():
                if repository_name == "hello-world":
                    # Create a repository client from the registry client
                    async for tag in client.list_tag_properties(repository_name):
                        print(tag.digest)

                    # [START delete_repository]
                    await client.delete_repository(repository_name, "hello-world")
                    # [END delete_repository]


async def main():
    sample = HelloWorldAsync()
    await sample.basic_sample()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
