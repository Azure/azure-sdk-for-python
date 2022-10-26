# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_copyright_for_world_async.py
DESCRIPTION:
    This sample demonstrates how to serve copyright information for Render Tile  service. In addition
        to basic copyright for the whole map, API is serving  specific groups of copyrights for some
        countries.
        Returns the copyright information for the world. To obtain the default copyright information
        for the whole world, do not specify a tile or bounding box.

USAGE:
    python sample_get_copyright_for_world_async.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def get_copyright_for_world_async():
    # [START get_copyright_for_world_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render.aio import MapsRenderClient

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    async with maps_render_client:
        result = await maps_render_client.get_copyright_for_world()

    print("Get copyright for the world result:")
    print(result.general_copyrights[0])
    # [END get_copyright_for_world_async]

if __name__ == '__main__':
    asyncio.run(get_copyright_for_world_async())