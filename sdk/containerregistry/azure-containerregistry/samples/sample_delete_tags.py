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

    This sample assumes your registry has at least one repository with more than three tags.
"""
from azure.containerregistry import ContainerRegistryClient, ArtifactTagOrder
from sample_base import SampleBase


class DeleteTags(SampleBase):
    def delete_tags(self):
        self._set_up()    
        with ContainerRegistryClient(self.endpoint, self.credential, audience=self.audience) as client:
            # [START list_repository_names]
            for repository in client.list_repository_names():
                print(repository)
                # [END list_repository_names]

                # Keep the three most recent tags, delete everything else
                tag_count = 0
                for tag in client.list_tag_properties(
                    repository, order_by=ArtifactTagOrder.LAST_UPDATED_ON_DESCENDING
                ):
                    tag_count += 1
                    if tag_count > 3:
                        print("Deleting {}:{}".format(repository, tag.name))
                        client.delete_tag(repository, tag.name)


if __name__ == "__main__":
    sample = DeleteTags()
    sample.delete_tags()
