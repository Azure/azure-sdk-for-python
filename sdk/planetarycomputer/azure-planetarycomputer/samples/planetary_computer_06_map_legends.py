# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetary_computer_06_map_legends.py

DESCRIPTION:
    This sample demonstrates map legend operations from the Azure Planetary Computer Pro SDK.

USAGE:
    python planetary_computer_06_map_legends.py

    Set the environment variable AZURE_PLANETARY_COMPUTER_ENDPOINT with your endpoint URL.
"""

import os
import io
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential
from azure.planetarycomputer.models import ColorMapNames
from PIL import Image as PILImage

import logging
from azure.core.pipeline.policies import HttpLoggingPolicy

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)


def get_class_map_legend(client):
    """Get a class map legend (categorical color map)."""
    result = client.tiler.get_class_map_legend(
        classmap_name=ColorMapNames.MTBS_SEVERITY,
    )
    logging.info(result)


def get_interval_legend(client):
    """Get an interval legend (continuous color map)."""
    result = client.tiler.get_interval_legend(classmap_name=ColorMapNames.MODIS64_A1)
    logging.info(result)


def get_legend(client):
    """Get a legend as a PNG image."""
    legend_response = client.tiler.get_legend(color_map_name="rdylgn")

    # Convert the binary response to an image
    legend_bytes = b"".join(legend_response)
    legend_image = PILImage.open(io.BytesIO(legend_bytes))

    logging.info(f"Legend image loaded: {legend_image.format} {legend_image.size} {legend_image.mode}")


def main():
    endpoint = os.environ.get("AZURE_PLANETARY_COMPUTER_ENDPOINT")

    if not endpoint:
        raise ValueError("AZURE_PLANETARY_COMPUTER_ENDPOINT environment variable must be set")

    client = PlanetaryComputerClient(endpoint=endpoint, credential=DefaultAzureCredential())

    get_class_map_legend(client)
    get_interval_legend(client)
    get_legend(client)


if __name__ == "__main__":
    main()
