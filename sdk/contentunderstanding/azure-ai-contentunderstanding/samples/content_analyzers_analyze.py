# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: use the prebuilt-documentAnalyzer to extract content from a URL.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # or set AZURE_CONTENT_UNDERSTANDING_KEY

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - falls back to DefaultAzureCredential)

Run:
    python content_analyzers_analyze.py
"""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from sample_helper import get_credential, save_response_to_file

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Extract content from URL using begin_analyze API
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Analyze a document from a remote URL using begin_analyze with prebuilt-documentAnalyzer
# 3. Save the full analysis result to a JSON file

async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    credential = get_credential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
        url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"
        print(f"🔍 Analyzing remote document from {url} with prebuilt-documentAnalyzer...")
        poller = await client.content_analyzers.begin_analyze(
            analyzer_id="prebuilt-documentAnalyzer",
            body={
                "url": url,
            },
        )
        result = await poller.result()
        save_response_to_file(result, filename_prefix="content_analyzers_analyze")


if __name__ == "__main__":
    asyncio.run(main())
