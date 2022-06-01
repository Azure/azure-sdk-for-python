# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_set_image_properties.py

DESCRIPTION:
    This sample demonstrates setting an image's properties on the tag so it can't be overwritten during a lengthy
    deployment.

USAGE:
    python sample_set_image_properties.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account
    
    This sample assumes the registry "myacr.azurecr.io" has a repository "hello-world" with image tagged "v1".
"""

from dotenv import find_dotenv, load_dotenv
import os

from azure.containerregistry import ContainerRegistryClient
from azure.identity import DefaultAzureCredential

class SetImageProperties(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    def set_image_properties(self):
        # Instantiate an instance of ContainerRegistryClient
        audience = "https://management.azure.com"
        endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]

        with ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience=audience) as client:
            # Set permissions on the v1 image's "latest" tag
            client.update_manifest_properties(
                "library/hello-world",
                "latest",
                can_write=False,
                can_delete=False
            )
            # After this update, if someone were to push an update to `myacr.azurecr.io\hello-world:v1`, it would fail.
            # It's worth noting that if this image also had another tag, such as `latest`, and that tag did not have
            # permissions set to prevent reads or deletes, the image could still be overwritten. For example,
            # if someone were to push an update to `<registry endpoint>\hello-world:latest`
            # (which references the same image), it would succeed.


if __name__ == "__main__":
    sample = SetImageProperties()
    sample.set_image_properties()
