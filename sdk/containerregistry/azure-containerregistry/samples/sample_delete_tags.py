# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_delete_tags.py

DESCRIPTION:
    This sample demonstrates deleting all but the most recent three tags for each repository.

USAGE:
    python sample_delete_tags.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account
"""

from dotenv import find_dotenv, load_dotenv
import os

from azure.containerregistry import ContainerRegistryClient, TagOrder
from azure.identity import DefaultAzureCredential


class DeleteTags(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.account_url = os.environ["CONTAINERREGISTRY_ENDPOINT"]

    def delete_tags(self):
        # [START list_repository_names]
        credential = DefaultAzureCredential()
        audience = "https://management.azure.com"
        client = ContainerRegistryClient(self.account_url, credential, audience=audience)

        for repository in client.list_repository_names():
            print(repository)
            # [END list_repository_names]

            # [START list_tag_properties]
            # Keep the three most recent tags, delete everything else
            tag_count = 0
            for tag in client.list_tag_properties(repository, order_by=TagOrder.LAST_UPDATE_TIME_DESCENDING):
                tag_count += 1
                if tag_count > 3:
                    client.delete_tag(repository, tag.name)
            # [END list_tag_properties]

        client.close()


if __name__ == "__main__":
    sample = DeleteTags()
    sample.delete_tags()
