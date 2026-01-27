# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to create, get, update, and delete a search index.

USAGE:
    python sample_index_crud.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
"""


import os
from typing import List

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
index_name = "hotels-sample-index-index-crud"


def create_index():
    # [START create_index]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        ComplexField,
        CorsOptions,
        SearchIndex,
        ScoringProfile,
        SearchFieldDataType,
        SimpleField,
        SearchableField,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    fields = [
        SimpleField(name="HotelId", type=SearchFieldDataType.STRING, key=True),
        SimpleField(name="HotelName", type=SearchFieldDataType.STRING, searchable=True),
        SimpleField(name="BaseRate", type=SearchFieldDataType.DOUBLE),
        SearchableField(name="Description", type=SearchFieldDataType.STRING, collection=True),
        ComplexField(
            name="Address",
            fields=[
                SimpleField(name="StreetAddress", type=SearchFieldDataType.STRING),
                SimpleField(name="City", type=SearchFieldDataType.STRING),
            ],
            collection=True,
        ),
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profiles: List[ScoringProfile] = []
    index = SearchIndex(
        name=index_name,
        fields=fields,
        scoring_profiles=scoring_profiles,
        cors_options=cors_options,
    )

    result = index_client.create_index(index)
    print(f"Created: index '{result.name}'")
    # [END create_index]


def get_index():
    # [START get_index]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    result = index_client.get_index(index_name)
    print(f"Retrieved: index '{result.name}'")
    # [END get_index]


def update_index():
    # [START update_index]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        ComplexField,
        CorsOptions,
        SearchIndex,
        ScoringProfile,
        SearchFieldDataType,
        SimpleField,
        SearchableField,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    fields = [
        SimpleField(name="HotelId", type=SearchFieldDataType.STRING, key=True),
        SimpleField(name="HotelName", type=SearchFieldDataType.STRING, searchable=True),
        SimpleField(name="BaseRate", type=SearchFieldDataType.DOUBLE),
        SearchableField(name="Description", type=SearchFieldDataType.STRING, collection=True),
        ComplexField(
            name="Address",
            fields=[
                SimpleField(name="StreetAddress", type=SearchFieldDataType.STRING),
                SimpleField(name="City", type=SearchFieldDataType.STRING),
                SimpleField(name="State", type=SearchFieldDataType.STRING),
            ],
            collection=True,
        ),
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profile = ScoringProfile(name="MyProfile")
    scoring_profiles = []
    scoring_profiles.append(scoring_profile)
    index = SearchIndex(
        name=index_name,
        fields=fields,
        scoring_profiles=scoring_profiles,
        cors_options=cors_options,
    )

    result = index_client.create_or_update_index(index=index)
    print(f"Updated: index '{result.name}'")
    # [END update_index]


def delete_index():
    # [START delete_index]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    index_client.delete_index(index_name)
    print(f"Deleted: index '{index_name}'")
    # [END delete_index]


if __name__ == "__main__":
    create_index()
    get_index()
    update_index()
    delete_index()
