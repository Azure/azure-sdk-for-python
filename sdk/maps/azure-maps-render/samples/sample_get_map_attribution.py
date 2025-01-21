# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_map_attribution.py
DESCRIPTION:
    This sample demonstrates how to allows users to request map copyright attribution information for a
    section of a tileset.
USAGE:
    python sample_get_map_attribution.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


def get_map_attribution():
    # [START get_map_attribution]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render import MapsRenderClient
    from azure.maps.render import TilesetID

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    result = maps_render_client.get_map_attribution(
        tileset_id=TilesetID.MICROSOFT_BASE,
        zoom=6,
        bounds=[42.982261, 24.980233, 56.526017, 1.355233],
    )

    print("Get map attribution result:")
    print(result["copyrights"][0] if len(result.get("copyrights", [])) > 0 else "no copyrights")
    # [END get_map_attribution]


if __name__ == "__main__":
    get_map_attribution()
