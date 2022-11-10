# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.credentials import AzureKeyCredential
from azure.ai.personalizer import PersonalizerClient, PersonalizerAdministrationClient
from devtools_testutils import EnvironmentVariableLoader
import functools
import time

PersonalizerPreparer = functools.partial(
    EnvironmentVariableLoader,
    'personalizer',
    personalizer_endpoint_single_slot="https://REDACTED.cognitiveservices.azure.com",
    personalizer_api_key_single_slot="REDACTED",
    personalizer_endpoint_multi_slot="https://REDACTED.cognitiveservices.azure.com",
    personalizer_api_key_multi_slot="REDACTED",
    personalizer_preset_endpoint_single_slot="https://REDACTED.cognitiveservices.azure.com",
    personalizer_preset_api_key_single_slot="REDACTED",
)


def create_personalizer_client(personalizer_endpoint, personalizer_api_key):
    credential = AzureKeyCredential(personalizer_api_key)
    client = PersonalizerClient(personalizer_endpoint, credential=credential)
    return client


def create_personalizer_admin_client(personalizer_endpoint, personalizer_api_key):
    credential = AzureKeyCredential(personalizer_api_key)
    client = PersonalizerAdministrationClient(personalizer_endpoint, credential=credential)
    return client


def enable_multi_slot(personalizer_endpoint, personalizer_api_key, is_live):
    client = create_personalizer_admin_client(personalizer_endpoint, personalizer_api_key)
    policy = client.get_policy()
    if policy["arguments"].__contains__("--ccb_explore_adf"):
        return

    configuration = client.get_service_configuration()
    if configuration.get("isAutoOptimizationEnabled"):
        configuration["isAutoOptimizationEnabled"] = False
        client.update_service_configuration(configuration)
        if is_live:
            time.sleep(30)

    multi_slot_policy = {
        "name": "enable multi slot",
        "arguments": policy["arguments"].replace("--cb_explore_adf", "--ccb_explore_adf")
    }

    client.update_policy(multi_slot_policy)
    if is_live:
        time.sleep(30)

