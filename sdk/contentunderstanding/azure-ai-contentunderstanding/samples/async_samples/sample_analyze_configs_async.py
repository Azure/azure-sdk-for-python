# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_configs_async.py

DESCRIPTION:
    This sample demonstrates how to extract additional features from documents such as charts,
    hyperlinks, formulas, and annotations using the prebuilt-documentSearch analyzer.

    The prebuilt-documentSearch analyzer has the following configurations enabled by default:
    - ReturnDetails: true - Returns detailed information about document elements
    - EnableOcr: true - Performs OCR on documents
    - EnableLayout: true - Extracts layout information (tables, figures, hyperlinks, annotations)
    - EnableFormula: true - Extracts mathematical formulas from documents
    - EnableFigureDescription: true - Generates descriptions for figures
    - EnableFigureAnalysis: true - Analyzes figures including charts
    - ChartFormat: "chartjs" - Chart figures are returned in Chart.js format
    - TableFormat: "html" - Tables are returned in HTML format
    - AnnotationFormat: "markdown" - Annotations are returned in markdown format

    The following code snippets demonstrate extraction of features enabled by these configs:
    - Charts: Enabled by EnableFigureAnalysis - Chart figures with Chart.js configuration
    - Hyperlinks: Enabled by EnableLayout - URLs and links found in the document
    - Formulas: Enabled by EnableFormula - Mathematical formulas in LaTeX format
    - Annotations: Enabled by EnableLayout - PDF annotations, comments, and markup

    For custom analyzers, you can configure these options in ContentAnalyzerConfig when creating
    the analyzer.

USAGE:
    python sample_analyze_configs_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_configure_defaults.py for setup instructions.
"""

import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeResult,
    DocumentContent,
    DocumentChartFigure,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # [START analyze_with_configs]
        file_path = "sample_files/sample_document_features.pdf"

        with open(file_path, "rb") as f:
            pdf_bytes = f.read()

        print(f"Analyzing {file_path} with prebuilt-documentSearch...")
        print("Note: prebuilt-documentSearch has formulas, layout, and OCR enabled by default.")

        # Analyze with prebuilt-documentSearch which has formulas, layout, and OCR enabled
        poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=pdf_bytes,
        )
        result: AnalyzeResult = await poller.result()
        # [END analyze_with_configs]

        # [START extract_charts]
        # Extract charts from document content (enabled by EnableFigureAnalysis config)
        document_content: DocumentContent = result.contents[0]  # type: ignore
        if document_content.figures:
            for figure in document_content.figures:
                if isinstance(figure, DocumentChartFigure):
                    print(f"  Chart ID: {figure.id}")
                    print(f"    Description: {figure.description or '(not available)'}")
                    print(f"    Caption: {figure.caption.content if figure.caption else '(not available)'}")
        # [END extract_charts]

        # [START extract_hyperlinks]
        # Extract hyperlinks from document content (enabled by EnableLayout config)
        doc_content: DocumentContent = result.contents[0]  # type: ignore
        print(f"Found {len(doc_content.hyperlinks) if doc_content.hyperlinks else 0} hyperlink(s)")
        for hyperlink in doc_content.hyperlinks or []:
            print(f"  URL: {hyperlink.url or '(not available)'}")
            print(f"    Content: {hyperlink.content or '(not available)'}")
        # [END extract_hyperlinks]

        # [START extract_formulas]
        # Extract formulas from document pages (enabled by EnableFormula config)
        content: DocumentContent = result.contents[0]  # type: ignore
        all_formulas = []
        for page in content.pages or []:
            all_formulas.extend(page.formulas or [])

        print(f"Found {len(all_formulas)} formula(s)")
        for formula in all_formulas:
            print(f"  Formula Kind: {formula.kind}")
            print(f"    LaTeX: {formula.value or '(not available)'}")
            print(f"    Confidence: {f'{formula.confidence:.2f}' if formula.confidence else 'N/A'}")
        # [END extract_formulas]

        # [START extract_annotations]
        # Extract annotations from document content (enabled by EnableLayout config)
        document: DocumentContent = result.contents[0]  # type: ignore
        print(f"Found {len(document.annotations) if document.annotations else 0} annotation(s)")
        for annotation in document.annotations or []:
            print(f"  Annotation ID: {annotation.id}")
            print(f"    Kind: {annotation.kind}")
            print(f"    Author: {annotation.author or '(not available)'}")
            print(f"    Comments: {len(annotation.comments) if annotation.comments else 0}")
            for comment in annotation.comments or []:
                print(f"      - {comment.message}")
        # [END extract_annotations]

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
