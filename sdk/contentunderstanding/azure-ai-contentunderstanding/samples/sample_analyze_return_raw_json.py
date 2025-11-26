# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_return_raw_json.py

DESCRIPTION:
    This sample demonstrates how to access the raw JSON response from analysis operations
    using protocol methods. This is useful for advanced scenarios where you need direct access
    to the JSON structure.

    The Content Understanding SDK provides two approaches for accessing analysis results:
    1. Object model approach (recommended): Returns strongly-typed AnalyzeResult objects
    2. Protocol method approach: Returns raw BinaryData containing the JSON response

    For production use, prefer the object model approach as it provides:
    - Type safety
    - IntelliSense support
    - Easier navigation of results
    - Better error handling

    Use raw JSON only when you need:
    - Custom JSON processing
    - Direct access to the raw response structure
    - Integration with custom JSON parsers

USAGE:
    python sample_analyze_return_raw_json.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_configure_defaults.py for setup instructions.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # Analyze and return raw JSON
    analyze_return_raw_json(client)


# [START ContentUnderstandingAnalyzeReturnRawJson]
def analyze_return_raw_json(client: ContentUnderstandingClient) -> None:
    """Use the protocol method to get raw JSON response."""

    file_path = "sample_files/sample_invoice.pdf"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    print(f"Analyzing {file_path} with prebuilt-documentSearch...")

    # Use the standard method which returns an AnalyzeResult
    # Then serialize to JSON for raw access
    poller = client.begin_analyze_binary(
        analyzer_id="prebuilt-documentSearch",
        binary_input=file_bytes,
    )
    result = poller.result()

    # Convert to dictionary and then to JSON
    result_dict = result.as_dict()
    parse_and_save_json(result_dict)
# [END ContentUnderstandingAnalyzeReturnRawJson]


# [START ContentUnderstandingParseRawJson]
def parse_and_save_json(result_dict: dict) -> None:
    """Parse and format the raw JSON response."""

    # Pretty-print the JSON
    pretty_json = json.dumps(result_dict, indent=2, ensure_ascii=False, default=str)

    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / "sample_output"
    output_dir.mkdir(exist_ok=True)

    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"analyze_result_{timestamp}.json"
    output_path = output_dir / output_filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_json)

    print(f"\nRaw JSON response saved to: {output_path}")
    print(f"File size: {len(pretty_json):,} characters")

    # Show a preview of the JSON structure
    print("\nJSON Structure Preview:")
    print("=" * 50)
    preview = pretty_json[:2000] + "..." if len(pretty_json) > 2000 else pretty_json
    print(preview)
    print("=" * 50)
# [END ContentUnderstandingParseRawJson]


if __name__ == "__main__":
    main()
