# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py

DESCRIPTION:
    This sample demonstrates how to authenticate with the text analytics service.

    There are two supported methods of authentication:
    1) Use a cognitive services/text analytics API key with TextAnalyticsApiKeyCredential
    2) Use a token credential to authenticate with Azure Active Directory

    See more details about authentication here:
    https://docs.microsoft.com/azure/cognitive-services/authentication

USAGE:
    python sample_authentication.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services/text analytics resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics API key
    3) AZURE_CLIENT_ID - the client ID of your active directory application.
    4) AZURE_TENANT_ID - the tenant ID of your active directory application.
    5) AZURE_CLIENT_SECRET - the secret of your active directory application.
"""

import os


class AuthenticationSample(object):

    def authentication_with_api_key_credential(self):
        # [START create_ta_client_with_key]
        from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential
        endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
        key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

        text_analytics_client = TextAnalyticsClient(endpoint, TextAnalyticsApiKeyCredential(key))
        # [END create_ta_client_with_key]

        doc = ["I need to take my cat to the veterinarian."]
        result = text_analytics_client.detect_language(doc)

        print("Language detected: {}".format(result[0].primary_language.name))
        print("Confidence score: {}".format(result[0].primary_language.score))

    def authentication_with_azure_active_directory(self):
        """DefaultAzureCredential will use the values from the environment
        variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
        """
        # [START create_ta_client_with_aad]
        from azure.ai.textanalytics import TextAnalyticsClient
        from azure.identity import DefaultAzureCredential

        endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
        credential = DefaultAzureCredential()

        text_analytics_client = TextAnalyticsClient(endpoint, credential=credential)
        # [END create_ta_client_with_aad]

        doc = ["I need to take my cat to the veterinarian."]
        result = text_analytics_client.detect_language(doc)

        print("Language detected: {}".format(result[0].primary_language.name))
        print("Confidence score: {}".format(result[0].primary_language.score))


if __name__ == '__main__':
    sample = AuthenticationSample()
    sample.authentication_with_api_key_credential()
    sample.authentication_with_azure_active_directory()
