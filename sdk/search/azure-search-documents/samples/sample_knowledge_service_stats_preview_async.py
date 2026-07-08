# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates preview knowledge base and knowledge source service counters using async clients.

USAGE:
    python sample_knowledge_service_stats_preview_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
"""

import asyncio
import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]


async def main():
    # [START sample_knowledge_service_stats_preview_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        stats = await index_client.get_service_statistics()
    print(f"Knowledge bases: {stats.counters.knowledge_base_counter.usage}")
    print(f"Knowledge sources: {stats.counters.knowledge_source_counter.usage}")
    # [END sample_knowledge_service_stats_preview_async]


if __name__ == "__main__":
    asyncio.run(main())
