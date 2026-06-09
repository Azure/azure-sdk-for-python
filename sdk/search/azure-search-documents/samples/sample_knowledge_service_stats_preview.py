# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates preview knowledge base and knowledge source service counters.

USAGE:
    python sample_knowledge_service_stats_preview.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
"""

import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]


def main():
    # [START sample_knowledge_service_stats_preview]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    stats = index_client.get_service_statistics()
    print(f"Knowledge bases: {stats.counters.knowledge_base_counter.usage}")
    print(f"Knowledge sources: {stats.counters.knowledge_source_counter.usage}")
    # [END sample_knowledge_service_stats_preview]


if __name__ == "__main__":
    main()
