# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_map_static_image_async.py
DESCRIPTION:
    This sample demonstrates how to the static image service renders a user-defined, rectangular image containing a map section using a zoom level from 0 to 20. The static image service renders a user-defined, rectangular image containing a map section using a zoom level from 0 to 20.
USAGE:
    python sample_get_map_static_image_async.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def get_map_static_image_async():
    # [START get_map_static_image_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render.aio import MapsRenderClient

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    async with maps_render_client:
        result = await maps_render_client.get_map_static_image(img_format="png", center=(52.41064,4.84228))
    # [END get_map_static_image_async]

if __name__ == '__main__':
   asyncio.run(get_map_static_image_async())