# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_map_tileset_async.py
DESCRIPTION:
    This sample demonstrates how to request metadata for a tileset.
USAGE:
    python sample_get_map_tileset_async.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def get_map_tileset_async():
    # [START get_map_tile_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render.aio import MapsRenderClient
    from azure.maps.render.models import TilesetID

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    async with maps_render_client:
        result = await maps_render_client.get_map_tileset(tileset_id=TilesetID.MICROSOFT_BASE)

    print("Get map tileset result:")
    print(result.map_attribution)
    print(result.bounds)
    print(result.version)
    # [END get_map_tile_async]

if __name__ == '__main__':
    asyncio.run(get_map_tileset_async())