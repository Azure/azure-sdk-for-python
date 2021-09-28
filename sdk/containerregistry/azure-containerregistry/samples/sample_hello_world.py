# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_hello_world.py

DESCRIPTION:
    These samples demonstrate creating a ContainerRegistryClient and a ContainerRepository

USAGE:
    python sample_hello_world.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account
"""

from dotenv import find_dotenv, load_dotenv
import os

from azure.containerregistry import ContainerRegistryClient
from azure.identity import DefaultAzureCredential


class CreateClients(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    def create_registry_client(self):
        # Instantiate the ContainerRegistryClient
        # [START create_registry_client]
        account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
        audience = "https://management.azure.com"
        client = ContainerRegistryClient(account_url, DefaultAzureCredential(), audience=audience)
        # [END create_registry_client]

    def basic_sample(self):
        # Instantiate the client
        account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
        audience = "https://management.azure.com"
        client = ContainerRegistryClient(account_url, DefaultAzureCredential(), audience=audience)
        with client:
            # Iterate through all the repositories
            for repository_name in client.list_repository_names():
                if repository_name == "hello-world":
                    for tag in client.list_tag_properties(repository_name):
                        print(tag.digest)

                    # [START delete_repository]
                    client.delete_repository(repository_name, tag.name)
                    # [END delete_repository]


if __name__ == "__main__":
    sample = CreateClients()
    sample.create_registry_client()
    sample.basic_sample()
