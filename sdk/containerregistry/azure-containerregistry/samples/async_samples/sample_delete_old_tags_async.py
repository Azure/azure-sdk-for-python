# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_delete_old_tags_async.py

DESCRIPTION:
    These samples demonstrates deleting the three oldest tags for each repository asynchronously.

USAGE:
    python sample_delete_old_tags_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account
"""

import asyncio
from dotenv import find_dotenv, load_dotenv
import os


class DeleteOperations(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]

    async def delete_old_tags(self):
        from azure.containerregistry import TagOrderBy
        from azure.containerregistry.aio import (
            ContainerRegistryClient,
            ContainerRepositoryClient,
        )
        from azure.identity.aio import DefaultAzureCredential

        # [START list_repositories]
        account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]
        credential = DefaultAzureCredential()
        client = ContainerRegistryClient(account_url, credential)

        async for repository in client.list_repositories():
            repository_client = ContainerRepositoryClient(account_url, repository, credential)
            # [END list_repositories]

            # [START list_tags]
            tag_count = 0
            async for tag in repository_client.list_tags(order_by=TagOrderBy.LAST_UPDATE_TIME_DESCENDING):
                tag_count += 1
                if tag_count > 3:
                    await repository_client.delete_tag(tag.name)
            # [END list_tags]

        await client.close()


async def main():
    sample = DeleteOperations()
    sample.delete_old_tags()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
