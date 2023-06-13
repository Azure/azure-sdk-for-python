# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import uuid
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.digitaltwins.core import DigitalTwinsClient

# Scenario example of how to:
# - create a DigitalTwins Service Client using the DigitalTwinsClient constructor
# - create an import job based on a model
# - get import job
# - cancel import job
# - delete import job
#
# Preconditions:
# - Environment variables have to be set
# - DigitalTwins enabled device must exist on the ADT hub
# - Storage account and container with necessary permissions (for more information, go to https://learn.microsoft.com/en-us/azure/digital-twins/concepts-apis-sdks#bulk-import-with-the-jobs-api)
# - Upload input blob file to storage container (Sample blob file can be found in this folder)
#
# For the purpose of this example we will create temporary import job using random Ids.
# We have to make sure these Ids are unique within the DT instance so we use generated UUIDs.
try:
    import_job_id = 'importjob-' + str(uuid.uuid4())

    temporary_import_job = {
        "@id": import_job_id,
        "@input_blob_uri": "storageAccountContainerEndpoint/storageAccountContainerName/sampleInputBlob.ndjson",
        "@output_blob_uri": "storageAccountContainerEndpoint/storageAccountContainerName/sampleOutputBlob.ndjson",
    }

    # DefaultAzureCredential supports different authentication mechanisms and determines
    # the appropriate credential type based of the environment it is executing in.
    # It attempts to use multiple credential types in an order until it finds a working credential.

    # - AZURE_URL: The tenant ID in Azure Active Directory
    url = os.getenv("AZURE_URL")

    # DefaultAzureCredential expects the following three environment variables:
    # - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
    # - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
    # - AZURE_CLIENT_SECRET: The client secret for the registered application
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential)

    # Create import job
    created_import_job = service_client.upsert_import_job(import_job_id, temporary_import_job)
    print('Created Import Job:')
    print(created_import_job)

    # Get import job
    get_import_job = service_client.get_import_jobs(import_job_id)
    print('Get Import Job:')
    print(get_import_job)

    # Cancel import job
    canceled_import_job = service_client.cancel_import_job(import_job_id)
    print('Canceled Import Job:')
    print(canceled_import_job)

    # Delete import job
    service_client.delete_import_job(import_job_id)

except HttpResponseError as e:
    print("\nThis sample has caught an error. {0}".format(e.message))