# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetarycomputer_shared_access_signature.py

DESCRIPTION:
    This sample demonstrates Shared Access Signature (SAS) operations including:
    - Generating SAS tokens for collections
    - Signing asset HREFs for authenticated access
    - Revoking SAS tokens
    - Downloading assets using signed URLs

USAGE:
    python planetarycomputer_shared_access_signature.py

    Set the environment variable AZURE_PLANETARY_COMPUTER_ENDPOINT with your endpoint URL.
    Set the environment variable AZURE_COLLECTION_ID with your collection ID.
"""

import os
import io
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential
import httpx
from PIL import Image as PILImage

import logging
from azure.core.pipeline.policies import HttpLoggingPolicy

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)


def generate_sas_token(client: PlanetaryComputerClient, collection_id: str):
    """Generate a SAS token for a collection."""
    get_token_response = client.shared_access_signature.get_token(collection_id=collection_id, duration_in_minutes=60)
    logging.info(get_token_response)
    return get_token_response


def sign_asset_href(client: PlanetaryComputerClient, collection_id: str):
    """Sign an asset HREF to enable authenticated download."""
    collection = client.stac.get_collection(collection_id=collection_id)

    if not collection:
        raise Exception(f"Collection '{collection_id}' not found.")

    if not collection.assets:
        raise Exception(f"No assets found in collection '{collection_id}'.")

    if "thumbnail" in collection.assets.keys():
        href = collection.assets["thumbnail"].href
    else:
        raise Exception("No thumbnail found in collection assets.")

    get_sign_response = client.shared_access_signature.get_sign(href=href)
    logging.info(get_sign_response)
    return get_sign_response.href


def download_asset(signed_href: str):
    """Download and display an asset using a signed HREF."""
    with httpx.Client() as http_client:
        get_visual_href_response = http_client.get(signed_href)
        image = PILImage.open(io.BytesIO(get_visual_href_response.content))

        # Display the image in the notebook
        # In a real notebook, you would use: display(image)
        logging.info(f"Image loaded successfully: {image.format} {image.size} {image.mode}")
        logging.info("(Image would be displayed in Jupyter notebook)")


def revoke_token(client: PlanetaryComputerClient):
    """Revoke the current SAS token."""
    revoke_token_response = client.shared_access_signature.revoke_token()
    logging.info(revoke_token_response)


def main():
    # Get configuration from environment
    endpoint = os.environ.get("AZURE_PLANETARY_COMPUTER_ENDPOINT")
    collection_id = os.environ.get("AZURE_COLLECTION_ID", "naip")

    if not endpoint:
        raise ValueError("AZURE_PLANETARY_COMPUTER_ENDPOINT environment variable must be set")

    # Create client
    client = PlanetaryComputerClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Execute SAS workflow using exact parameters from notebook
    get_token_response = generate_sas_token(client, collection_id)

    signed_href = sign_asset_href(client, collection_id)
    download_asset(signed_href)

    revoke_token(client)


if __name__ == "__main__":
    main()
