# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_index_crud_operations.py
DESCRIPTION:
    This sample demonstrates how to get, create, update, or delete an index.
USAGE:
    python sample_index_crud_operations.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_API_KEY - your search API key
"""


import os

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchServiceClient, CorsOptions, Index, ScoringProfile

client = SearchServiceClient(service_endpoint, AzureKeyCredential(key)).get_indexes_client()

def create_index():
    # [START create_index]
    name = "hotels"
    fields = [
        {
            "name": "hotelId",
            "type": "Edm.String",
            "key": True,
            "searchable": False
        },
        {
            "name": "baseRate",
            "type": "Edm.Double"
        }]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profiles = []
    index = Index(
        name=name,
        fields=fields,
        scoring_profiles=scoring_profiles,
        cors_options=cors_options)

    result = client.create_index(index)
    # [END create_index]

def get_index():
    # [START get_index]
    name = "hotels"
    result = client.get_index(name)
    # [END get_index]

def update_index():
    # [START update_index]
    name = "hotels"
    fields = [
        {
            "name": "hotelId",
            "type": "Edm.String",
            "key": True,
            "searchable": False
        },
        {
            "name": "baseRate",
            "type": "Edm.Double"
        }]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profile = ScoringProfile(
        name="MyProfile"
    )
    scoring_profiles = []
    scoring_profiles.append(scoring_profile)
    index = Index(
        name=name,
        fields=fields,
        scoring_profiles=scoring_profiles,
        cors_options=cors_options)

    result = client.create_or_update_index(index_name=index.name, index=index)
    # [END update_index]

def delete_index():
    # [START delete_index]
    name = "hotels"
    client.delete_index(name)
    # [END delete_index]

if __name__ == '__main__':
    create_index()
    get_index()
    update_index()
    delete_index()
