# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_configs.py

DESCRIPTION:
    This sample demonstrates how to extract additional features from documents such as charts,
    hyperlinks, formulas, and annotations using the prebuilt-documentSearch analyzer.

    The prebuilt-documentSearch analyzer has the following configurations enabled by default:
    - EnableFormula: Extracts mathematical formulas from documents
    - EnableLayout: Extracts layout information (tables, figures, etc.)
    - EnableOcr: Performs OCR on documents

    These configs enable extraction of:
    - Charts: Chart figures with Chart.js configuration
    - Hyperlinks: URLs and links found in the document
    - Formulas: Mathematical formulas in LaTeX format
    - Annotations: PDF annotations, comments, and markup

USAGE:
    python sample_analyze_configs.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_configure_defaults.py for setup instructions.
"""

import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeResult,
    DocumentContent,
    MediaContentKind,
    DocumentChartFigure,
    DocumentFigureKind,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # [START analyze_with_configs]
    file_path = "sample_files/sample_invoice.pdf"

    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    print(f"Analyzing {file_path} with prebuilt-documentSearch...")
    print("Note: prebuilt-documentSearch has formulas, layout, and OCR enabled by default.")

    # Analyze with prebuilt-documentSearch which has formulas, layout, and OCR enabled
    poller = client.begin_analyze_binary(
        analyzer_id="prebuilt-documentSearch",
        binary_input=pdf_bytes,
    )
    result: AnalyzeResult = poller.result()
    # [END analyze_with_configs]

    # [START extract_charts]
    if result.contents and len(result.contents) > 0:
        content = result.contents[0]

        if content.kind == MediaContentKind.DOCUMENT:
            document_content: DocumentContent = content  # type: ignore

            if document_content.figures and len(document_content.figures) > 0:
                # Filter for chart figures
                chart_figures = [
                    f for f in document_content.figures
                    if isinstance(f, DocumentChartFigure) or (hasattr(f, 'kind') and f.kind == DocumentFigureKind.CHART)
                ]

                print(f"\nFound {len(chart_figures)} chart(s)")
                for chart in chart_figures:
                    print(f"  Chart ID: {chart.id}")
                    if hasattr(chart, 'description') and chart.description:
                        print(f"    Description: {chart.description}")
                    if hasattr(chart, 'caption') and chart.caption and chart.caption.content:
                        print(f"    Caption: {chart.caption.content}")
            else:
                print("\nNo figures found in the document.")
    else:
        print("\nNo content found in the analysis result.")
    # [END extract_charts]

    # [START extract_hyperlinks]
    if result.contents and len(result.contents) > 0:
        content = result.contents[0]

        if content.kind == MediaContentKind.DOCUMENT:
            document_content: DocumentContent = content  # type: ignore

            if document_content.hyperlinks and len(document_content.hyperlinks) > 0:
                print(f"\nFound {len(document_content.hyperlinks)} hyperlink(s)")
                for hyperlink in document_content.hyperlinks:
                    print(f"  URL: {hyperlink.url or '(not available)'}")
                    print(f"    Content: {hyperlink.content or '(not available)'}")
            else:
                print("\nNo hyperlinks found in the document.")
    # [END extract_hyperlinks]

    # [START extract_formulas]
    if result.contents and len(result.contents) > 0:
        content = result.contents[0]

        if content.kind == MediaContentKind.DOCUMENT:
            document_content: DocumentContent = content  # type: ignore

            all_formulas = []
            if document_content.pages:
                for page in document_content.pages:
                    if hasattr(page, 'formulas') and page.formulas:
                        all_formulas.extend(page.formulas)

            if len(all_formulas) > 0:
                print(f"\nFound {len(all_formulas)} formula(s)")
                for formula in all_formulas:
                    print(f"  Formula: {formula.value or '(no value)'}")
                    if hasattr(formula, 'kind') and formula.kind:
                        print(f"    Kind: {formula.kind}")
            else:
                print("\nNo formulas found in the document.")
    # [END extract_formulas]

    # Extract annotations
    if result.contents and len(result.contents) > 0:
        content = result.contents[0]

        if content.kind == MediaContentKind.DOCUMENT:
            document_content: DocumentContent = content  # type: ignore

            if hasattr(document_content, 'annotations') and document_content.annotations and len(document_content.annotations) > 0:
                print(f"\nFound {len(document_content.annotations)} annotation(s)")
                for annotation in document_content.annotations:
                    print(f"  Kind: {annotation.kind or '(unknown)'}")
                    if hasattr(annotation, 'content') and annotation.content:
                        print(f"    Content: {annotation.content}")
            else:
                print("\nNo annotations found in the document.")


if __name__ == "__main__":
    main()
