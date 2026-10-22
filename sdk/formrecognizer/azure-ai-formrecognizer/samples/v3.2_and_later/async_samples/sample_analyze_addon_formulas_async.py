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

    Add-on capabilities are available within all models except for the Business card
    model. This sample uses Layout model to demonstrate.

    Add-on capabilities accept a list of strings containing values from the `AnalysisFeature`
    enum class. For more information, see:
    https://learn.microsoft.com/en-us/python/api/azure-ai-formrecognizer/azure.ai.formrecognizer.analysisfeature?view=azure-python.

    The following capabilities are free:
    - BARCODES
    - LANGUAGES

    The following capabilities will incur additional charges:
    - FORMULAS
    - OCR_HIGH_RESOLUTION
    - STYLE_FONT

    See pricing: https://azure.microsoft.com/pricing/details/ai-document-intelligence/.

USAGE:
    python sample_analyze_addon_formulas_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import asyncio
import os


def format_bounding_region(bounding_regions):
    if not bounding_regions:
        return "N/A"
    return ", ".join(
        f"Page #{region.page_number}: {format_polygon(region.polygon)}"
        for region in bounding_regions
    )


def format_polygon(polygon):
    if not polygon:
        return "N/A"
    return ", ".join([f"[{p.x}, {p.y}]" for p in polygon])


async def analyze_formulas():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "..",
            "sample_forms/add_ons/formulas.pdf",
        )
    )
    # [START analyze_formulas]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import AnalysisFeature
    from azure.ai.formrecognizer.aio import DocumentAnalysisClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    async with document_analysis_client:
        # Specify which add-on capabilities to enable
        with open(path_to_sample_documents, "rb") as f:
            poller = await document_analysis_client.begin_analyze_document(
                "prebuilt-layout", document=f, features=[AnalysisFeature.FORMULAS]
            )
        result = await poller.result()

    # Iterate over extracted formulas on each page and print inline and display formulas
    # separately.
    for page in result.pages:
        print(f"----Formulas detected from page #{page.page_number}----")
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
    # [END analyze_formulas]


async def main():
    await analyze_formulas()


if __name__ == "__main__":
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
