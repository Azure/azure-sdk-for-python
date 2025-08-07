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
from typing import Any
from enum import Enum

from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential


class PollerType(Enum):
    """Enum to distinguish different types of pollers for operation ID extraction."""
    ANALYZER_CREATION = "analyzer_creation"
    ANALYZE_CALL = "analyze_call"
    CLASSIFIER_CREATION = "classifier_creation"
    CLASSIFY_CALL = "classify_call"


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


def extract_operation_id_from_poller(poller: Any, poller_type: PollerType) -> str:
    """Extract operation ID from an LROPoller or AsyncLROPoller.
    
    The poller stores the initial response in `_initial_response`, which contains
    the Operation-Location header. The extraction pattern depends on the poller type:
    - AnalyzerCreation: https://endpoint/contentunderstanding/operations/{operation_id}?api-version=...
    - AnalyzeCall: https://endpoint/contentunderstanding/analyzerResults/{operation_id}?api-version=...
    - ClassifierCreation: https://endpoint/contentunderstanding/operations/{operation_id}?api-version=...
    - ClassifyCall: https://endpoint/contentunderstanding/classifierResults/{operation_id}?api-version=...
    
    Args:
        poller: The LROPoller or AsyncLROPoller instance
        poller_type: The type of poller (ANALYZER_CREATION, ANALYZE_CALL, CLASSIFIER_CREATION, or CLASSIFY_CALL) - REQUIRED
        
    Returns:
        str: The operation ID extracted from the poller
        
    Raises:
        ValueError: If no operation ID can be extracted from the poller or if poller_type is not provided
    """
    if poller_type is None:
        raise ValueError("poller_type is required and must be specified")
    # Extract from Operation-Location header (standard approach)
    initial_response = poller.polling_method()._initial_response
    operation_location = initial_response.http_response.headers.get("Operation-Location")
    
    if operation_location:
        if poller_type == PollerType.ANALYZER_CREATION or poller_type == PollerType.CLASSIFIER_CREATION:
            # Pattern: https://endpoint/.../operations/{operation_id}?api-version=...
            if "/operations/" in operation_location:
                operation_id = operation_location.split("/operations/")[1].split("?")[0]
                return operation_id
        elif poller_type == PollerType.ANALYZE_CALL:
            # Pattern: https://endpoint/.../analyzerResults/{operation_id}?api-version=...
            if "/analyzerResults/" in operation_location:
                operation_id = operation_location.split("/analyzerResults/")[1].split("?")[0]
                return operation_id
        elif poller_type == PollerType.CLASSIFY_CALL:
            # Pattern: https://endpoint/.../classifierResults/{operation_id}?api-version=...
            if "/classifierResults/" in operation_location:
                operation_id = operation_location.split("/classifierResults/")[1].split("?")[0]
                return operation_id
    
    raise ValueError(f"Could not extract operation ID from poller for type {poller_type}")
