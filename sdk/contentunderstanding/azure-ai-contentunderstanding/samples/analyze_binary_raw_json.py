# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: use the prebuilt-documentSearch to extract content from a PDF and save raw JSON response.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python analyze_binary_raw_json.py
"""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalyzeResult
from sample_helper import save_json_to_file
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Extract content from PDF using begin_analyze_binary API and save raw JSON
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Read a PDF file from disk
# 3. Analyze the document using begin_analyze_binary with prebuilt-documentSearch
# 4. Save the raw JSON response to a file using a customized callback in poller parameter
#
# prebuilt-documentSearch is an AI-enhanced analyzer that extends prebuilt-document with:
# - Document summarization: Returns a "Summary" field with AI-generated document summaries
# - Figure analysis: Extracts descriptions and analyzes figures in documents (enableFigureDescription, enableFigureAnalysis)
# - Enhanced output: Provides more detailed analysis results (returnDetails: true)
# - AI completion model: Uses gpt-4.1-mini for intelligent content extraction
#
# IMPORTANT NOTES:
# - The SDK returns analysis results with an object model, which is easier to navigate and retrieve
#   the desired results compared to parsing raw JSON
# - This sample is ONLY for demonstration purposes to show how to access raw JSON responses
# - For production use, prefer the object model approach shown in:
#   - analyze_binary.py
#   - analyze_url.py


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        with open("sample_files/sample_invoice.pdf", "rb") as f:
            pdf_bytes: bytes = f.read()

        print("Analyzing sample_files/sample_invoice.pdf with prebuilt-documentSearch...")

        # Use poller callback to save raw JSON response
        # The 'cls' parameter allows us to intercept the response before it gets deserialized as an object model
        # We return a tuple: (deserialized_object, raw_http_response)
        poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=pdf_bytes,
            content_type="application/pdf",
            cls=lambda pipeline_response, deserialized_obj, response_headers: (
                deserialized_obj,
                pipeline_response.http_response,
            ),
        )

        # Wait for completion and get both model and raw HTTP response
        _, raw_http_response = await poller.result()

        # Save the raw JSON response
        save_json_to_file(raw_http_response.json(), filename_prefix="analyze_binary_raw_json")  # type: ignore[attr-defined]
        # Note: For easier data access, see object model samples:
        #    analyze_binary.py
        #    analyze_url.py

        print("Analysis completed and raw JSON response saved!")

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())

