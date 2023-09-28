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
    1) CONTAINERREGISTRY_ENDPOINT - The URL of your Container Registry account

    This sample assumes your registry has at least one repository with more than three images,
    run load_registry() if you don't have.
    Set the environment variables with your own values before running load_registry():
    1) CONTAINERREGISTRY_ENDPOINT - The URL of your Container Registry account
    2) CONTAINERREGISTRY_TENANT_ID - The service principal's tenant ID
    3) CONTAINERREGISTRY_CLIENT_ID - The service principal's client ID
    4) CONTAINERREGISTRY_CLIENT_SECRET - The service principal's client secret
"""
import asyncio
import os
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry import ArtifactManifestOrder
from azure.containerregistry.aio import ContainerRegistryClient
from utilities import load_registry, get_authority, get_credential


class DeleteImagesAsync(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
        self.authority = get_authority(self.endpoint)
        self.credential = get_credential(self.authority, is_async=True)

    async def delete_images(self):
        load_registry(self.endpoint)
        # Instantiate an instance of ContainerRegistryClient
        async with ContainerRegistryClient(self.endpoint, self.credential) as client:
            async for repository in client.list_repository_names():
                # Keep the three most recent images, delete everything else
                manifest_count = 0
                async for manifest in client.list_manifest_properties(
                    repository, order_by=ArtifactManifestOrder.LAST_UPDATED_ON_DESCENDING
                ):
                    manifest_count += 1
                    if manifest_count > 3:
                        # Make sure will have the permission to delete the manifest later
                        await client.update_manifest_properties(
                            repository, manifest.digest, can_write=True, can_delete=True
                        )

                        print(f"Deleting {repository}:{manifest.digest}")
                        await client.delete_manifest(repository, manifest.digest)


async def main():
    sample = DeleteImagesAsync()
    await sample.delete_images()


if __name__ == "__main__":
    asyncio.run(main())
