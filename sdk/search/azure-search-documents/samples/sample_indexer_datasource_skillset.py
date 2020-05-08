"""
FILE: sample_indexer_datasource_skillset.py
DESCRIPTION:
    This sample demonstrates use an indexer, datasource and skillset together.

    Indexer is used to efficiently write data to an index using a datasource.
    So we first identify a supported data source - we use azure storage blobs
    in this example. Then we create an index which is compatible with the datasource.
    Further, we create an azure cognitive search datasource which we require to finally
    create an indexer.

    Additionally, we will also use skillsets to provide some AI enhancements in our indexers.

    Once we create the indexer, we run the indexer and perform some basic operations like getting
    the indexer status.

    The datasource used in this sample is stored as metadata for empty blobs in "searchcontainer".
    The json file can be found in samples/files folder named patient_data.json has the metdata of
    each blob.
USAGE:
    python sample_indexer_datasource_skillset.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_API_KEY - your search API key
    3) AZURE_STORAGE_CONNECTION_STRING - The connection string for the storage blob account that is
    being used to create the datasource.
"""

import os
import datetime

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import (
    DataSource, DataContainer, DataSourceCredentials, Index, Indexer, SimpleField, edm,
    EntityRecognitionSkill, InputFieldMappingEntry, OutputFieldMappingEntry, Skillset,
    CorsOptions, IndexingSchedule
)
from azure.search.documents import SearchServiceClient


service_client = SearchServiceClient(service_endpoint, AzureKeyCredential(key))

def _create_index():
    name = "patient-index"

    # Here we create an index with listed fields.
    fields = [
        SimpleField(name="agebracket", type=edm.String, filterable=True, sortable=True),
        SimpleField(name="backupnotes", type=edm.String),
        SimpleField(name="contractedfromwhichpatientsuspected", type=edm.String),
        SimpleField(name="currentstatus", type=edm.String, filterable=True),
        SimpleField(name="dateannounced", type=edm.String),
        SimpleField(name="detectedcity", type=edm.String),
        SimpleField(name="detecteddistrict", type=edm.String),
        SimpleField(name="detectedstate", type=edm.String),
        SimpleField(name="estimatedonsetdate", type=edm.String),
        SimpleField(name="gender", type=edm.String, filterable=True),
        SimpleField(name="nationality", type=edm.String),
        SimpleField(name="notes", type=edm.String),
        SimpleField(name="patientnumber", type=edm.String, key=True, filterable=True),
        SimpleField(name="statecode", type=edm.String),
        SimpleField(name="typeoftransmission", type=edm.String),
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)

    # pass in the name, fields and cors options and create the index
    index = Index(
        name=name,
        fields=fields,
        cors_options=cors_options)
    index_client = service_client.get_indexes_client()
    result = index_client.create_index(index)
    return result

def _create_datasource():
    # Here we create a datasource. As mentioned in the description we have stored it in
    # "searchcontainer"
    ds_client = service_client.get_datasources_client()
    credentials = DataSourceCredentials(connection_string=connection_string)
    container = DataContainer(name='searchcontainer')
    ds = DataSource(name="patient-datasource", type="azureblob", credentials=credentials, container=container)
    data_source = ds_client.create_datasource(ds)
    return data_source

def _create_skillset():
    client = service_client.get_skillsets_client()
    inp = InputFieldMappingEntry(name="text", source="/document/dateannounced")
    output = OutputFieldMappingEntry(name="dateTimes", target_name="Date")
    s = EntityRecognitionSkill(name="merge-skill", inputs=[inp], outputs=[output])

    result = client.create_skillset(name='patient-data-skill', skills=[s], description="example skillset")
    return result

def sample_indexer_workflow():
    # Now that we have a datasource and an index, we can create an indexer.

    skillset_name = _create_skillset().name
    print("Skillset is created")

    ds_name = _create_datasource().name
    print("Data source is created")

    ind_name = _create_index().name
    print("Index is created")

    # we pass the data source, skillsets and targeted index to build an indexer
    indexer = Indexer(
        name="patient-data-indexer",
        data_source_name=ds_name,
        target_index_name=ind_name,
        skillset_name=skillset_name
    )

    indexer_client = service_client.get_indexers_client()
    indexer_client.create_indexer(indexer) # create the indexer

    # to get an indexer
    result = indexer_client.get_indexer("patient-data-indexer")
    print(result)

    # To run an indexer, we can use run_indexer()
    indexer_client.run_indexer(result.name)

    # Using create or update to schedule an indexer

    schedule = IndexingSchedule(interval=datetime.timedelta(hours=24))
    result.schedule = schedule
    updated_indexer = indexer_client.create_or_update_indexer(result)

    print(updated_indexer)

    # get the status of an indexer
    indexer_client.get_indexer_status(updated_indexer.name)

if __name__=="__main__":
    sample_indexer_workflow()
