# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_documents_output_in_markdown_async.py

DESCRIPTION:
    This sample demonstrates how to analyze an document in markdown output format.

USAGE:
    python sample_analyze_documents_output_in_markdown_async.py

    Set the environment variables with your own values before running the sample:
    1) DOCUMENTINTELLIGENCE_ENDPOINT - the endpoint to your Document Intelligence resource.
    2) DOCUMENTINTELLIGENCE_API_KEY - your Document Intelligence API key.
"""

import asyncio
import os


async def analyze_documents_output_in_markdown():
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentContentFormat, AnalyzeResult

    endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
    url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/documentintelligence/azure-ai-documentintelligence/samples/sample_forms/forms/Invoice_1.pdf"

    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    async with document_intelligence_client:
        poller = await document_intelligence_client.begin_analyze_document(
            "prebuilt-layout",
            AnalyzeDocumentRequest(url_source=url),
            output_content_format=DocumentContentFormat.MARKDOWN,
        )
        result: AnalyzeResult = await poller.result()

    print(f"Here's the full content in format {result.content_format}:\n")
    print(result.content)


async def main():
    await analyze_documents_output_in_markdown()


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError
    from dotenv import find_dotenv, load_dotenv

    try:
        load_dotenv(find_dotenv())
        asyncio.run(main())
    except HttpResponseError as error:
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
            # Raise the error again after printing it
            raise
        # If the inner error is None and then it is possible to check the message to get more information:
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Uh-oh! Seems there was an invalid request: {error}")
        # Raise the error again
        raise
