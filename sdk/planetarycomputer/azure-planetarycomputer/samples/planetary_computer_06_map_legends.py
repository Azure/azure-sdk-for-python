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
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential
from azure.planetarycomputer.models import ColorMapNames

import logging

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
    """Get a legend as a PNG image and save it locally."""
    legend_response = client.tiler.get_legend(color_map_name="rdylgn")

    # Save the legend to a file
    legend_bytes = b"".join(legend_response)
    filename = "legend_rdylgn.png"
    with open(filename, "wb") as f:
        f.write(legend_bytes)

    logging.info(f"Legend saved as: {filename} ({len(legend_bytes)} bytes)")


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
