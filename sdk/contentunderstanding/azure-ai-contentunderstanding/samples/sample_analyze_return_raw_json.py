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
    using the 'cls' callback parameter. This is useful for advanced scenarios where you need
    direct access to the JSON structure.

    The Content Understanding SDK provides two approaches for accessing analysis results:

    1. Object model approach (recommended): Returns strongly-typed AnalyzeResult objects
       that are easier to navigate and use. This is shown in sample_analyze_binary.py.

    2. Protocol method approach: Returns raw HTTP response containing the JSON. This sample
       demonstrates this approach for advanced scenarios.

    IMPORTANT: For production use, prefer the object model approach as it provides:
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

    # [START analyze_return_raw_json]
    file_path = "sample_files/sample_invoice.pdf"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    print(f"Analyzing {file_path} with prebuilt-documentSearch...")

    # Use the 'cls' callback parameter to get the raw HTTP response
    # The 'cls' parameter allows us to intercept the response and return custom data
    # We return a tuple: (deserialized_object, raw_http_response)
    # Note: For production use, prefer the object model approach (without cls parameter)
    #       which returns AnalyzeResult objects that are easier to work with
    poller = client.begin_analyze_binary(
        analyzer_id="prebuilt-documentSearch",
        binary_input=file_bytes,
        content_type="application/pdf",
        cls=lambda pipeline_response, deserialized_obj, response_headers: (
            deserialized_obj,
            pipeline_response.http_response,
        ),
    )

    # Wait for completion and get both the deserialized object and raw HTTP response
    _, raw_http_response = poller.result()
    # [END analyze_return_raw_json]

    # [START parse_raw_json]
    # Parse the raw JSON response
    response_json = raw_http_response.json()

    # Pretty-print the JSON
    pretty_json = json.dumps(response_json, indent=2, ensure_ascii=False)

    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / "sample_output"
    output_dir.mkdir(exist_ok=True)

    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"analyze_result_{timestamp}.json"
    output_path = output_dir / output_filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_json)

    print(f"Raw JSON response saved to: {output_path}")
    print(f"File size: {len(pretty_json):,} characters")
    # [END parse_raw_json]

    # [START extract_from_raw_json]
    # Extract key information from raw JSON
    # This demonstrates accessing the same data that would be available via the object model
    if "result" in response_json:
        result_data = response_json["result"]

        if "analyzerId" in result_data:
            print(f"\nAnalyzer ID: {result_data['analyzerId']}")

        if "contents" in result_data and isinstance(result_data["contents"], list):
            print(f"Contents count: {len(result_data['contents'])}")

            if len(result_data["contents"]) > 0:
                first_content = result_data["contents"][0]

                if "kind" in first_content:
                    print(f"Content kind: {first_content['kind']}")
                if "mimeType" in first_content:
                    print(f"MIME type: {first_content['mimeType']}")

                # Extract markdown content from raw JSON
                # Object model equivalent: content.markdown
                print("\nMarkdown Content (from raw JSON):")
                print("=" * 50)
                if "markdown" in first_content and first_content["markdown"]:
                    print(first_content["markdown"])
                else:
                    print("No markdown content available.")
                print("=" * 50)

                # Extract document properties from raw JSON
                # Object model equivalent: document_content.start_page_number, etc.
                if first_content.get("kind") == "document":
                    print("\nDocument Information (from raw JSON):")
                    if "startPageNumber" in first_content:
                        print(f"  Start page: {first_content['startPageNumber']}")
                    if "endPageNumber" in first_content:
                        print(f"  End page: {first_content['endPageNumber']}")

                    start_page = first_content.get("startPageNumber")
                    end_page = first_content.get("endPageNumber")
                    if start_page and end_page:
                        total_pages = end_page - start_page + 1
                        print(f"  Total pages: {total_pages}")

                    # Extract pages information
                    # Object model equivalent: document_content.pages
                    if "pages" in first_content and first_content["pages"]:
                        pages = first_content["pages"]
                        unit = first_content.get("unit", "units")
                        print(f"\nPages ({len(pages)}):")
                        for page in pages:
                            page_num = page.get("pageNumber")
                            width = page.get("width")
                            height = page.get("height")
                            print(f"  Page {page_num}: {width} x {height} {unit}")
    # [END extract_from_raw_json]


if __name__ == "__main__":
    main()
