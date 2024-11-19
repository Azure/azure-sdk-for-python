# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_map_tileset.py
DESCRIPTION:
    This sample demonstrates how to request metadata for a tileset.
USAGE:
    python sample_get_map_tileset.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


def get_map_tileset():
    # [START get_map_tileset]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render import MapsRenderClient
    from azure.maps.render import TilesetID

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    result = maps_render_client.get_map_tileset(tileset_id=TilesetID.MICROSOFT_BASE)

    print("Get map tileset result:")
    print(result.get("tiles", "empty tileset"))
    # [END get_map_tileset]


if __name__ == "__main__":
    get_map_tileset()
