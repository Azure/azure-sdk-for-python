# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_map_attribution_async.py
DESCRIPTION:
    This sample demonstrates how to allows users to request map copyright attribution information for a
    section of a tileset.
USAGE:
    python sample_get_map_attribution_async.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def get_map_attribution_async():
    # [START get_map_attribution_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render.aio import MapsRenderClient
    from azure.maps.render.models import TilesetID, BoundingBox

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    async with maps_render_client:
        result = await maps_render_client.get_map_attribution(
            tileset_id=TilesetID.MICROSOFT_BASE,
            zoom=6,
            bounds=BoundingBox(
                south=42.982261,
                west=24.980233,
                north=56.526017,
                east=1.355233
            )
        )

    print("Get map attribution result:")
    print(result.copyrights[0])
    # [END get_map_attribution_async]

if __name__ == '__main__':
    asyncio.run(get_map_attribution_async())