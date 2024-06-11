import functools
import inspect
import random
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
    healthdataaiservices_storage_account_sas_uri="https://mystorage.blob.core.windows.net/container-test?sv=2015-04-05&ss=b&srt=sco&sp=rwlca&se=2024-06-08T02%3A19%3A02.0000000Z&spr=https&sig=signature%3D",
)


class DeidBaseTestCase(AzureRecordedTestCase):
    OUTPUT_PATH = "_output"

    def make_client(self, endpoint) -> DeidentificationClient:
        credential = self.get_credential(DeidentificationClient)
        client = self.create_client_from_credential(
            DeidentificationClient,
            credential=credential,
            endpoint=endpoint.replace(
                "https://", ""
            ),  # Client library expects just hostname
            connection_verify="localhost"
            not in endpoint,  # Skip SSL verification for localhost
        )
        return client

    def generate_job_name(self) -> str:
        caller_function_name = inspect.stack()[1].function
        jobname = self.create_random_name(caller_function_name)
        if self.in_recording:
            pass
        elif self.is_live:
            jobname += random.randint(0, 100000)

        return jobname
