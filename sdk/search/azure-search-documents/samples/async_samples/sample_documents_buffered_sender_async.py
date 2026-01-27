# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to use the SearchIndexingBufferedSender for high-throughput indexing.

USAGE:
    python sample_documents_buffered_sender_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the admin key for your search service
"""

import os
import asyncio

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]


async def sample_batching_client_async():
    # [START sample_batching_client_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchIndexingBufferedSender

    document = {
        "HotelId": "100",
        "HotelName": "Azure Sanctuary",
        "Description": "A quiet retreat offering understated elegance and premium amenities.",
        "Description_fr": "Meilleur hôtel en ville si vous aimez les hôtels de luxe.",
        "Category": "Luxury",
        "Tags": [
            "pool",
            "view",
            "wifi",
            "concierge",
            "private beach",
            "gourmet dining",
            "spa",
        ],
        "ParkingIncluded": False,
        "LastRenovationDate": "2024-01-15T00:00:00+00:00",
        "Rating": 5,
        "Location": {"type": "Point", "coordinates": [-122.131577, 47.678581]},
    }

    async with SearchIndexingBufferedSender(service_endpoint, index_name, AzureKeyCredential(key)) as buffered_sender:
        # add upload actions
        await buffered_sender.upload_documents(documents=[document])
        print(f"Uploaded: document {document['HotelId']}")

        # add merge actions
        await buffered_sender.merge_documents(documents=[{"HotelId": "100", "Rating": 4.5}])
        print(f"Merged: document {document['HotelId']}")

        # add delete actions
        await buffered_sender.delete_documents(documents=[{"HotelId": "100"}])
        print(f"Deleted: document {document['HotelId']}")
    # [END sample_batching_client_async]


if __name__ == "__main__":
    asyncio.run(sample_batching_client_async())
