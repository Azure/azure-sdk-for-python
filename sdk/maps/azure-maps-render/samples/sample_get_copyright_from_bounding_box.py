# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_copyright_from_bounding_box.py
DESCRIPTION:
    This sample demonstrates how to get copyright information for a given bounding box. Bounding-box requests should specify
    the minimum and maximum longitude and latitude (EPSG-3857) coordinates.
USAGE:
    python sample_get_copyright_from_bounding_box.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


def get_copyright_from_bounding_box():
    # [START get_copyright_from_bounding_box]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render import MapsRenderClient

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    result = maps_render_client.get_copyright_from_bounding_box(
        south_west=[42.982261, 24.980233],
        north_east=[56.526017, 1.355233],
    )

    print("Get copyright from bounding box result:")
    print(result["generalCopyrights"][0] if len(result.get("generalCopyrights", [])) > 0 else "no copyright")


if __name__ == "__main__":
    get_copyright_from_bounding_box()
