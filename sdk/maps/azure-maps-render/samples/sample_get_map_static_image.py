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

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def get_map_static_image():
    # [START get_map_static_image]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render import MapsRenderClient

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    result = maps_render_client.get_map_static_image(img_format="png", center=(52.41064, 5.84228))

    print("Get map tile result to png:")
    # Save result to file as png
    file = open('map_static_image', 'wb')
    file.write(next(result))
    file.close()
    # [END get_map_static_image]

if __name__ == '__main__':
    get_map_static_image()