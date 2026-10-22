# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_copyright_caption.py
DESCRIPTION:
    This sample demonstrates how to serve copyright information for Render Tile
    service. In addition to basic copyright for the whole map, API is serving
    specific groups of copyrights for some countries.
USAGE:
    python sample_get_copyright_caption.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


def get_copyright_caption():
    # [START get_copyright_caption]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render import MapsRenderClient

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    result = maps_render_client.get_copyright_caption()

    print("Get copyright caption result:")
    print(result.get("copyrightsCaption", "no caption"))
    # [END get_copyright_caption]


if __name__ == "__main__":
    get_copyright_caption()
