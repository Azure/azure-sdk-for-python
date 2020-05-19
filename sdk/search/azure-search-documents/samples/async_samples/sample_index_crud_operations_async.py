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
import asyncio

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchServiceClient
from azure.search.documents import ComplexField, CorsOptions, Index, ScoringProfile, edm, SimpleField, SearchableField

client = SearchServiceClient(service_endpoint, AzureKeyCredential(key)).get_indexes_client()

async def create_index():
    # [START create_index_async]
    name = "hotels"
    fields = [
        SimpleField(name="hotelId", type=edm.String, key=True),
        SimpleField(name="baseRate", type=edm.Double),
        SearchableField(name="description", type=edm.String),
        ComplexField(name="address", fields=[
            SimpleField(name="streetAddress", type=edm.String),
            SimpleField(name="city", type=edm.String),
        ])
    ]

    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profiles = []
    index = Index(
        name=name,
        fields=fields,
        scoring_profiles=scoring_profiles,
        cors_options=cors_options)

    result = await client.create_index(index)
    # [END create_index_async]

async def get_index():
    # [START get_index_async]
    name = "hotels"
    result = await client.get_index(name)
    # [END get_index_async]

async def update_index():
    # [START update_index_async]
    name = "hotels"
    fields = fields = [
        SimpleField(name="hotelId", type=edm.String, key=True),
        SimpleField(name="baseRate", type=edm.Double),
        SearchableField(name="description", type=edm.String),
        SearchableField(name="hotelName", type=edm.String),
        ComplexField(name="address", fields=[
            SimpleField(name="streetAddress", type=edm.String),
            SimpleField(name="city", type=edm.String),
            SimpleField(name="state", type=edm.String),
        ])
    ]

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

    result = await client.create_or_update_index(index_name=index.name, index=index)
    # [END update_index_async]

async def delete_index():
    # [START delete_index_async]
    name = "hotels"
    await client.delete_index(name)
    # [END delete_index_async]

async def main():
    await create_index()
    await get_index()
    await update_index()
    await delete_index()
    await client.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
