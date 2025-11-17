# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Helper utilities for Content Understanding samples."""

from __future__ import annotations
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def save_json_to_file(data: dict[str, Any], filename_prefix: str = "result") -> str:
    """Save JSON data to a file with timestamp.

    :param data: Dictionary to save as JSON
    :type data: dict[str, Any]
    :param filename_prefix: Prefix for the output filename
    :type filename_prefix: str
    :return: Path to the saved file
    :rtype: str
    """
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / "sample_output"
    output_dir.mkdir(exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    filepath = output_dir / filename

    # Save to file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved to: {filepath}")
    return str(filepath)


def get_sample_file_path(filename: str) -> str:
    """Get the absolute path to a sample file.

    :param filename: Name of the sample file
    :type filename: str
    :return: Absolute path to the file
    :rtype: str
    """
    samples_dir = Path(__file__).parent
    filepath = samples_dir / "sample_files" / filename

    if not filepath.exists():
        raise FileNotFoundError(f"Sample file not found: {filepath}")

    return str(filepath)


def read_binary_file(filepath: str) -> bytes:
    """Read a binary file and return its contents.

    :param filepath: Path to the file
    :type filepath: str
    :return: File contents as bytes
    :rtype: bytes
    """
    with open(filepath, "rb") as f:
        return f.read()
