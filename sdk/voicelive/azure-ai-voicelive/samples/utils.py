#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
Helper utilities for Azure VoiceLive samples.
"""

import os
from pathlib import Path
import sys
from typing import Dict, Optional


def load_env_vars(verbose: bool = True) -> Dict[str, str]:
    """
    Load environment variables from .env file if available.
    Returns a dictionary of loaded environment variables.

    Args:
        verbose (bool): Whether to print info about the loaded environment variables

    Returns:
        Dict[str, str]: Dictionary of loaded environment variables
    """
    # Try to import dotenv
    try:
        from dotenv import load_dotenv
    except ImportError:
        if verbose:
            print("python-dotenv package not found. Environment variables will not be loaded from .env file.")
            print("Install with: pip install python-dotenv")
        return {}

    # Look for .env file in the current directory and parent directories
    env_path = find_env_file()

    if env_path and os.path.isfile(env_path):
        if verbose:
            print(f"Loading environment variables from {env_path}")
        load_dotenv(env_path)
        if verbose:
            print("Environment variables loaded successfully")

        # Return the loaded environment variables
        loaded_vars = {}
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key.strip() in os.environ:
                        loaded_vars[key.strip()] = (
                            "********" if "KEY" in key or "SECRET" in key else os.environ[key.strip()]
                        )

        if verbose and loaded_vars:
            print("Loaded environment variables:")
            for key, value in loaded_vars.items():
                print(f"  {key}: {value}")

        return loaded_vars
    else:
        if verbose:
            print("No .env file found. Using existing environment variables.")
        return {}


def find_env_file() -> Optional[str]:
    """
    Find a .env file by looking in the current directory and walking up the directory tree.

    Returns:
        Optional[str]: Path to the .env file if found, None otherwise
    """
    # Start with the current working directory
    current_dir = os.getcwd()

    # Check if we're in a sample directory and need to go up to the package root
    if os.path.basename(current_dir) == "samples":
        # Try the parent directory
        parent_dir = os.path.dirname(current_dir)
        env_path = os.path.join(parent_dir, ".env")
        if os.path.isfile(env_path):
            return env_path

    # Try the current directory first
    env_path = os.path.join(current_dir, ".env")
    if os.path.isfile(env_path):
        return env_path

    # Walk up the directory tree
    max_levels = 3  # Limit how far up we go
    for _ in range(max_levels):
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # We've reached the root directory
            break

        current_dir = parent_dir
        env_path = os.path.join(current_dir, ".env")
        if os.path.isfile(env_path):
            return env_path

    # If we didn't find it in the parent directories, check the samples directory
    # in case we're running from the package root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ".env")
    if os.path.isfile(env_path):
        return env_path

    # Check one level up from the script directory
    env_path = os.path.join(os.path.dirname(script_dir), ".env")
    if os.path.isfile(env_path):
        return env_path

    return None


def check_samples_prerequisites():
    """
    Check prerequisites for running the samples.
    """
    try:
        import azure.ai.voicelive
    except ImportError:
        print("azure-ai-voicelive package is not installed. Install with:")
        print("pip install azure-ai-voicelive")
        sys.exit(1)

    try:
        import dotenv
    except ImportError:
        print("python-dotenv package is not installed. Install with:")
        print("pip install python-dotenv")
        print("Continuing without .env file support...")
