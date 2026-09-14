# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_content_source.py

DESCRIPTION:
    This sample demonstrates how to read grounding source references from analysis results.
    When the service extracts a field value (for example a customer name or invoice total), it
    can also report where in the original content that value was found via ``ContentField.source``.

    In Python, sources are plain strings. Use the source string formats below to interpret
    document, image, audio, and visual locations.

    ## Source string formats

    Encoded sources use ``PREFIX(params)`` with multiple regions separated by ``;``:

    - Document/image: ``D(page,x1,y1,...,xN,yN)`` or page-only ``D(page)``
    - Audio/visual: ``AV(timeMs[,x,y,w,h])``

    Example multi-region document source::

        D(1,0.10,0.20,0.50,0.20,0.50,0.25,0.10,0.25);D(1,0.10,0.30,0.50,0.30,0.50,0.35,0.10,0.35)

    Coordinates use the document unit from ``DocumentContent.unit`` (often inches for US PDFs).

USAGE:
    python sample_content_source.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    See sample_update_defaults.py for model deployment setup guidance.
"""

import os
from typing import cast

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalysisInput, AnalysisResult, DocumentContent
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # [START content_source_from_analysis]
    # Analyze an invoice to get fields with grounding sources.
    invoice_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"

    print("Analyzing invoice and reading field grounding sources...")
    poller = client.begin_analyze(
        analyzer_id="prebuilt-invoice",
        inputs=[AnalysisInput(url=invoice_url)],
    )
    result: AnalysisResult = poller.result()
    document = cast(DocumentContent, result.contents[0])

    # Iterate over fields and print each grounding source string.
    # Sources identify where the field value appears in the original content.
    for field_name, field in (document.fields or {}).items():
        print(f"Field: {field_name} = {getattr(field, 'value', None)}")
        if field.source:
            # Keep the wire-format string as-is. Split only if you need each region separately.
            print(f"  Source: {field.source}")
            regions = [region.strip() for region in field.source.split(";") if region.strip()]
            if len(regions) > 1:
                print(f"  Regions: {len(regions)}")
                for index, region in enumerate(regions, start=1):
                    print(f"    [{index}] {region}")
    # [END content_source_from_analysis]


if __name__ == "__main__":
    main()
