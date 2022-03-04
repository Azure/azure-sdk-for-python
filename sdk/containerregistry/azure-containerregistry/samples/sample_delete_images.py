# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_delete_images.py

DESCRIPTION:
    This sample demonstrates deleting all but the most recent three images for each repository.

USAGE:
    python sample_delete_images.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account
"""

from dotenv import find_dotenv, load_dotenv
import os

from azure.containerregistry import ContainerRegistryClient, ArtifactManifestOrder
from azure.identity import DefaultAzureCredential

class DeleteImages(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    def delete_images(self):
        # Instantiate an instance of ContainerRegistryClient
        audience = "https://management.azure.com"
        endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]

        with ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience=audience) as client:
            for repository in client.list_repository_names():
                print(repository)

                # Keep the three most recent images, delete everything else
                manifest_count = 0
                for manifest in client.list_manifest_properties(
                    repository, order_by=ArtifactManifestOrder.LAST_UPDATED_ON_DESCENDING):
                    manifest_count += 1
                    if manifest_count > 3:
                        print("Deleting {}:{}".format(repository, manifest.digest))
                        client.delete_manifest(repository, manifest.digest)


if __name__ == "__main__":
    sample = DeleteImages()
    sample.delete_images()
