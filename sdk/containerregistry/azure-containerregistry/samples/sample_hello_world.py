# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_hello_world.py

DESCRIPTION:
    This sample demonstrate creating a ContainerRegistryClient and iterating
    through the collection of tags in the repository with anonymous access.

USAGE:
    python sample_hello_world.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account

    This sample assumes your registry has a repository "library/hello-world", run load_registry() if you don't have.
    Set the environment variables with your own values before running load_registry():
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account
    2) CONTAINERREGISTRY_TENANT_ID - The service principal's tenant ID
    3) CONTAINERREGISTRY_CLIENT_ID - The service principal's client ID
    4) CONTAINERREGISTRY_CLIENT_SECRET - The service principal's client secret
    5) CONTAINERREGISTRY_RESOURCE_GROUP - The resource group name
    6) CONTAINERREGISTRY_REGISTRY_NAME - The registry name
"""
import os
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry import ContainerRegistryClient
from utilities import load_registry, get_authority, get_audience, get_credential


class HelloWorld(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ.get("CONTAINERREGISTRY_ENDPOINT")
        self.authority = get_authority(self.endpoint)
        self.audience = get_audience(self.authority)
        self.credential = get_credential(self.authority)

    def basic_sample(self):
        load_registry()
        # Instantiate an instance of ContainerRegistryClient
        # [START create_registry_client]
        with ContainerRegistryClient(self.endpoint, self.credential, audience=self.audience) as client:
        # [END create_registry_client]
            # Iterate through all the repositories
            for repository_name in client.list_repository_names():
                print(repository_name)
                if repository_name == "library/hello-world":
                    print("Tags of repository library/hello-world:")
                    for tag in client.list_tag_properties(repository_name):
                        print(tag.name)
                        
                        # Make sure will have the permission to delete the repository later
                        client.update_manifest_properties(
                            repository_name,
                            tag.name,
                            can_write=True,
                            can_delete=True
                        )

                    print("Deleting " + repository_name)
                    # [START delete_repository]
                    client.delete_repository(repository_name)
                    # [END delete_repository]


if __name__ == "__main__":
    sample = HelloWorld()
    sample.basic_sample()
