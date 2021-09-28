# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_list_tags.py

DESCRIPTION:
    This sample demonstrates listing the tags for an image in a repository with anonymous pull access.
    Anonymous access allows a user to list all the collections there, but they wouldn't have permissions to
    modify or delete any of the images in the registry.

USAGE:
    python sample_list_tags.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account

    This sample assumes the registry "myacr.azurecr.io" has a repository "hello-world".
"""

from dotenv import find_dotenv, load_dotenv
import os

from azure.containerregistry import ContainerRegistryClient
from azure.identity import DefaultAzureCredential

class ListTags(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]

    def list_tags(self):
        # Create a new ContainerRegistryClient
        credential = DefaultAzureCredential()
        audience = "https://myacr.azurecr.io"
        client = ContainerRegistryClient(self.account_url, credential, audience=audience)

        manifest = client.get_manifest_properties("library/hello-world", "latest")
        print(manifest.repository_name + ": ")
        for tag in manifest.tags:
            print(tag + "\n")

        client.close()


if __name__ == "__main__":
    sample = ListTags()
    sample.list_tags()
