from azure.core.credentials import AzureKeyCredential
from azure.ai.personalizer import PersonalizerClient
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
)


def create_personalizer_client(personalizer_endpoint, personalizer_api_key):
    credential = AzureKeyCredential(personalizer_api_key)
    client = PersonalizerClient(personalizer_endpoint, credential=credential)
    return client


def enable_multi_slot(client, is_live):
    policy = client.policy.get()
    if policy["arguments"].__contains__("--ccb_explore_adf"):
        return

    configuration = client.service_configuration.get()
    if configuration.get("isAutoOptimizationEnabled"):
        configuration["isAutoOptimizationEnabled"] = False
        client.service_configuration.put(configuration)
        if is_live:
            time.sleep(30)

    multi_slot_policy = {
        "name": "enable multi slot",
        "arguments": policy["arguments"].replace("--cb_explore_adf", "--ccb_explore_adf")
    }

    client.policy.update(multi_slot_policy)
    if is_live:
        time.sleep(30)

