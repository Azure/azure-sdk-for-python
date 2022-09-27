import os
import sys
from azure.core.credentials import AzureKeyCredential


def get_personalizer_client():
    endpoint = get_endpoint()
    api_key = get_api_key()
    from azure.ai.personalizer import PersonalizerClient
    return PersonalizerClient(endpoint, AzureKeyCredential(api_key))


def get_async_personalizer_client():
    endpoint = get_endpoint()
    api_key = get_api_key()
    from azure.ai.personalizer.aio import PersonalizerClient
    return PersonalizerClient(endpoint, AzureKeyCredential(api_key))


def get_endpoint():
    try:
        return os.environ['PERSONALIZER_ENDPOINT']
    except KeyError:
        print("PERSONALIZER_ENDPOINT must be set.")
        sys.exit(1)


def get_api_key():
    try:
        return os.environ['PERSONALIZER_API_KEY']
    except KeyError:
        print("PERSONALIZER_API_KEY must be set.")
        sys.exit(1)
