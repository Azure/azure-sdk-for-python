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

    This sample assumes your registry has a repository "library/hello-world".
"""
from azure.containerregistry import ContainerRegistryClient
from sample_base import SampleBase


class ListTags(SampleBase):
    def list_tags(self):
        self._set_up()
        # Instantiate an instance of ContainerRegistryClient
        with ContainerRegistryClient(self.endpoint, self.credential, audience=self.audience) as client:
            manifest = client.get_manifest_properties("library/hello-world", "latest")
            print("Tags of " + manifest.repository_name + ": ")
            # Iterate through all the tags
            for tag in manifest.tags:
                print(tag)


if __name__ == "__main__":
    sample = ListTags()
    sample.list_tags()
