# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to run an indexer with a data source and skillset.

USAGE:
    python sample_indexer_workflow.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_STORAGE_CONNECTION_STRING - connection string for the Azure Storage account
"""

import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

index_name = "hotels-sample-index-indexer-workflow"
data_source_name = "hotels-sample-blob"
skillset_name = "hotels-sample-skillset"
indexer_name = "hotels-sample-indexer-indexer-workflow"
container_name = "hotels-sample-container"


def sample_indexer_workflow():
    # [START sample_indexer_workflow]
    import datetime
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient, SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndexerDataContainer,
        SearchIndex,
        SearchIndexer,
        SimpleField,
        SearchFieldDataType,
        EntityRecognitionSkill,
        InputFieldMappingEntry,
        OutputFieldMappingEntry,
        SearchIndexerSkillset,
        CorsOptions,
        IndexingSchedule,
        SearchableField,
        IndexingParameters,
        SearchIndexerDataSourceConnection,
        IndexingParametersConfiguration,
    )

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    # 1. Create an index
    fields = [
        SimpleField(
            name="HotelId",
            type=SearchFieldDataType.STRING,
            filterable=True,
            sortable=True,
            key=True,
        ),
        SearchableField(name="HotelName", type=SearchFieldDataType.STRING),
        SimpleField(name="Description", type=SearchFieldDataType.STRING),
        SimpleField(name="Description_fr", type=SearchFieldDataType.STRING),
        SimpleField(name="Category", type=SearchFieldDataType.STRING),
        SimpleField(name="ParkingIncluded", type=SearchFieldDataType.BOOLEAN, filterable=True),
        SimpleField(name="SmokingAllowed", type=SearchFieldDataType.BOOLEAN, filterable=True),
        SimpleField(name="LastRenovationDate", type=SearchFieldDataType.STRING),
        SimpleField(name="Rating", type=SearchFieldDataType.DOUBLE, sortable=True),
        SimpleField(name="Location", type=SearchFieldDataType.GEOGRAPHY_POINT),
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    index = SearchIndex(name=index_name, fields=fields, cors_options=cors_options)
    index_client.create_index(index)
    print(f"Created: index '{index_name}'")

    # 2. Create a data source
    container = SearchIndexerDataContainer(name=container_name)
    data_source_connection = SearchIndexerDataSourceConnection(
        name=data_source_name,
        type="azureblob",
        connection_string=connection_string,
        container=container,
    )
    indexer_client.create_data_source_connection(data_source_connection)
    print(f"Created: data source '{data_source_name}'")

    # 3. Create a skillset
    inp = InputFieldMappingEntry(name="text", source="/document/lastRenovationDate")
    output = OutputFieldMappingEntry(name="dateTimes", target_name="RenovatedDate")
    skill = EntityRecognitionSkill(name="merge-skill", inputs=[inp], outputs=[output])
    skillset = SearchIndexerSkillset(name=skillset_name, skills=[skill], description="example skillset")
    indexer_client.create_skillset(skillset)
    print(f"Created: skillset '{skillset_name}'")

    # 4. Create an indexer
    configuration = IndexingParametersConfiguration(parsing_mode="jsonArray")
    parameters = IndexingParameters(configuration=configuration)
    indexer = SearchIndexer(
        name=indexer_name,
        data_source_name=data_source_name,
        target_index_name=index_name,
        skillset_name=skillset_name,
        parameters=parameters,
    )
    indexer_client.create_indexer(indexer)
    print(f"Created: indexer '{indexer_name}'")

    # Get the indexer
    result = indexer_client.get_indexer(indexer_name)
    print(f"Retrieved: indexer '{result.name}'")

    # Run the indexer
    indexer_client.run_indexer(result.name)
    print("Started: indexer run")

    # Schedule the indexer
    schedule = IndexingSchedule(interval=datetime.timedelta(hours=24))
    result.schedule = schedule
    updated_indexer = indexer_client.create_or_update_indexer(result)
    if updated_indexer.schedule is not None:
        print(f"Scheduled: indexer every {updated_indexer.schedule.interval}")

    # Get indexer status
    status = indexer_client.get_indexer_status(updated_indexer.name)
    print(f"Status: indexer '{updated_indexer.name}' is {status.status}")
    # [END sample_indexer_workflow]


def delete_indexer_workflow_resources():
    # [START delete_indexer_workflow_resources]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient, SearchIndexClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    indexer_client.delete_indexer(indexer_name)
    print(f"Deleted: indexer '{indexer_name}'")

    indexer_client.delete_skillset(skillset_name)
    print(f"Deleted: skillset '{skillset_name}'")

    indexer_client.delete_data_source_connection(data_source_name)
    print(f"Deleted: data source '{data_source_name}'")

    index_client.delete_index(index_name)
    print(f"Deleted: index '{index_name}'")
    # [END delete_indexer_workflow_resources]


if __name__ == "__main__":
    sample_indexer_workflow()
    delete_indexer_workflow_resources()
