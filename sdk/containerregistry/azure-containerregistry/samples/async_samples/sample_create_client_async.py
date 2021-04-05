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
        self.account_url = os.environ["AZURE_CONTAINERREGISTRY_URL"]

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


if __name__ == '__main__':
    sample = CreateClients()
    sample.create_registry_client()
    sample.create_repository_client()
