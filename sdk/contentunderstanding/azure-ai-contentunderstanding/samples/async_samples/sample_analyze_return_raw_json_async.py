# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_return_raw_json_async.py

DESCRIPTION:
    This sample demonstrates how to access the raw JSON response from analysis operations
    using the 'cls' callback parameter (async version). This is useful for scenarios where
    you need to inspect the full response structure exactly as returned by the service.

    The Content Understanding SDK provides a convenient object model approach (shown in
    sample_analyze_binary_async.py) that returns AnalyzeResult objects with deeper navigation
    through the object model. However, sometimes you may need access to the raw JSON
    response for:

    - Easy inspection: View the complete response structure in the exact format returned
      by the service, making it easier to understand the full data model and discover
      available fields
    - Debugging: Inspect the raw response to troubleshoot issues, verify service behavior,
      or understand unexpected results
    - Advanced scenarios: Work with response structures that may change or include
      additional metadata not captured in the typed model

    NOTE: For most production scenarios, the object model approach is recommended as it
    provides type safety, IntelliSense support, and easier navigation. Use raw JSON access
    when you specifically need the benefits listed above.

USAGE:
    python sample_analyze_return_raw_json_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_configure_defaults.py for setup instructions.
"""

import asyncio
import json
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # [START analyze_return_raw_json]
        file_path = "sample_files/sample_invoice.pdf"

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        print(f"Analyzing {file_path} with prebuilt-documentSearch...")

        # Use the 'cls' callback parameter to get the raw HTTP response
        # This allows access to the complete response structure for easy inspection and debugging
        poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            cls=lambda pipeline_response, deserialized_obj, response_headers: (
                deserialized_obj,
                pipeline_response.http_response,
            ),
        )

        # Wait for completion and get both the deserialized object and raw HTTP response
        _, raw_http_response = await poller.result()
        # [END analyze_return_raw_json]

        # [START parse_raw_json]
        # Pretty-print the raw JSON response
        response_json = raw_http_response.json()
        pretty_json = json.dumps(response_json, indent=2, ensure_ascii=False)
        print(pretty_json)
        # [END parse_raw_json]

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
