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

    Set the environment variable PLANETARYCOMPUTER_ENDPOINT with your endpoint URL.
    Set the environment variable AZURE_COLLECTION_ID with your collection ID.
"""

import os
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential
from urllib.request import urlopen

import logging

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)


def generate_sas_token(client: PlanetaryComputerProClient, collection_id: str):
    """Generate a SAS token for a collection."""
    get_token_response = client.shared_access_signature.get_token(collection_id=collection_id, duration_in_minutes=60)
    return get_token_response


def sign_asset_href(client: PlanetaryComputerProClient, collection_id: str):
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

    get_sign_response = client.shared_access_signature.get_sign(href=href, duration_in_minutes=60)
    return get_sign_response.href, href  # Return both signed and unsigned hrefs


def download_asset(signed_href: str):
    """Download and verify an asset using a signed HREF."""
    with urlopen(signed_href) as http_response:
        content = http_response.read()

        # Check HTTP status
        if http_response.status != 200:
            raise Exception(f"Failed to download asset: HTTP {http_response.status}")

        # Check that the response has content
        content_length = len(content)
        if content_length == 0:
            raise Exception("Downloaded image has zero size")

        # Check that it's a PNG by verifying the PNG magic bytes (89 50 4E 47)
        is_png = content[:8] == b"\x89PNG\r\n\x1a\n"
        if not is_png:
            raise Exception(f"Downloaded content is not a valid PNG file (magic bytes: {content[:8].hex()})")


def revoke_token(client: PlanetaryComputerProClient):
    """Revoke the current SAS token."""
    revoke_token_response = client.shared_access_signature.revoke_token()
    return revoke_token_response


def main():
    # Get configuration from environment
    endpoint = os.environ.get("PLANETARYCOMPUTER_ENDPOINT")
    collection_id = os.environ.get("PLANETARYCOMPUTER_COLLECTION_ID")

    assert endpoint is not None
    assert collection_id is not None

    # Create client
    client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Using API for signing a given URI
    signed_href, unsigned_href = sign_asset_href(client, collection_id)

    # Using SAS token appended to unsigned URI
    sas_token_response = generate_sas_token(client, collection_id)
    sas_token = sas_token_response.token
    href_with_sas = f"{unsigned_href}?{sas_token}"

    # Test both methods
    download_asset(signed_href)
    download_asset(href_with_sas)

    revoke_token(client)


if __name__ == "__main__":
    main()
