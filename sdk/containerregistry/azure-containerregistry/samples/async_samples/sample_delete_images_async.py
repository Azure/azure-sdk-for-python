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

from azure.containerregistry import ManifestOrder
from azure.containerregistry.aio import ContainerRegistryClient
from azure.identity.aio import DefaultAzureCredential


class DeleteImagesAsync(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]

    async def delete_images(self):
        # [START list_repository_names]
        credential = DefaultAzureCredential()
        client = ContainerRegistryClient(self.account_url, credential)

        async with client:
            async for repository in client.list_repository_names():
                print(repository)
                # [END list_repository_names]

                # [START list_tag_properties]
                # Keep the three most recent images, delete everything else
                tag_count = 0
                async for tag in client.list_tag_properties(repository, order_by=ManifestOrder.LAST_UPDATE_TIME_DESCENDING):
                    tag_count += 1
                    if tag_count > 3:
                        await client.delete_manifest(repository, tag.name)
                # [END list_tag_properties]


async def main():
    sample = DeleteImagesAsync()
    await sample.delete_images()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
