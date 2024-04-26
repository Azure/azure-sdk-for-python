# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_query_session_async.py
DESCRIPTION:
    To ensure more consistent and unique search results within a user's session, you can use session id.
    Simply include the session_id parameter in your queries to create a unique identifier for each user session.
    This ensures a uniform experience for users throughout their "query session".
USAGE:
    python sample_query_session_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os
import asyncio

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]


async def query_session():
    # [START query_session_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    async with search_client:
        results = await search_client.search(search_text="spa", session_id="session-1")

        print("Hotels containing 'spa' in the name (or other fields):")
        async for result in results:
            print("    Name: {} (rating {})".format(result["hotelName"], result["rating"]))
    # [END query_session_async]


if __name__ == "__main__":
    asyncio.run(query_session())
