# [START create_client]
from azure.health.deidentification import DeidentificationClient
from azure.identity import DefaultAzureCredential
import os


endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
credential = DefaultAzureCredential()
client = DeidentificationClient(endpoint, credential)
# [END create_client]

# [START handle_error]
from azure.core.exceptions import AzureError
from azure.health.deidentification.models import (
    DeidentificationContent,
)


error_client = DeidentificationClient("https://contoso.deid.azure.com", credential)
body = DeidentificationContent(input_text="Hello, I'm Dr. John Smith.")

try:
    error_client.deidentify_text(body)
except AzureError as e:
    print("\nError: " + e.message)
# [END handle_error]
