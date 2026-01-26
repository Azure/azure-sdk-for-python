# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to upload, merge, get, and delete documents.

USAGE:
    python sample_documents_crud.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the admin key for your search service
"""

import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]


def upload_document():
    # [START upload_document]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

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

    result = search_client.upload_documents(documents=[document])

    print(f"Uploaded: document 100 (succeeded={result[0].succeeded})")
    # [END upload_document]


def merge_document():
    # [START merge_document]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    result = search_client.merge_documents(
        documents=[{"HotelId": "100", "HotelName": "Azure Sanctuary & Spa"}]
    )

    print(f"Merged: document 100 (succeeded={result[0].succeeded})")
    # [END merge_document]


def get_document():
    # [START get_document]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    result = search_client.get_document(key="100")

    print("Result:")
    print(f"  HotelId: 100")
    print(f"  HotelName: {result['HotelName']}")
    # [END get_document]


def delete_document():
    # [START delete_document]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    result = search_client.delete_documents(documents=[{"HotelId": "100"}])

    print(f"Deleted: document 100 (succeeded={result[0].succeeded})")
    # [END delete_document]


if __name__ == "__main__":
    upload_document()
    merge_document()
    get_document()
    delete_document()
