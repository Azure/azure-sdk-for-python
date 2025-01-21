# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_addon_barcodes.py

DESCRIPTION:
    This sample demonstrates how to extract all identified barcodes using the
    add-on 'BARCODES' capability.

    This sample uses Layout model to demonstrate.

    Add-on capabilities accept a list of strings containing values from the `DocumentAnalysisFeature`
    enum class. For more information, see:
    https://aka.ms/azsdk/python/documentintelligence/analysisfeature.

    The following capabilities are free:
    - BARCODES
    - LANGUAGES

    The following capabilities will incur additional charges:
    - FORMULAS
    - OCR_HIGH_RESOLUTION
    - STYLE_FONT
    - QUERY_FIELDS

    See pricing: https://azure.microsoft.com/pricing/details/ai-document-intelligence/.

USAGE:
    python sample_analyze_addon_barcodes.py

    Set the environment variables with your own values before running the sample:
    1) DOCUMENTINTELLIGENCE_ENDPOINT - the endpoint to your Document Intelligence resource.
    2) DOCUMENTINTELLIGENCE_API_KEY - your Document Intelligence API key.
"""

import os


def analyze_barcodes():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "sample_forms/add_ons/barcodes.jpg",
        )
    )
    # [START analyze_barcodes]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult

    endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]

    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Specify which add-on capabilities to enable.
    with open(path_to_sample_documents, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout",
            body=f,
            features=[DocumentAnalysisFeature.BARCODES],
        )
    result: AnalyzeResult = poller.result()

    # Iterate over extracted barcodes on each page.
    for page in result.pages:
        print(f"----Barcodes detected from page #{page.page_number}----")
        if page.barcodes:
            print(f"Detected {len(page.barcodes)} barcodes:")
            for barcode_idx, barcode in enumerate(page.barcodes):
                print(f"- Barcode #{barcode_idx}: {barcode.value}")
                print(f"  Kind: {barcode.kind}")
                print(f"  Confidence: {barcode.confidence}")
                if not barcode.polygon:
                    print("  Bounding regions: N/A")
                else:
                    print("  Bounding regions: ")
                    print(
                        ", ".join(
                            [
                                f"[{barcode.polygon[i]}, {barcode.polygon[i + 1]}]"
                                for i in range(0, len(barcode.polygon), 2)
                            ]
                        )
                    )

    print("----------------------------------------")
    # [END analyze_barcodes]


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError
    from dotenv import find_dotenv, load_dotenv

    try:
        load_dotenv(find_dotenv())
        analyze_barcodes()
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
