# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_identity_documents_async.py

DESCRIPTION:
    This sample demonstrates how to analyze an identity document.

    See fields found on identity documents here:
    https://aka.ms/azsdk/formrecognizer/iddocumentfieldschema

USAGE:
    python sample_analyze_identity_documents_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import asyncio


async def analyze_identity_documents_async():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "..",
            "./sample_forms/id_documents/license.jpg",
        )
    )

    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer.aio import DocumentAnalysisClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    async with document_analysis_client:
        with open(path_to_sample_documents, "rb") as f:
            poller = await document_analysis_client.begin_analyze_document(
                "prebuilt-idDocument", document=f
            )
        id_documents = await poller.result()

    for idx, id_document in enumerate(id_documents.documents):
        print(f"--------Analyzing ID document #{idx + 1}--------")
        first_name = id_document.fields.get("FirstName")
        if first_name:
            print(
                f"First Name: {first_name.value} has confidence: {first_name.confidence}"
            )
        last_name = id_document.fields.get("LastName")
        if last_name:
            print(
                f"Last Name: {last_name.value} has confidence: {last_name.confidence}"
            )
        document_number = id_document.fields.get("DocumentNumber")
        if document_number:
            print(
                f"Document Number: {document_number.value} has confidence: {document_number.confidence}"
            )
        dob = id_document.fields.get("DateOfBirth")
        if dob:
            print(f"Date of Birth: {dob.value} has confidence: {dob.confidence}")
        doe = id_document.fields.get("DateOfExpiration")
        if doe:
            print(f"Date of Expiration: {doe.value} has confidence: {doe.confidence}")
        sex = id_document.fields.get("Sex")
        if sex:
            print(f"Sex: {sex.value} has confidence: {sex.confidence}")
        address = id_document.fields.get("Address")
        if address:
            print(f"Address: {address.value} has confidence: {address.confidence}")
        country_region = id_document.fields.get("CountryRegion")
        if country_region:
            print(
                f"Country/Region: {country_region.value} has confidence: {country_region.confidence}"
            )
        region = id_document.fields.get("Region")
        if region:
            print(f"Region: {region.value} has confidence: {region.confidence}")


async def main():
    await analyze_identity_documents_async()


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError

    try:
        asyncio.run(main())
    except HttpResponseError as error:
        print(
            "For more information about troubleshooting errors, see the following guide: "
            "https://aka.ms/azsdk/python/formrecognizer/troubleshooting"
        )
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
