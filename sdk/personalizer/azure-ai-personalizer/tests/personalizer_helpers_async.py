from azure.core.credentials import AzureKeyCredential
from azure.ai.personalizer.aio import PersonalizerClient


def create_async_personalizer_client(personalizer_endpoint, personalizer_api_key):
    credential = AzureKeyCredential(personalizer_api_key)
    client = PersonalizerClient(personalizer_endpoint, credential=credential)
    return client

