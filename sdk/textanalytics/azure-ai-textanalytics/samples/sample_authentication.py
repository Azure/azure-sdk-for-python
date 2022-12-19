# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py

DESCRIPTION:
    This sample demonstrates how to authenticate to the Language service.

    There are two supported methods of authentication:
    1) Use a Language API key with AzureKeyCredential from azure.core.credentials
    2) Use a token credential from azure-identity to authenticate with Azure Active Directory

    See more details about authentication here:
    https://docs.microsoft.com/azure/cognitive-services/authentication

USAGE:
    python sample_authentication.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language API key
    3) AZURE_CLIENT_ID - the client ID of your active directory application.
    4) AZURE_TENANT_ID - the tenant ID of your active directory application.
    5) AZURE_CLIENT_SECRET - the secret of your active directory application.
"""

import os


def sample_authentication_with_api_key_credential() -> None:
    print("\n.. authentication_with_api_key_credential")
    # [START create_ta_client_with_key]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient
    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))
    # [END create_ta_client_with_key]

    doc = [
        """
        I need to take my cat to the veterinarian. She's been coughing for a while and I thought it was just a hairball,
        but now I'm now worried it might be something else. She's still very healthy so I'm not too worried though.
        """
    ]
    result = text_analytics_client.detect_language(doc)

    print(f"Language detected: {result[0].primary_language.name}")
    print(f"Confidence score: {result[0].primary_language.confidence_score}")

def sample_authentication_with_azure_active_directory() -> None:
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    """
    print("\n.. authentication_with_azure_active_directory")
    # [START create_ta_client_with_aad]
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    credential = DefaultAzureCredential()

    text_analytics_client = TextAnalyticsClient(endpoint, credential=credential)
    # [END create_ta_client_with_aad]

    doc = [
        """
        I need to take my cat to the veterinarian. She's been coughing for a while and I thought it was just a hairball,
        but now I'm now worried it might be something else. She's still very healthy so I'm not too worried though.
        """
    ]
    result = text_analytics_client.detect_language(doc)

    print(f"Language detected: {result[0].primary_language.name}")
    print(f"Confidence score: {result[0].primary_language.confidence_score}")


if __name__ == '__main__':
    sample_authentication_with_api_key_credential()
    sample_authentication_with_azure_active_directory()
