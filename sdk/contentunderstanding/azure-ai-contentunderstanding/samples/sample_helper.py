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
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Dict
from enum import Enum
from azure.ai.contentunderstanding.models import (
    ContentClassifier,
    ClassifierCategory,
    ContentField,
)


def get_field_value(fields: Dict[str, ContentField], field_name: str) -> Any:
    """
    Extract the actual value from a ContentField using the unified .value property.

    Args:
        fields: A dictionary of field names to ContentField objects.
        field_name: The name of the field to extract.

    Returns:
        The extracted value or None if not found.
    """
    if not fields or field_name not in fields:
        return None

    field_data = fields[field_name]

    # Simply use the .value property which works for all ContentField types
    return field_data.value


class PollerType(Enum):
    """Enum to distinguish different types of pollers for operation ID extraction."""

    ANALYZER_CREATION = "analyzer_creation"
    ANALYZE_CALL = "analyze_call"
    CLASSIFIER_CREATION = "classifier_creation"
    CLASSIFY_CALL = "classify_call"


def save_json_to_file(
    result, output_dir: str = "test_output", filename_prefix: str = "analysis_result"
) -> str:
    """Persist the full AnalyzeResult as JSON and return the file path."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = os.path.join(output_dir, f"{filename_prefix}_{timestamp}.json")
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(result, fp, indent=2, ensure_ascii=False)
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
    operation_location = initial_response.http_response.headers.get(
        "Operation-Location"
    )

    if operation_location:
        if (
            poller_type == PollerType.ANALYZER_CREATION
            or poller_type == PollerType.CLASSIFIER_CREATION
        ):
            # Pattern: https://endpoint/.../operations/{operation_id}?api-version=...
            if "/operations/" in operation_location:
                operation_id = operation_location.split("/operations/")[1].split("?")[0]
                return operation_id
        elif poller_type == PollerType.ANALYZE_CALL:
            # Pattern: https://endpoint/.../analyzerResults/{operation_id}?api-version=...
            if "/analyzerResults/" in operation_location:
                operation_id = operation_location.split("/analyzerResults/")[1].split(
                    "?"
                )[0]
                return operation_id
        elif poller_type == PollerType.CLASSIFY_CALL:
            # Pattern: https://endpoint/.../classifierResults/{operation_id}?api-version=...
            if "/classifierResults/" in operation_location:
                operation_id = operation_location.split("/classifierResults/")[1].split(
                    "?"
                )[0]
                return operation_id

    raise ValueError(
        f"Could not extract operation ID from poller for type {poller_type}"
    )


def save_keyframe_image_to_file(
    image_content: bytes,
    keyframe_id: str,
    test_name: str,
    test_py_file_dir: str,
    identifier: Optional[str] = None,
    output_dir: str = "test_output",
) -> str:
    """Save keyframe image to output file using pytest naming convention.

    Args:
        image_content: The binary image content to save
        keyframe_id: The keyframe ID (e.g., "keyFrame.1")
        test_name: Name of the test case (e.g., function name)
        test_py_file_dir: Directory where pytest files are located
        identifier: Optional unique identifier to avoid conflicts (e.g., analyzer_id)
        output_dir: Directory name to save the output file (default: "test_output")

    Returns:
        str: Path to the saved image file

    Raises:
        OSError: If there are issues creating directory or writing file
    """
    # Generate timestamp and frame ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    frame_id = keyframe_id.replace("keyFrame.", "")

    # Create output directory if it doesn't exist
    output_dir_path = os.path.join(test_py_file_dir, output_dir)
    os.makedirs(output_dir_path, exist_ok=True)

    # Generate output filename with optional identifier to avoid conflicts
    if identifier:
        output_filename = f"{test_name}_{identifier}_{timestamp}_{frame_id}.jpg"
    else:
        output_filename = f"{test_name}_{timestamp}_{frame_id}.jpg"

    saved_file_path = os.path.join(output_dir_path, output_filename)

    # Write the image content to file
    with open(saved_file_path, "wb") as image_file:
        image_file.write(image_content)

    print(f"🖼️  Image file saved to: {saved_file_path}")
    return saved_file_path


def read_image_to_base64(image_path: str) -> str:
    """Read image file and return base64-encoded string."""
    import base64

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
        return base64.b64encode(image_bytes).decode("utf-8")


def read_image_to_base64_bytes(image_path: str) -> bytes:
    """Read image file and return base64-encoded bytes."""
    import base64

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
        return base64.b64encode(image_bytes)
