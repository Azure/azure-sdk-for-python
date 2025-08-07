# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Helper functions for Azure AI Content Understanding samples.
"""

import json
import os
from datetime import datetime, timezone

from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential


def get_credential():
    """Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential."""
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    return AzureKeyCredential(key) if key else DefaultAzureCredential()


def save_response_to_file(result, output_dir: str = "test_output", filename_prefix: str = "analysis_result") -> str:
    """Persist the full AnalyzeResult as JSON and return the file path."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = os.path.join(output_dir, f"{filename_prefix}_{timestamp}.json")
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(result.as_dict(), fp, indent=2, ensure_ascii=False)
    print(f"💾 Analysis result saved to: {path}")
    return path
