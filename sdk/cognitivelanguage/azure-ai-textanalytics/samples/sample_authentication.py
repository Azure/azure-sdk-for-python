# coding=utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py

DESCRIPTION:
    This sample demonstrates how to authenticate to the Text Analytics service.
    We authenticate using an AzureKeyCredential from azure.core.credentials or a token credential from the
    azure-identity client library.

    See more details about authentication here:
    https://learn.microsoft.com/azure/cognitive-services/authentication

    Note: the endpoint must be formatted to use the custom domain name for your resource:
    https://<NAME-OF-YOUR-RESOURCE>.cognitiveservices.azure.com/

USAGE:
    python sample_authentication.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ENDPOINT - the endpoint to your Text Analytics resource.
    2) AZURE_TEXT_KEY - your Text Analytics API key
"""


def sample_authentication_api_key():
    # [START create_ta_client_with_key]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalysisClient

    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    key = os.environ["AZURE_TEXT_KEY"]

    text_client = TextAnalysisClient(endpoint, AzureKeyCredential(key)) # pylint:disable=unused-variable
    # [END create_ta_client_with_key]


def sample_authentication_with_aad():
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    """
    print("\n.. authentication_with_azure_active_directory")
    # [START create_ta_client_with_aad]
    import os
    from azure.ai.textanalytics import TextAnalysisClient
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    text_client = TextAnalysisClient(endpoint, credential=credential) # pylint:disable=unused-variable
    # [END create_ta_client_with_aad]


def main():
    sample_authentication_api_key()


if __name__ == "__main__":
    main()
