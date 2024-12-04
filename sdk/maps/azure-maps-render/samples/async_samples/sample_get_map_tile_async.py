# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_map_tile_async.py
DESCRIPTION:
    This sample demonstrates how to request map tiles in vector or raster formats typically
    to be integrated into a map control or SDK. Some example tiles that can be requested are Azure
    Maps road tiles, real-time  Weather Radar tiles. By default, Azure Maps uses vector tiles for its web map
    control (Web SDK) and Android SDK.
USAGE:
    python sample_get_map_tile_async.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


async def get_map_tile_async():
    # [START get_map_tile_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render.aio import MapsRenderClient
    from azure.maps.render import TilesetID

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    async with maps_render_client:
        result = await maps_render_client.get_map_tile(
            tileset_id=TilesetID.MICROSOFT_BASE, z=6, x=9, y=22, tile_size="512"
        )
    # [END get_map_tile_async]


if __name__ == "__main__":
    asyncio.run(get_map_tile_async())
