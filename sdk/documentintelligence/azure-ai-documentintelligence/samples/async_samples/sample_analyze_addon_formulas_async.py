# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_addon_formulas_async.py

DESCRIPTION:
    This sample demonstrates how to extract all identified formulas, such as mathematical
    equations, using the add-on 'FORMULAS' capability.

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
    python sample_analyze_addon_formulas_async.py

    Set the environment variables with your own values before running the sample:
    1) DOCUMENTINTELLIGENCE_ENDPOINT - the endpoint to your Document Intelligence resource.
    2) DOCUMENTINTELLIGENCE_API_KEY - your Document Intelligence API key.
"""

import asyncio
import os


def format_polygon(polygon):
    if not polygon:
        return "N/A"
    return ", ".join([f"[{polygon[i]}, {polygon[i + 1]}]" for i in range(0, len(polygon), 2)])


async def analyze_formulas():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "sample_forms/add_ons/formulas.pdf",
        )
    )
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult

    endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]

    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    async with document_intelligence_client:
        # Specify which add-on capabilities to enable
        with open(path_to_sample_documents, "rb") as f:
            poller = await document_intelligence_client.begin_analyze_document(
                "prebuilt-layout",
                body=f,
                features=[DocumentAnalysisFeature.FORMULAS],
            )
        result: AnalyzeResult = await poller.result()

    # Iterate over extracted formulas on each page and print inline and display formulas
    # separately.
    for page in result.pages:
        print(f"----Formulas detected from page #{page.page_number}----")
        if page.formulas:
            inline_formulas = [f for f in page.formulas if f.kind == "inline"]
            display_formulas = [f for f in page.formulas if f.kind == "display"]

            print(f"Detected {len(inline_formulas)} inline formulas.")
            for formula_idx, formula in enumerate(inline_formulas):
                print(f"- Inline #{formula_idx}: {formula.value}")
                print(f"  Confidence: {formula.confidence}")
                print(f"  Bounding regions: {format_polygon(formula.polygon)}")

            print(f"\nDetected {len(display_formulas)} display formulas.")
            for formula_idx, formula in enumerate(display_formulas):
                print(f"- Display #{formula_idx}: {formula.value}")
                print(f"  Confidence: {formula.confidence}")
                print(f"  Bounding regions: {format_polygon(formula.polygon)}")

    print("----------------------------------------")


async def main():
    await analyze_formulas()


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
