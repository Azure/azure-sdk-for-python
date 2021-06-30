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

from azure.identity import AzureAuthorityHosts


class CreateClients(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    def get_authority(self, endpoint):
        if ".azurecr.io" in endpoint:
            return AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
        if ".azurecr.cn" in endpoint:
            return AzureAuthorityHosts.AZURE_CHINA
        if ".azurecr.us" in endpoint:
            return AzureAuthorityHosts.AZURE_GOVERNMENT
        raise ValueError("Endpoint ({}) could not be understood".format(endpoint))

    def get_credential_scopes(self, authority):
        if authority == AzureAuthorityHosts.AZURE_PUBLIC_CLOUD:
            return "https://management.core.windows.net/.default"
        if authority == AzureAuthorityHosts.AZURE_CHINA:
            return "https://management.chinacloudapi.cn/.default"
        if authority == AzureAuthorityHosts.AZURE_GOVERNMENT:
            return "https://management.usgovcloudapi.net/.default"

    async def create_registry_client(self):
        # Instantiate the ContainerRegistryClient
        # [START create_registry_client]
        from azure.containerregistry.aio import ContainerRegistryClient
        from azure.identity.aio import DefaultAzureCredential

        account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
        authority = self.get_authority(account_url)
        credential = DefaultAzureCredential(authority=authority)
        credential_scopes = self.get_credential_scopes(authority)

        client = ContainerRegistryClient(account_url, credential, credential_scopes=credential_scopes)
        # [END create_registry_client]

    async def basic_sample(self):

        from azure.containerregistry.aio import ContainerRegistryClient
        from azure.identity.aio import DefaultAzureCredential

        account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
        authority = self.get_authority(account_url)
        credential = DefaultAzureCredential(authority=authority)
        credential_scopes = self.get_credential_scopes(authority)

        client = ContainerRegistryClient(account_url, credential, credential_scopes=credential_scopes)
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
    sample = CreateClients()
    await sample.create_registry_client()
    await sample.basic_sample()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
