from azure.core.credentials import AzureKeyCredential
from azure.ai.personalizer import PersonalizerClient
from devtools_testutils import EnvironmentVariableLoader
import functools


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
