# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
File operation utilities for Red Team Agent.

This module provides centralized file handling, path operations, and
data serialization utilities used across the red team components.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Try to import DefaultOpenEncoding, fallback to standard encoding
try:
    from azure.ai.evaluation._common._utils import DefaultOpenEncoding

    DEFAULT_ENCODING = DefaultOpenEncoding.WRITE
except ImportError:
    DEFAULT_ENCODING = "utf-8"


class FileManager:
    """Centralized file operations manager for Red Team operations."""

    def __init__(self, base_output_dir: Optional[str] = None, logger=None):
        """Initialize file manager.

        :param base_output_dir: Base directory for all file operations
        :param logger: Logger instance for file operations
        """
        self.base_output_dir = base_output_dir or "."
        self.logger = logger

    def ensure_directory(self, path: Union[str, os.PathLike]) -> str:
        """Ensure a directory exists, creating it if necessary.

        :param path: Path to the directory
        :return: Absolute path to the directory
        """
        abs_path = os.path.abspath(path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def generate_unique_filename(
        self, prefix: str = "", suffix: str = "", extension: str = "", use_timestamp: bool = False
    ) -> str:
        """Generate a unique filename.

        :param prefix: Prefix for the filename
        :param suffix: Suffix for the filename
        :param extension: File extension (with or without dot)
        :param use_timestamp: Whether to include timestamp in filename
        :return: Unique filename
        """
        parts = []

        if prefix:
            parts.append(prefix)

        if use_timestamp:
            parts.append(datetime.now().strftime("%Y%m%d_%H%M%S"))

        # Always include UUID for uniqueness
        parts.append(str(uuid.uuid4()))

        if suffix:
            parts.append(suffix)

        filename = "_".join(parts)

        if extension:
            if not extension.startswith("."):
                extension = "." + extension
            filename += extension

        return filename

    def get_scan_output_path(self, scan_id: str, filename: str = "") -> str:
        """Get path for scan output files.

        :param scan_id: Unique scan identifier
        :param filename: Optional filename to append
        :return: Full path for scan output
        """
        # Create scan directory based on DEBUG environment
        is_debug = os.environ.get("DEBUG", "").lower() in ("true", "1", "yes", "y")
        folder_prefix = "" if is_debug else "."

        scan_dir = os.path.join(self.base_output_dir, f"{folder_prefix}{scan_id}")
        self.ensure_directory(scan_dir)

        # Create .gitignore in scan directory if not debug mode
        if not is_debug:
            gitignore_path = os.path.join(scan_dir, ".gitignore")
            if not os.path.exists(gitignore_path):
                with open(gitignore_path, "w", encoding="utf-8") as f:
                    f.write("*\n")

        if filename:
            return os.path.join(scan_dir, filename)
        return scan_dir

    def write_json(self, data: Any, filepath: Union[str, os.PathLike], indent: int = 2, ensure_dir: bool = True) -> str:
        """Write data to JSON file.

        :param data: Data to write
        :param filepath: Path to write the file
        :param indent: JSON indentation
        :param ensure_dir: Whether to ensure directory exists
        :return: Absolute path of written file
        """
        abs_path = os.path.abspath(filepath)

        if ensure_dir:
            self.ensure_directory(os.path.dirname(abs_path))

        with open(abs_path, "w", encoding=DEFAULT_ENCODING) as f:
            json.dump(data, f, indent=indent)

        if self.logger:
            self.logger.debug(f"Successfully wrote JSON to {abs_path}")

        return abs_path

    def read_json(self, filepath: Union[str, os.PathLike]) -> Any:
        """Read data from JSON file.

        :param filepath: Path to the JSON file
        :return: Parsed JSON data
        """
        abs_path = os.path.abspath(filepath)

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if self.logger:
                self.logger.debug(f"Successfully read JSON from {abs_path}")

            return data
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to read JSON from {abs_path}: {str(e)}")
            raise

    def read_jsonl(self, filepath: Union[str, os.PathLike]) -> List[Dict]:
        """Read data from JSONL file.

        :param filepath: Path to the JSONL file
        :return: List of parsed JSON objects
        """
        abs_path = os.path.abspath(filepath)
        data = []

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            if self.logger:
                                self.logger.warning(f"Skipping invalid JSON line {line_num} in {abs_path}: {str(e)}")

            if self.logger:
                self.logger.debug(f"Successfully read {len(data)} records from JSONL {abs_path}")

            return data
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to read JSONL from {abs_path}: {str(e)}")
            raise

    def write_jsonl(self, data: List[Dict], filepath: Union[str, os.PathLike], ensure_dir: bool = True) -> str:
        """Write data to JSONL file.

        :param data: List of dictionaries to write
        :param filepath: Path to write the file
        :param ensure_dir: Whether to ensure directory exists
        :return: Absolute path of written file
        """
        abs_path = os.path.abspath(filepath)

        if ensure_dir:
            self.ensure_directory(os.path.dirname(abs_path))

        with open(abs_path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")

        if self.logger:
            self.logger.debug(f"Successfully wrote {len(data)} records to JSONL {abs_path}")

        return abs_path

    def safe_filename(self, name: str, max_length: int = 255) -> str:
        """Create a safe filename from a string.

        :param name: Original name
        :param max_length: Maximum filename length
        :return: Safe filename
        """
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        safe_name = "".join(c if c not in invalid_chars else "_" for c in name)

        # Replace spaces with underscores
        safe_name = safe_name.replace(" ", "_")

        # Truncate if too long
        if len(safe_name) > max_length:
            safe_name = safe_name[: max_length - 4] + "..."

        return safe_name

    def get_file_size(self, filepath: Union[str, os.PathLike]) -> int:
        """Get file size in bytes.

        :param filepath: Path to the file
        :return: File size in bytes
        """
        return os.path.getsize(filepath)

    def file_exists(self, filepath: Union[str, os.PathLike]) -> bool:
        """Check if file exists.

        :param filepath: Path to check
        :return: True if file exists
        """
        return os.path.isfile(filepath)

    def cleanup_file(self, filepath: Union[str, os.PathLike], ignore_errors: bool = True) -> bool:
        """Delete a file if it exists.

        :param filepath: Path to the file to delete
        :param ignore_errors: Whether to ignore deletion errors
        :return: True if file was deleted or didn't exist
        """
        try:
            if self.file_exists(filepath):
                os.remove(filepath)
                if self.logger:
                    self.logger.debug(f"Deleted file: {filepath}")
            return True
        except Exception as e:
            if not ignore_errors:
                raise
            if self.logger:
                self.logger.warning(f"Failed to delete file {filepath}: {str(e)}")
            return False


def create_file_manager(base_output_dir: Optional[str] = None, logger=None) -> FileManager:
    """Create a FileManager instance.

    :param base_output_dir: Base directory for file operations
    :param logger: Logger instance
    :return: Configured FileManager
    """
    return FileManager(base_output_dir=base_output_dir, logger=logger)
