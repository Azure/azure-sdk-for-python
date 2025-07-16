# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
Import the VoiceLiveClient in the main module namespace
"""

from typing import List

from .voice_live_client import VoiceLiveClient

# Add VoiceLiveClient to the public exports
__all__ = ["VoiceLiveClient"]

def patch_sdk() -> None:
    """
    Patch the SDK to add additional client classes.
    This is called when the module is imported.
    """
    pass