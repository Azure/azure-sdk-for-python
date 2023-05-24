# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_set_image_properties_async.py

DESCRIPTION:
    This sample demonstrates setting an image's properties on the tag so it can't be overwritten during a lengthy
    deployment.

USAGE:
    python sample_set_image_properties_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTAINERREGISTRY_ENDPOINT - The URL of your Container Registry account

    This sample assumes your registry has a repository "library/hello-world" with image tagged "v1",
    run load_registry() if you don't have.
    Set the environment variables with your own values before running load_registry():
    1) CONTAINERREGISTRY_ENDPOINT - The URL of your Container Registry account
    2) CONTAINERREGISTRY_TENANT_ID - The service principal's tenant ID
    3) CONTAINERREGISTRY_CLIENT_ID - The service principal's client ID
    4) CONTAINERREGISTRY_CLIENT_SECRET - The service principal's client secret
    5) CONTAINERREGISTRY_RESOURCE_GROUP - The resource group name
    6) CONTAINERREGISTRY_REGISTRY_NAME - The registry name
"""
import asyncio
import os
from dotenv import find_dotenv, load_dotenv
from azure.containerregistry.aio import ContainerRegistryClient
from utilities import load_registry, get_authority, get_credential


class SetImagePropertiesAsync(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.endpoint = os.environ.get("CONTAINERREGISTRY_ENDPOINT")
        self.authority = get_authority(self.endpoint)
        self.credential = get_credential(self.authority, is_async=True)

    async def set_image_properties(self):
        load_registry()
        # Instantiate an instance of ContainerRegistryClient
        async with ContainerRegistryClient(self.endpoint, self.credential) as client:
            # Set permissions on image "library/hello-world:v1"
            await client.update_manifest_properties(
                "library/hello-world",
                "v1",
                can_write=False,
                can_delete=False
            )        
        # After this update, if someone were to push an update to `<registry endpoint>\library\hello-world:v1`,
        # it would fail. It's worth noting that if this image also had another tag, such as `latest`,
        # and that tag did not have permissions set to prevent reads or deletes, the image could still be
        # overwritten. For example, if someone were to push an update to `<registry endpoint>\hello-world:latest`
        # (which references the same image), it would succeed.


async def main():
    sample = SetImagePropertiesAsync()
    await sample.set_image_properties()


if __name__ == "__main__":
    asyncio.run(main())
