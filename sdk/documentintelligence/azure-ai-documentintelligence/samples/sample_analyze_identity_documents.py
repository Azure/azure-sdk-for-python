# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_identity_documents.py

DESCRIPTION:
    This sample demonstrates how to analyze an identity document.

    See fields found on identity documents here:
    https://aka.ms/azsdk/documentintelligence/iddocumentfieldschema

USAGE:
    python sample_analyze_identity_documents.py

    Set the environment variables with your own values before running the sample:
    1) DOCUMENTINTELLIGENCE_ENDPOINT - the endpoint to your Document Intelligence resource.
    2) DOCUMENTINTELLIGENCE_API_KEY - your Document Intelligence API key.
"""

import os


def analyze_identity_documents():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "./sample_forms/id_documents/license.jpg",
        )
    )

    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeResult

    endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]

    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    with open(path_to_sample_documents, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document("prebuilt-idDocument", body=f)
    id_documents: AnalyzeResult = poller.result()

    if id_documents.documents:
        for idx, id_document in enumerate(id_documents.documents):
            print(f"--------Analyzing ID document #{idx + 1}--------")
            if id_document.fields:
                first_name = id_document.fields.get("FirstName")
                if first_name:
                    print(f"First Name: {first_name.get('valueString')} has confidence: {first_name.confidence}")
                last_name = id_document.fields.get("LastName")
                if last_name:
                    print(f"Last Name: {last_name.get('valueString')} has confidence: {last_name.confidence}")
                document_number = id_document.fields.get("DocumentNumber")
                if document_number:
                    print(
                        f"Document Number: {document_number.get('valueString')} has confidence: {document_number.confidence}"
                    )
                dob = id_document.fields.get("DateOfBirth")
                if dob:
                    print(f"Date of Birth: {dob.get('valueDate')} has confidence: {dob.confidence}")
                doe = id_document.fields.get("DateOfExpiration")
                if doe:
                    print(f"Date of Expiration: {doe.get('valueDate')} has confidence: {doe.confidence}")
                sex = id_document.fields.get("Sex")
                if sex:
                    print(f"Sex: {sex.get('valueString')} has confidence: {sex.confidence}")
                address = id_document.fields.get("Address")
                if address:
                    print(f"Address: {address.get('valueString')} has confidence: {address.confidence}")
                country_region = id_document.fields.get("CountryRegion")
                if country_region:
                    print(
                        f"Country/Region: {country_region.get('valueCountryRegion')} has confidence: {country_region.confidence}"
                    )
                region = id_document.fields.get("Region")
                if region:
                    print(f"Region: {region.get('valueString')} has confidence: {region.confidence}")


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError
    from dotenv import find_dotenv, load_dotenv

    try:
        load_dotenv(find_dotenv())
        analyze_identity_documents()
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
