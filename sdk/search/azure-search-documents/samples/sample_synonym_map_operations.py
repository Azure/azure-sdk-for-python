# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_synonym_map_operations.py
DESCRIPTION:
    This sample demonstrates how to get, create, update, or delete a Synonym Map.
USAGE:
    python sample_synonym_map_operations.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_API_KEY - your search API key
"""

import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SynonymMap

client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))


def create_synonym_map():
    # [START create_synonym_map]
    synonyms = [
        "USA, United States, United States of America",
        "Washington, Wash. => WA",
    ]
    synonym_map = SynonymMap(name="test-syn-map", synonyms=synonyms)
    result = client.create_synonym_map(synonym_map)
    print("Create new Synonym Map 'test-syn-map succeeded")
    # [END create_synonym_map]


def create_synonym_map_from_file():
    # [START create_synonym_map_from_file]
    from os.path import dirname, join, realpath

    CWD = dirname(realpath(__file__))
    file_path = join(CWD, "synonym_map.txt")
    with open(file_path, "r") as f:
        solr_format_synonyms = f.read()
        synonyms = solr_format_synonyms.split("\n")
        synonym_map = SynonymMap(name="test-syn-map", synonyms=synonyms)
        result = client.create_synonym_map(synonym_map)
        print("Create new Synonym Map 'test-syn-map succeeded")
    # [END create_synonym_map_from_file]


def get_synonym_maps():
    # [START get_synonym_maps]
    result = client.get_synonym_maps()
    names = [x.name for x in result]
    print("Found {} Synonym Maps in the service: {}".format(len(result), ", ".join(names)))
    # [END get_synonym_maps]


def get_synonym_map():
    # [START get_synonym_map]
    result = client.get_synonym_map("test-syn-map")
    print("Retrived Synonym Map 'test-syn-map' with synonyms")
    if result:
        for syn in result.synonyms:
            print("    {}".format(syn))
    # [END get_synonym_map]


def delete_synonym_map():
    # [START delete_synonym_map]
    client.delete_synonym_map("test-syn-map")
    print("Synonym Map 'test-syn-map' deleted")
    # [END delete_synonym_map]


if __name__ == "__main__":
    create_synonym_map()
    get_synonym_maps()
    get_synonym_map()
    delete_synonym_map()
