# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: demonstrate additional features on prebuilt-documentSearch to show results for charts, hyperlinks, and PDF annotations from PDF.

This sample demonstrates the additional features available in the prebuilt-documentSearch analyzer:
- Charts: Extraction and analysis of charts from PDF documents
- Hyperlinks: Detection and extraction of hyperlinks in PDF documents
- PDF Annotations: Detection and extraction of annotations (highlights, comments, etc.) from PDF documents

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python analyze_binary_features.py
"""

from __future__ import annotations

import asyncio
import json
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeResult,
    MediaContent,
    DocumentContent,
    MediaContentKind,
    DocumentChartFigure,
    DocumentFigureKind,
    DocumentAnnotation,
    DocumentAnnotationKind,
    DocumentHyperlink,
    DocumentFormula,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential
from sample_helper import save_json_to_file

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Demonstrate additional features on prebuilt-documentSearch
# ---------------------------------------------------------------------------
# This sample demonstrates additional features on prebuilt-documentSearch to show
# results for charts, hyperlinks, and PDF annotations from PDF documents.
#
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Read a PDF file from disk
# 3. Analyze the document using begin_analyze_binary with prebuilt-documentSearch
# 4. Extract and display chart information from figures
# 5. Extract and display annotation information
# 6. Extract and display hyperlink information
# 7. Extract and display formula information
#
# The prebuilt-documentSearch analyzer has the following additional features enabled:
# - enableFigureDescription: True - Enables figure descriptions
# - enableFigureAnalysis: True - Enables figure analysis including charts
# - chartFormat: 'chartjs' - Charts are represented as Chart.js config in the figure content
# - annotationFormat: 'markdown' - Enables annotation detection and represents annotations in markdown format
# - returnDetails: True - Returns detailed information including figures and annotations
# 
# Note: The analyzer also has other features enabled (enableOcr, enableLayout, enableFormula, etc.)
# but this sample focuses on demonstrating charts, hyperlinks, and PDF annotations.
#
# Charts are accessed via:
# - document_content.figures - List of all figures (including charts)
# - Filter figures where figure.kind == DocumentFigureKind.CHART to get charts
# - Each DocumentChartFigure has a 'content' property containing Chart.js configuration
# - Charts are also embedded in the markdown content based on chartFormat setting
#
# Annotations are accessed via:
# - document_content.annotations - List of all annotations in the document
# - Each DocumentAnnotation has properties like kind, spans, comments, author, etc.
# - Annotations are also represented in the markdown content based on annotationFormat setting
#
# Hyperlinks are accessed via:
# - document_content.hyperlinks - List of all hyperlinks in the document
# - Each DocumentHyperlink has properties like content (link text), url, span, source
# - Hyperlinks are also represented in the markdown content as [text](url) format


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # Read the sample_document_features.pdf file
        pdf_path = "sample_files/sample_document_features.pdf"
        with open(pdf_path, "rb") as f:
            pdf_bytes: bytes = f.read()

        print(f"Analyzing {pdf_path} with prebuilt-documentSearch...")
        print("This sample demonstrates additional features: charts, hyperlinks, and PDF annotations.")
        print()

        # Analyze the document using prebuilt-documentSearch
        # The analyzer config includes:
        # - enableFigureAnalysis: True (enables chart detection and analysis)
        # - chartFormat: 'chartjs' (charts represented as Chart.js config)
        # - annotationFormat: 'markdown' (enables annotation detection and represents annotations in markdown format)
        poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=pdf_bytes,
        )
        result: AnalyzeResult = await poller.result()

        # Get the document content from the analysis result
        content: MediaContent = result.contents[0]
        
        # Verify this is document content
        if content.kind != MediaContentKind.DOCUMENT:
            print("Error: Expected document content")
            return

        # Type assertion: we know this is DocumentContent for PDF files
        document_content: DocumentContent = content  # type: ignore

        print("=" * 80)
        print("DOCUMENT ANALYSIS RESULTS")
        print("=" * 80)
        print(f"Start page: {document_content.start_page_number}")
        print(f"End page: {document_content.end_page_number}")
        print(f"Total pages: {document_content.end_page_number - document_content.start_page_number + 1}")
        print()

        # =====================================================================
        # PART 1: EXTRACT AND DISPLAY CHARTS
        # =====================================================================
        # Charts are stored in document_content.figures
        # We need to filter for figures where kind == DocumentFigureKind.CHART
        # Each chart figure (DocumentChartFigure) contains:
        # - id: Unique identifier for the chart
        # - content: Chart.js configuration object (when chartFormat is 'chartjs')
        # - description: AI-generated description of the chart
        # - caption: Chart caption if present
        # - span: Location of the chart in the markdown content
        # - source: Position of the chart in the document
        print("=" * 80)
        print("CHARTS EXTRACTION")
        print("=" * 80)
        
        if document_content.figures:
            # Filter for chart figures
            # Charts are a subtype of DocumentFigure with kind == DocumentFigureKind.CHART
            # We can check the kind property or use isinstance with DocumentChartFigure
            chart_figures = [
                figure for figure in document_content.figures 
                if isinstance(figure, DocumentChartFigure) or 
                (hasattr(figure, 'kind') and figure.kind == DocumentFigureKind.CHART)
            ]
            
            print(f"Found {len(chart_figures)} chart(s) in the document")
            print()
            
            for i, figure in enumerate(chart_figures, 1):
                # Cast to DocumentChartFigure for type safety
                chart: DocumentChartFigure = figure  # type: ignore
                
                print(f"Chart {i}:")
                print(f"  ID: {chart.id}")
                print(f"  Source: {chart.source}")
                
                if chart.description:
                    print(f"  Description: {chart.description}")
                
                if chart.caption:
                    print(f"  Caption: {chart.caption.content}")
                
                if chart.span:
                    print(f"  Location in markdown: offset={chart.span.offset}, length={chart.span.length}")
                
                # The chart content contains Chart.js configuration
                # This is a JSON object that can be used with Chart.js library to render the chart
                if chart.content:
                    print(f"  Chart.js Config:")
                    print(f"  {json.dumps(chart.content, indent=4, default=str)}")
                
                print()
        else:
            print("No figures found in the document")
            print()

        # =====================================================================
        # PART 2: EXTRACT AND DISPLAY ANNOTATIONS
        # =====================================================================
        # Annotations are stored in document_content.annotations
        # Each annotation (DocumentAnnotation) contains:
        # - id: Unique identifier for the annotation
        # - kind: Type of annotation (highlight, strikethrough, underline, italic, bold, circle, note)
        # - spans: List of content spans where the annotation appears
        # - comments: List of comments associated with the annotation
        # - author: Author of the annotation
        # - created_at: When the annotation was created
        # - tags: Tags associated with the annotation
        print("=" * 80)
        print("ANNOTATIONS EXTRACTION")
        print("=" * 80)
        
        if document_content.annotations:
            print(f"Found {len(document_content.annotations)} annotation(s) in the document")
            print()
            
            for i, annotation in enumerate(document_content.annotations, 1):
                print(f"Annotation {i}:")
                print(f"  ID: {annotation.id}")
                print(f"  Kind: {annotation.kind}")
                
                if annotation.spans:
                    print(f"  Spans ({len(annotation.spans)}):")
                    for span in annotation.spans:
                        print(f"    - offset={span.offset}, length={span.length}")
                
                if annotation.comments:
                    print(f"  Comments ({len(annotation.comments)}):")
                    for comment in annotation.comments:
                        print(f"    - {comment.message}")
                
                if annotation.author:
                    print(f"  Author: {annotation.author}")
                
                if annotation.created_at:
                    print(f"  Created at: {annotation.created_at}")
                
                if annotation.tags:
                    print(f"  Tags: {annotation.tags}")
                
                if annotation.source:
                    print(f"  Source: {annotation.source}")
                
                print()
        else:
            print("No annotations found in the document")
            print()

        # =====================================================================
        # PART 3: EXTRACT AND DISPLAY HYPERLINKS
        # =====================================================================
        # Hyperlinks are stored in document_content.hyperlinks
        # Each hyperlink (DocumentHyperlink) contains:
        # - content: The text/content that is hyperlinked
        # - url: The URL of the hyperlink
        # - span: Location of the hyperlink in the markdown content
        # - source: Position of the hyperlink in the document
        print("=" * 80)
        print("HYPERLINKS EXTRACTION")
        print("=" * 80)
        
        if document_content.hyperlinks:
            print(f"Found {len(document_content.hyperlinks)} hyperlink(s) in the document")
            print()
            
            for i, hyperlink in enumerate(document_content.hyperlinks, 1):
                print(f"Hyperlink {i}:")
                print(f"  Content: {hyperlink.content}")
                print(f"  URL: {hyperlink.url}")
                
                if hyperlink.span:
                    print(f"  Location in markdown: offset={hyperlink.span.offset}, length={hyperlink.span.length}")
                
                if hyperlink.source:
                    print(f"  Source: {hyperlink.source}")
                
                print()
        else:
            print("No hyperlinks found in the document")
            print()

        # =====================================================================
        # PART 4: EXTRACT AND DISPLAY FORMULAS
        # =====================================================================
        # Formulas are stored in document_content.pages[].formulas (per page)
        # Each formula (DocumentFormula) contains:
        # - kind: Type of formula (inline or display)
        # - value: The LaTeX representation of the formula (may contain extra spaces)
        # - span: Location of the formula in the markdown content
        # - source: Position of the formula in the document
        # - confidence: Confidence of predicting the formula
        #
        # Note: The LaTeX value extracted from PDFs may have extra spaces between
        # commands and arguments (e.g., "\frac { 1 } { n }" instead of "\frac{1}{n}").
        # While this will still render correctly in most LaTeX processors, you may
        # want to clean it up for production use by removing extra spaces.
        print("=" * 80)
        print("FORMULAS EXTRACTION")
        print("=" * 80)
        
        # Collect all formulas from all pages
        all_formulas = []
        if document_content.pages:
            for page in document_content.pages:
                if page.formulas:
                    all_formulas.extend(page.formulas)
        
        if all_formulas:
            print(f"Found {len(all_formulas)} formula(s) in the document")
            print()
            print("Note: LaTeX values may contain extra spaces (e.g., '\\frac { 1 } { n }').")
            print("      This is expected from PDF extraction and will still render correctly.")
            print()
            
            for i, formula in enumerate(all_formulas, 1):
                print(f"Formula {i}:")
                print(f"  Kind: {formula.kind}")
                print(f"  LaTeX: {formula.value}")
                
                if formula.confidence:
                    print(f"  Confidence: {formula.confidence}")
                
                if formula.span:
                    print(f"  Location in markdown: offset={formula.span.offset}, length={formula.span.length}")
                
                if formula.source:
                    print(f"  Source: {formula.source}")
                
                print()
        else:
            print("No formulas found in the document")
            print()

        # =====================================================================
        # PART 5: MARKDOWN CONTENT
        # =====================================================================
        # The markdown content is also available in the result and contains embedded
        # representations of charts, annotations, hyperlinks, and formulas:
        # - Charts appear in markdown using image syntax: ![chart data](path "description")
        # - Annotations appear as markdown formatting (e.g., ==highlighted text== for highlights)
        # - Hyperlinks appear as [text](url) format
        # - Formulas appear as LaTeX syntax: $formula$ for inline, $$formula$$ for display
        # 
        # To see how to extract and display markdown content, see the analyze_binary.py sample.
        # The markdown can be accessed via: content.markdown or document_content.markdown
        print("=" * 80)
        print("MARKDOWN CONTENT")
        print("=" * 80)
        print("Note: Markdown content is available in the result and contains embedded")
        print("representations of charts, annotations, and hyperlinks.")
        print("See analyze_binary.py for how to extract and display markdown content.")
        print("=" * 80)
        print()

        # =====================================================================
        # PART 6: DUMP ANALYZE RESULT AS JSON
        # =====================================================================
        # Save the full AnalyzeResult as JSON for inspection
        # This includes all the data structures: contents, figures, annotations, etc.
        print()
        print("=" * 80)
        print("SAVING ANALYZE RESULT AS JSON")
        print("=" * 80)
        # Convert the result to a dictionary and save as JSON
        # This saves the object model, not the raw JSON response
        result_dict = result.as_dict()
        save_json_to_file(result_dict, filename_prefix="analyze_binary_features")
        print("=" * 80)

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())

