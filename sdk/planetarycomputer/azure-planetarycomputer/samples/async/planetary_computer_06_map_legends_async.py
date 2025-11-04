# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetary_computer_06_map_legends_async.py

DESCRIPTION:
    This sample demonstrates map legend operations from the Azure Planetary Computer Pro SDK.

USAGE:
    python planetary_computer_06_map_legends_async.py

    Set the environment variable PLANETARYCOMPUTER_ENDPOINT with your endpoint URL.
"""

import os
import asyncio
from azure.planetarycomputer.aio import PlanetaryComputerProClient
from azure.identity.aio import DefaultAzureCredential
from azure.planetarycomputer.models import ColorMapNames

import logging

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.ERROR
)
logging.basicConfig(level=logging.INFO)


async def get_class_map_legend(client: "PlanetaryComputerProClient"):
    """Get a class map legend (categorical color map)."""
    result = await client.data.get_class_map_legend(
        classmap_name=ColorMapNames.MTBS_SEVERITY,
    )
    logging.info(result)


async def get_interval_legend(client: "PlanetaryComputerProClient"):
    """Get an interval legend (continuous color map)."""
    result = await client.data.get_interval_legend(
        classmap_name=ColorMapNames.MODIS64_A1
    )
    logging.info(result)


async def get_legend(client: "PlanetaryComputerProClient"):
    """Get a legend as a PNG image and save it locally."""
    legend_response = await client.data.get_legend(color_map_name="rdylgn")

    # Save the legend to a file
    # Collect the async iterator into a list
    legend_bytes_chunks = []
    async for chunk in legend_response:
        legend_bytes_chunks.append(chunk)
    legend_bytes = b"".join(legend_bytes_chunks)
    filename = "legend_rdylgn.png"
    with open(filename, "wb") as f:
        f.write(legend_bytes)

    logging.info(f"Legend saved as: {filename} ({len(legend_bytes)} bytes)")


async def main():
    endpoint = os.environ.get("PLANETARYCOMPUTER_ENDPOINT")

    if not endpoint:
        raise ValueError("PLANETARYCOMPUTER_ENDPOINT environment variable must be set")

    credential = DefaultAzureCredential()

    client = PlanetaryComputerProClient(endpoint=endpoint, credential=credential)

    await get_class_map_legend(client)
    await get_interval_legend(client)
    await get_legend(client)

    await client.close()
    await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
