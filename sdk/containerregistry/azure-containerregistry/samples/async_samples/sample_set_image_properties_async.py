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
    1) CONTAINERREGISTRY_ENDPOINT - The URL of you Container Registry account

    This sample assumes your registry has a repository "library/hello-world" with image tagged "v1".
"""
import asyncio
from azure.containerregistry.aio import ContainerRegistryClient
from sample_base_async import SampleBaseAsync


class SetImagePropertiesAsync(SampleBaseAsync):
    async def set_image_properties(self):
        self._set_up()
        # Instantiate an instance of ContainerRegistryClient
        async with ContainerRegistryClient(self.endpoint, self.credential, audience=self.audience) as client:
            # Set permissions on the v1 image's "latest" tag
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
