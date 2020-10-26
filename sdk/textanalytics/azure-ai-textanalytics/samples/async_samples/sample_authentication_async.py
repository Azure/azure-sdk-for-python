# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication_async.py

DESCRIPTION:
    This sample demonstrates how to authenticate to the Text Analytics service.

    There are two supported methods of authentication:
    1) Use a Cognitive Services/Text Analytics API key with AzureKeyCredential from azure.core.credentials
    2) Use a token credential from azure-identity to authenticate with Azure Active Directory

    See more details about authentication here:
    https://docs.microsoft.com/azure/cognitive-services/authentication

USAGE:
    python sample_authentication_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Cognitive Services/Text Analytics API key
    3) AZURE_CLIENT_ID - the client ID of your active directory application.
    4) AZURE_TENANT_ID - the tenant ID of your active directory application.
    5) AZURE_CLIENT_SECRET - the secret of your active directory application.
"""

import os
import asyncio


class AuthenticationSampleAsync(object):

    async def authentication_with_api_key_credential_async(self):
        print("\n.. authentication_with_api_key_credential_async")
        # [START create_ta_client_with_key_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))
        # [END create_ta_client_with_key_async]

        doc = [
            """
            I need to take my cat to the veterinarian. She's been coughing for a while and I thought it was just a hairball,
            but now I'm now worried it might be something else. She's still very healthy so I'm not too worried though.
            """
        ]
        async with text_analytics_client:
            result = await text_analytics_client.detect_language(doc)

        print("Language detected: {}".format(result[0].primary_language.name))
        print("Confidence score: {}".format(result[0].primary_language.confidence_score))

    async def authentication_with_azure_active_directory_async(self):
        """DefaultAzureCredential will use the values from these environment
        variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
        """
        print("\n.. authentication_with_azure_active_directory_async")
        # [START create_ta_client_with_aad_async]
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from azure.identity.aio import DefaultAzureCredential

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        credential = DefaultAzureCredential()

        text_analytics_client = TextAnalyticsClient(endpoint, credential=credential)
        # [END create_ta_client_with_aad_async]

        doc = [
            """
            I need to take my cat to the veterinarian. She's been coughing for a while and I thought it was just a hairball,
            but now I'm now worried it might be something else. She's still very healthy so I'm not too worried though.
            """
        ]
        async with text_analytics_client:
            result = await text_analytics_client.detect_language(doc)

        print("Language detected: {}".format(result[0].primary_language.name))
        print("Confidence score: {}".format(result[0].primary_language.confidence_score))


async def main():
    sample = AuthenticationSampleAsync()
    await sample.authentication_with_api_key_credential_async()
    await sample.authentication_with_azure_active_directory_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
