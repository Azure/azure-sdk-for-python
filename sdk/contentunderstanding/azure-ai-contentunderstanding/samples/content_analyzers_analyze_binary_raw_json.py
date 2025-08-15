# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: use the prebuilt-documentAnalyzer to extract content from a PDF and save raw JSON response.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python content_analyzers_analyze_binary_raw_json.py
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalyzeResult
from sample_helper import get_credential, save_json_to_file

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Extract content from PDF using begin_analyze_binary API and save raw JSON
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Read a PDF file from disk
# 3. Analyze the document using begin_analyze_binary with prebuilt-documentAnalyzer
# 4. Save the raw JSON response to a file using poller callback
#
# IMPORTANT NOTES:
# - The SDK returns analysis results with an object model, which is easier to navigate and retrieve
#   the desired results compared to parsing raw JSON
# - This sample is ONLY for demonstration purposes to show how to access raw JSON responses
# - For production use, prefer the object model approach shown in:
#   - content_analyzers_analyze_binary.py
#   - content_analyzers_analyze_url.py

async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    credential = get_credential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
        with open("sample_files/sample_invoice.pdf", "rb") as f:
            pdf_bytes: bytes = f.read()

        print("🔍 Analyzing sample_files/sample_invoice.pdf with prebuilt-documentAnalyzer...")
        
        # Use poller callback to save raw JSON response
        # The 'cls' parameter allows us to intercept the response before it gets deserialized as an object model
        # We return a tuple: (deserialized_object, raw_http_response)
        poller = await client.content_analyzers.begin_analyze_binary(
            analyzer_id="prebuilt-documentAnalyzer",
            input=pdf_bytes,
            content_type="application/pdf",
            cls=lambda pipeline_response, deserialized_obj, response_headers: (deserialized_obj, pipeline_response.http_response)
        )
        
        # Wait for completion and get both model and raw HTTP response
        _, raw_http_response = await poller.result()
        
        # Save the raw JSON response
        save_json_to_file(raw_http_response.json(), "content_analyzers_analyze_binary")
        # Note: For easier data access, see object model samples: 
        #    content_analyzers_analyze_binary.py
        #    content_analyzers_analyze_url.py

        print("✅ Analysis completed and raw JSON response saved!")


if __name__ == "__main__":
    asyncio.run(main())
