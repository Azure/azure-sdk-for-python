# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_copyright_from_bounding_box_async.py
DESCRIPTION:
    This sample demonstrates how to get copyright information for a given bounding box. Bounding-box requests should specify
    the minimum and maximum longitude and latitude (EPSG-3857) coordinates.
USAGE:
    python sample_get_copyright_from_bounding_box_async.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import asyncio
import os
import json

def to_json(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__,
        sort_keys=True,
        indent=4
    )

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def get_copyright_from_bounding_box_async():
    # [START get_copyright_from_bounding_box_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render.aio import MapsRenderClient
    from azure.maps.render.models import BoundingBox, LatLon

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    async with maps_render_client:
        result = await maps_render_client.get_copyright_from_bounding_box(
        bounding_box=BoundingBox(bottom_left=LatLon(52.41064,4.84228), top_right=LatLon(52.41072,4.84239))
    )

    print("Get copyright from bounding box result:")
    print(result)
    print("------------------------------")
    print("Get copyright from bounding box result in Json format:")
    print(to_json(result))
    # [END get_copyright_from_bounding_box]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_copyright_from_bounding_box_async())