# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication_async.py

DESCRIPTION:
    This sample demonstrates how to authenticate to the Document Translation service.

    There is currently only one supported method of authentication:
    1) Use a Document Translation API key with AzureKeyCredential from azure.core.credentials


USAGE:
    python sample_authentication_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Form Recognizer API key
"""

import os
import asyncio


async def sample_authentication_api_key_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documenttranslation.aio import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    document_translation_client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    # make calls with authenticated client
    async with document_translation_client:
        result = await document_translation_client.get_document_formats()


async def main():
    await sample_authentication_api_key_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
