# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_index_alias_crud_operations.py
DESCRIPTION:
    This sample demonstrates how to get, create, update, or delete an alias with an existing index.
USAGE:
    python sample_index_alias_crud_operations.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_API_KEY - your search API key
    3) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
"""


import os

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
alias_name = "motels"

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
    SearchFieldDataType
)


client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

def create_alias():
    # [START create_alias]
    alias = SearchAlias(name = alias_name, indexes = [index_name])
    result = client.create_alias(alias)
    # [END create_index]

def get_alias():
    # [START get_alias]
    result = client.get_alias(alias_name)
    # [END get_alias]

def update_alias():
    # [START update_alias]
    new_index_name = "hotels"
    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SimpleField(name="baseRate", type=SearchFieldDataType.Double),
        SearchableField(name="description", type=SearchFieldDataType.String, collection=True),
        SearchableField(name="hotelName", type=SearchFieldDataType.String),
        ComplexField(name="address", fields=[
            SimpleField(name="streetAddress", type=SearchFieldDataType.String),
            SimpleField(name="city", type=SearchFieldDataType.String),
            SimpleField(name="state", type=SearchFieldDataType.String),
        ], collection=True)
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profile = ScoringProfile(
        name="MyProfile"
    )
    scoring_profiles = []
    scoring_profiles.append(scoring_profile)
    index = SearchIndex(
        name=new_index_name,
        fields=fields,
        scoring_profiles=scoring_profiles,
        cors_options=cors_options)

    result_index = client.create_or_update_index(index=index)

    alias = SearchAlias(name = alias_name, indexes = [new_index_name])
    result = client.create_or_update_alias(alias)

    # [END update_alias]

def delete_alias():
    # [START delete_alias]

    client.delete_alias(alias_name)
    # [END delete_alias]

if __name__ == '__main__':
    create_alias()
    get_alias()
    update_alias()
    delete_alias()
