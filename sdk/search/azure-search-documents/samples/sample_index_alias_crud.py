# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to create, get, update, and delete an index alias.

USAGE:
    python sample_index_alias_crud.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
"""


import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]
alias_name = "hotel-alias"
new_index_name = "hotels-sample-index-v2"


def create_alias():
    # [START create_alias]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import SearchAlias

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    alias = SearchAlias(name=alias_name, indexes=[index_name])
    result = index_client.create_alias(alias)
    print(f"Created: alias '{result.name}' -> index '{index_name}'")
    # [END create_alias]


def get_alias():
    # [START get_alias]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    result = index_client.get_alias(alias_name)
    print(f"Retrieved: alias '{result.name}'")
    # [END get_alias]


def update_alias():
    # [START update_alias]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        ComplexField,
        CorsOptions,
        ScoringProfile,
        SearchAlias,
        SearchIndex,
        SimpleField,
        SearchableField,
        SearchFieldDataType,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    # Create a new index with a different schema or settings
    # In a real scenario, this would be your updated index version (e.g., v2)
    fields = [
        SimpleField(name="HotelId", type=SearchFieldDataType.STRING, key=True),
        SimpleField(name="BaseRate", type=SearchFieldDataType.DOUBLE),
        SearchableField(name="Description", type=SearchFieldDataType.STRING, collection=True),
        SearchableField(name="HotelName", type=SearchFieldDataType.STRING),
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
    index = SearchIndex(
        name=new_index_name,
        fields=fields,
        scoring_profiles=[scoring_profile],
        cors_options=cors_options,
    )

    index_client.create_or_update_index(index=index)
    print(f"Created: index '{new_index_name}'")

    # Update the alias to point to the new index
    # This operation is atomic and ensures zero downtime for applications using the alias
    alias = SearchAlias(name=alias_name, indexes=[new_index_name])
    result = index_client.create_or_update_alias(alias)
    print(f"Updated: alias '{result.name}' -> index '{new_index_name}'")
    # [END update_alias]


def delete_alias():
    # [START delete_alias]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.core.exceptions import ResourceNotFoundError

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    index_client.delete_alias(alias_name)
    print(f"Deleted: alias '{alias_name}'")

    try:
        index_client.delete_index(new_index_name)
        print(f"Deleted: index '{new_index_name}'")
    except ResourceNotFoundError:
        print(f"Skipped: index '{new_index_name}' not found")
    # [END delete_alias]


if __name__ == "__main__":
    create_alias()
    get_alias()
    update_alias()
    delete_alias()
