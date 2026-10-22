# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_map_static_image.py
DESCRIPTION:
    This sample demonstrates how to the static image service renders a user-defined, rectangular image containing a map section using a zoom level from 0 to 20. The static image service renders a user-defined, rectangular image containing a map section using a zoom level from 0 to 20.
USAGE:
    python sample_get_map_static_image.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


def get_map_static_image():
    # [START get_map_static_image]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render import MapsRenderClient

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    result = maps_render_client.get_map_static_image(zoom=10, bounding_box_private=[13.228, 52.4559, 13.5794, 52.629])

    print("Get map tile result to png file as 'map_static_image.png'")
    # Save result to file as png
    with open("map_static_image.png", "wb") as file:
        file.write(next(result))
        file.close()
    # [END get_map_static_image]


if __name__ == "__main__":
    get_map_static_image()
