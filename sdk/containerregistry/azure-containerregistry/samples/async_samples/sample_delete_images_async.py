# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_delete_images_async.py

DESCRIPTION:
    This sample demonstrates deleting all but the most recent three images for each repository.

USAGE:
    python sample_delete_images_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account
"""

import asyncio
from dotenv import find_dotenv, load_dotenv
import os

from azure.containerregistry import ArtifactManifestOrder
from azure.containerregistry.aio import ContainerRegistryClient
from azure.identity.aio import DefaultAzureCredential


class DeleteImagesAsync(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    async def delete_images(self):
        # Instantiate an instance of ContainerRegistryClient
        audience = "https://management.azure.com"
        endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
        credential = DefaultAzureCredential()
        client = ContainerRegistryClient(endpoint, credential, audience=audience)

        async with client:
            async for repository in client.list_repository_names():
                print(repository)

                # Keep the three most recent images, delete everything else
                manifest_count = 0
                async for manifest in client.list_manifest_properties(repository, order_by=ArtifactManifestOrder.LAST_UPDATED_ON_DESCENDING):
                    manifest_count += 1
                    if manifest_count > 3:
                        await client.delete_manifest(repository, manifest.digest)


async def main():
    sample = DeleteImagesAsync()
    await sample.delete_images()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
