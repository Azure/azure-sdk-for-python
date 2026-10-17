# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Inspect service and indexer runtime, page through index statistics, and list
    resource definitions with property selection and prefix filters. Read-only:
    this sample does not create or delete resources.

USAGE:
    python sample_service_statistics.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT and AZURE_SEARCH_API_KEY (an admin key).
    Optional AZURE_SEARCH_RESOURCE_PREFIX defaults to "hotels".
    Statistics are collected periodically, not immediately after indexing.
"""

import os


def main():
    # [START sample_service_statistics]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
    from azure.search.documents.indexes.models import ListingSearchType

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
    prefix = os.environ.get("AZURE_SEARCH_RESOURCE_PREFIX", "hotels")
    with SearchIndexClient(endpoint, credential) as index_client, SearchIndexerClient(
        endpoint, credential
    ) as indexer_client:
        statistics = index_client.get_service_statistics()
        runtime = statistics.indexers_runtime
        if runtime is not None:
            print(f"Indexer runtime: used {runtime.used_seconds}s; remaining {runtime.remaining_seconds}s")
            print(f"Reporting period: {runtime.beginning_time} through {runtime.ending_time}")

        for summary in index_client.list_index_stats_summary(
            search=prefix, page_size=1, search_type=ListingSearchType.PREFIX
        ):
            print(f"Index {summary.name}: {summary.document_count} documents; {summary.storage_size} bytes")
            print(f"Vector index size: {summary.vector_index_size} bytes")

        for index in index_client.list_indexes(
            select=["name"], search=prefix, page_size=1, search_type=ListingSearchType.PREFIX
        ):
            print(f"Index: {index.name}")
        for alias in index_client.list_aliases(search=prefix, page_size=1, search_type=ListingSearchType.PREFIX):
            print(f"Alias: {alias.name}")
        for synonym_map in index_client.list_synonym_maps(
            select=["name"], search=prefix, page_size=1, search_type=ListingSearchType.PREFIX
        ):
            print(f"Synonym map: {synonym_map.name}")

        indexers = indexer_client.list_indexers(
            select=["name"], search=prefix, page_size=1, search_type=ListingSearchType.PREFIX
        )
        pages = indexers.by_page()
        for page in pages:
            for indexer in page:
                status = indexer_client.get_indexer_status(indexer.name)
                print(f"Indexer: {indexer.name}; status: {status.status}")
                if status.runtime is not None:
                    print(f"Runtime: {status.runtime.used_seconds}s; remaining: {status.runtime.remaining_seconds}s")
                    print(f"Period: {status.runtime.beginning_time} through {status.runtime.ending_time}")
            # Save this opaque token to resume using indexers.by_page(continuation_token=token).
            print(f"Next page token: {pages.continuation_token}")

        for data_source in indexer_client.list_data_source_connections(
            select=["name"], search=prefix, page_size=1, search_type=ListingSearchType.PREFIX
        ):
            print(f"Data source: {data_source.name}")
        for skillset in indexer_client.list_skillsets(
            select=["name"], search=prefix, page_size=1, search_type=ListingSearchType.PREFIX
        ):
            print(f"Skillset: {skillset.name}")
    # [END sample_service_statistics]


if __name__ == "__main__":
    main()
