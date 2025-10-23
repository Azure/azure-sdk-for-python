# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_simple_query.py
DESCRIPTION:
    This sample demonstrates how to get search results from a basic search text
    from an Azure Search index.
USAGE:
    python sample_simple_query.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os

service_endpoint = "https://gh-issue-test.search.windows.net"
index_name = "document-index3-python"


def simple_text_query():
    # [START simple_query]
    from azure.identity import AzureCliCredential
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes.models import (
        SemanticConfiguration,
        SemanticPrioritizedFields,
        SemanticField,
    )

    search_client = SearchClient(service_endpoint, index_name, AzureCliCredential())
    # semantic_config = SemanticConfiguration(
    #     name="semantic_config_name",
    #     prioritized_fields=[
    #         SemanticPrioritizedFields(
    #             title_field=SemanticField(field_name="Title"),
    #             content_fields=[
    #                 SemanticField(field_name="content")
    #             ]
    #         )
    #     ]
    # )

    results = search_client.search(
        search_text="luxury",
        query_type="semantic",
        debug="all",
        semantic_configuration_name="document-semantic-config",
    )

    print("Docs containing 'PersonalizerClient' in the name (or other fields):")
    for result in results:
        print("    Title: {} (chunk {})".format(result["Title"], result["chunk"]))
    # [END simple_query]


if __name__ == "__main__":
    simple_text_query()
