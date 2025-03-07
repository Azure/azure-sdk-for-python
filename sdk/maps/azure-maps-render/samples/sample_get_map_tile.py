# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_map_tile.py
DESCRIPTION:
    This sample demonstrates how to request map tiles in vector or raster formats typically
    to be integrated into a map control or SDK. Some example tiles that can be requested are Azure
    Maps road tiles, real-time  Weather Radar tiles. By default, Azure Maps uses vector tiles for its web map
    control (Web SDK) and Android SDK.
USAGE:
    python sample_get_map_tile.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


def get_map_tile():
    # [START get_map_tile]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render import MapsRenderClient
    from azure.maps.render import TilesetID

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    result = maps_render_client.get_map_tile(tileset_id=TilesetID.MICROSOFT_BASE, z=6, x=9, y=22, tile_size="512")

    print("Get map tile result store in file name 'map_tile.png'")
    # print(result)
    with open("map_tile.png", "wb") as file:
        file.write(next(result))
        file.close()
    # [END get_map_tile]


if __name__ == "__main__":
    get_map_tile()
