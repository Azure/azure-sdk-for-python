import functools
import inspect
import random
import datetime
from azure.health.deidentification import DeidentificationClient


from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
)

RealtimeEnv = functools.partial(
    EnvironmentVariableLoader,
    "healthdataaiservices",
    healthdataaiservices_deid_service_endpoint="https://deid-service-endpoint.com",
)

BatchEnv = functools.partial(
    EnvironmentVariableLoader,
    "healthdataaiservices",
    healthdataaiservices_deid_service_endpoint="https://deid-service-endpoint.com",
    healthdataaiservices_storage_account_name="blobstorageaccount",
    healthdataaiservices_storage_container_name="containername",
    healthdataaiservices_sas_uri="TESTINGONLY REMOVE",
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
        jobname = self.create_random_name(caller_function_name)
        if self.in_recording:
            print("Recording")
            pass
        elif self.is_live:
            random.seed(str(datetime.now()))
            jobname += random.randint(0, 100000)

        jobname += "2"
        return jobname
