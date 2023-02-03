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
    https://aka.ms/azsdk/formrecognizer/iddocumentfieldschema

USAGE:
    python sample_analyze_identity_documents.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os


def analyze_identity_documents():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "./sample_forms/id_documents/license.jpg",
        )
    )

    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    with open(path_to_sample_documents, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-idDocument", document=f
        )
    id_documents = poller.result()

    for idx, id_document in enumerate(id_documents.documents):
        print("--------Analyzing ID document #{}--------".format(idx + 1))
        first_name = id_document.fields.get("FirstName")
        if first_name:
            print(
                "First Name: {} has confidence: {}".format(
                    first_name.value, first_name.confidence
                )
            )
        last_name = id_document.fields.get("LastName")
        if last_name:
            print(
                "Last Name: {} has confidence: {}".format(
                    last_name.value, last_name.confidence
                )
            )
        document_number = id_document.fields.get("DocumentNumber")
        if document_number:
            print(
                "Document Number: {} has confidence: {}".format(
                    document_number.value, document_number.confidence
                )
            )
        dob = id_document.fields.get("DateOfBirth")
        if dob:
            print(
                "Date of Birth: {} has confidence: {}".format(dob.value, dob.confidence)
            )
        doe = id_document.fields.get("DateOfExpiration")
        if doe:
            print(
                "Date of Expiration: {} has confidence: {}".format(
                    doe.value, doe.confidence
                )
            )
        sex = id_document.fields.get("Sex")
        if sex:
            print("Sex: {} has confidence: {}".format(sex.value, sex.confidence))
        address = id_document.fields.get("Address")
        if address:
            print(
                "Address: {} has confidence: {}".format(
                    address.value, address.confidence
                )
            )
        country_region = id_document.fields.get("CountryRegion")
        if country_region:
            print(
                "Country/Region: {} has confidence: {}".format(
                    country_region.value, country_region.confidence
                )
            )
        region = id_document.fields.get("Region")
        if region:
            print(
                "Region: {} has confidence: {}".format(region.value, region.confidence)
            )


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError
    try:
        analyze_identity_documents()
    except HttpResponseError as error:
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
                sys.exit(1)
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
                sys.exit(1)
        # If the inner error is None and then it is possible to check the message to get more information:
        filter_msg = ["Generic error", "Timeout", "Invalid request", "InvalidImage"]
        if any(example_error.casefold() in error.message.casefold() for example_error in filter_msg):
            print(f"Uh-oh! Something unexpected happened: {error}")
            sys.exit(1)
        # Print the full error content:
        print(f"Full HttpResponseError: {error}")
