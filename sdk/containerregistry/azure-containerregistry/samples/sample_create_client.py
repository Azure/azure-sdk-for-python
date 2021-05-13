# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_client.py

DESCRIPTION:
    These samples demonstrate creating a ContainerRegistryClient and a ContainerRepository

USAGE:
    python sample_create_client.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account
"""

from dotenv import find_dotenv, load_dotenv
import os


class CreateClients(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    def create_registry_client(self):
        # Instantiate the ContainerRegistryClient
        # [START create_registry_client]
        from azure.containerregistry import ContainerRegistryClient
        from azure.identity import DefaultAzureCredential
        account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]

        client = ContainerRegistryClient(account_url, DefaultAzureCredential())
        # [END create_registry_client]

    def basic_sample(self):

        from azure.containerregistry import ContainerRegistryClient
        from azure.identity import DefaultAzureCredential
        account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]

        # Instantiate the client
        client = ContainerRegistryClient(account_url, DefaultAzureCredential())
        with client:
            # Iterate through all the repositories
            for repository_name in client.list_repository_names():
                if repository_name == "hello-world":
                    # Create a repository object from the registry client
                    container_repository = client.get_repository(repository_name)

                    with container_repository:
                        # Show all tags
                        for manifest in container_repository.list_manifests():
                            print(manifest.tags)

                    # [START delete_repository]
                    client.delete_repository("hello-world")
                    # [END delete_repository]


if __name__ == "__main__":
    sample = CreateClients()
    sample.create_registry_client()
    sample.basic_sample()
