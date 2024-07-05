import functools
import inspect
import os
import random
import datetime
import uuid
from azure.health.deidentification import DeidentificationClient


from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
)

RealtimeEnv = functools.partial(
    EnvironmentVariableLoader,
    "healthdataaiservices",
    healthdataaiservices_deid_service_endpoint="deid-service-endpoint.com",
)

BatchEnv = functools.partial(
    EnvironmentVariableLoader,
    "healthdataaiservices",
    healthdataaiservices_deid_service_endpoint="deid-service-endpoint.com",
    healthdataaiservices_storage_account_name="blobstorageaccount",
    healthdataaiservices_storage_container_name="containername",
    healthdataaiservices_sas_uri="https://blobstorageaccount.blob.core.windows.net:443/containername",  # Rely on SASURI sanitizer instead
)


class DeidBaseTestCase(AzureRecordedTestCase):
    OUTPUT_PATH = "_output"

    def make_client(self, endpoint) -> DeidentificationClient:
        credential = self.get_credential(DeidentificationClient)
        client = self.create_client_from_credential(
            DeidentificationClient,
            credential=credential,
            # Client library expects just hostname
            endpoint=endpoint.replace("https://", ""),
            # Skip SSL verification for localhost
            connection_verify="localhost" not in endpoint,
        )
        return client

    def generate_job_name(self) -> str:
        caller_function_name = inspect.stack()[1].function
        uniquifier = os.environ.get("HEALTHDATAAISERVICES_UNIQUIFIER", "")
        job_name = f"{caller_function_name}-{uniquifier}"
        return job_name

    def get_storage_location(self, kwargs):
        storage_name: str = kwargs.pop("healthdataaiservices_storage_account_name")
        container_name: str = kwargs.pop("healthdataaiservices_storage_container_name")
        # storage_location = f"https://{storage_name}.blob.core.windows.net/{container_name}"
        storage_location: str = kwargs.pop("healthdataaiservices_sas_uri")
        return storage_location
