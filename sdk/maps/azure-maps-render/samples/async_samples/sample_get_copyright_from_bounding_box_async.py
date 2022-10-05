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

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def get_copyright_from_bounding_box_async():
    # [START get_copyright_from_bounding_box_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render.aio import MapsRenderClient
    from azure.maps.render.models import BoundingBox

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))

    async with maps_render_client:
        result = await maps_render_client.get_copyright_from_bounding_box(
            bounding_box=BoundingBox(
                south=42.982261,
                west=24.980233,
                north=56.526017,
                east=1.355233
            )
        )

    print("Get copyright from bounding box result:")
    print(result.general_copyrights[0])
    print("Result country code:")
    print(result.regions[0].country.iso3)
    # [END get_copyright_from_bounding_box]

if __name__ == '__main__':
    asyncio.run(get_copyright_from_bounding_box_async())