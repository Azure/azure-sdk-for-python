# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: Create a classifier to categorize financial documents with automatic page segmentation.

This sample demonstrates how to:
1. Create a custom analyzer with content categories for document classification
2. Enable automatic page segmentation by category (enable_segment=True)
3. Classify documents into categories (Invoice, Bank Statement, Loan Application)
4. View classification results with automatic segmentation - pages are automatically grouped by category
5. Clean up resources

The key feature of this sample is the enable_segment=True option, which allows the analyzer to
automatically segment multi-page documents by their category. For example, if a document contains
both an invoice and a bank statement, each will be identified as separate segments with their
respective categories and page ranges.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python analyze_category_enable_segments.py
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from typing import cast

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeResult,
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentCategoryDefinition,
    DocumentContent,
    MediaContentKind,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    print(f"Using endpoint: {endpoint}\n")
    
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    print("Environment Variables:")
    print("=" * 50)
    print(f"AZURE_CONTENT_UNDERSTANDING_ENDPOINT: {endpoint}")
    print(f"AZURE_CONTENT_UNDERSTANDING_KEY: {'***' if key else '(not set, using DefaultAzureCredential)'}")
    print("=" * 50)

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # Create a unique analyzer ID
        analyzer_id = f"financial_doc_classifier_{int(asyncio.get_event_loop().time())}"
        
        print(f"\nCreating analyzer '{analyzer_id}'...")
        print("Categories: Invoice, Bank Statement, Loan Application")
        print("Note: enable_segment=True allows automatic page segmentation by category\n")

        # Create an analyzer with content categories for document classification
        # enable_segment=True enables automatic segmentation of pages by their category
        content_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            config=ContentAnalyzerConfig(
                return_details=True,
                content_categories={
                    "Loan application": ContentCategoryDefinition(
                        description="Documents submitted by individuals or businesses to request funding, typically including personal or business details, financial history, loan amount, purpose, and supporting documentation."
                    ),
                    "Invoice": ContentCategoryDefinition(
                        description="Billing documents issued by sellers or service providers to request payment for goods or services, detailing items, prices, taxes, totals, and payment terms."
                    ),
                    "Bank Statement": ContentCategoryDefinition(
                        description="Official statements issued by banks that summarize account activity over a period, including deposits, withdrawals, fees, and balances."
                    ),
                },
                enable_segment=True,  # Enable automatic page segmentation by category
            ),
            description=f"Custom analyzer for financial document categorization with automatic segmentation",
            models={"completion": "gpt-4.1"},
            tags={"demo_type": "category_classification_with_segmentation"},
        )

        # Create the analyzer
        poller = await client.begin_create_analyzer(
            analyzer_id=analyzer_id,
            resource=content_analyzer,
        )

        print("Waiting for analyzer creation to complete...")
        result = await poller.result()
        print(f"✅ Analyzer '{analyzer_id}' created successfully!\n")

        if result.warnings:
            print("⚠️  Warnings encountered while building the analyzer:")
            for warning in result.warnings:
                print(f"  - {warning}")
            print()

        # Test files to classify
        # Note: With enable_segment=True, documents will be automatically segmented by category.
        # mixed_financial_docs.pdf contains multiple document types (invoice, bank statement, etc.)
        # and will be automatically split into separate segments based on content category.
        test_files = [
            "sample_invoice.pdf",  # Single category
            "sample_bank_statement.pdf",  # Single category
            "mixed_financial_docs.pdf",  # Will be auto-segmented into multiple categories
        ]

        samples_dir = os.path.dirname(__file__)
        output_dir = os.path.join(samples_dir, "sample_output")
        os.makedirs(output_dir, exist_ok=True)

        # Classify each document
        for test_file in test_files:
            test_file_path = os.path.join(samples_dir, "sample_files", test_file)
            
            if not os.path.exists(test_file_path):
                print(f"⚠️  Skipping {test_file} - file not found")
                continue

            print(f"{'=' * 60}")
            print(f"📄 Analyzing: {test_file}")
            print(f"{'=' * 60}")

            # Read and analyze the document
            with open(test_file_path, "rb") as f:
                pdf_bytes = f.read()

            analyze_poller = await client.begin_analyze_binary(
                analyzer_id=analyzer_id,
                binary_input=pdf_bytes,
                content_type="application/pdf",
            )
            
            analyze_result: AnalyzeResult = await analyze_poller.result()
            print("✅ Classification completed!\n")

            # Display classification results
            print("📊 Classification Results (with automatic segmentation):")
            print("-" * 60)
            
            for content in analyze_result.contents:
                if content.kind == MediaContentKind.DOCUMENT:
                    document_content: DocumentContent = cast(DocumentContent, content)
                    
                    # Display segments with their categories
                    # When enable_segment=True, pages are automatically grouped by category
                    if document_content.segments:
                        print(f"\nFound {len(document_content.segments)} segment(s):")
                        for i, segment in enumerate(document_content.segments, 1):
                            print(f"\n  Segment {i}:")
                            print(f"    Category: {segment.category}")
                            print(f"    Pages: {segment.start_page_number}-{segment.end_page_number}")
                            print(f"    Segment ID: {segment.segment_id}")
                    else:
                        # Fallback if no segments (shouldn't happen with enable_segment=True)
                        print(f"\n⚠️  No segments found for this document")
                        print(f"  Pages: {document_content.start_page_number}-{document_content.end_page_number}")

            print()

            # Save results to JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_filename = f"analyze_category_segments_{test_file.replace('.pdf', '')}_{timestamp}.json"
            result_file = os.path.join(output_dir, result_filename)
            
            with open(result_file, "w") as f:
                json.dump(analyze_result.as_dict(), f, indent=2, default=str)
            
            print(f"💾 Results saved to: {result_file}\n")

        # Cleanup
        print(f"{'=' * 60}")
        print(f"🗑️  Deleting analyzer '{analyzer_id}' (demo cleanup)...")
        await client.delete_analyzer(analyzer_id=analyzer_id)
        print(f"✅ Analyzer '{analyzer_id}' deleted successfully!")
        print(f"{'=' * 60}")

    # Close DefaultAzureCredential if used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
