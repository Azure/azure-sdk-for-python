# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility for building ``x-platform-server`` version strings."""

from __future__ import annotations

import sys


def build_server_version(sdk_name: str, version: str) -> str:
    """Build a standard version segment for the ``x-platform-server`` header.

    Format: ``{sdk_name}/{version} (python/{major}.{minor})``

    Protocol packages call this during host initialisation and pass the
    result to :meth:`AgentServerHost.register_server_version`.

    :param sdk_name: The SDK identifier
        (e.g., ``"azure-ai-agentserver-responses"``).
    :type sdk_name: str
    :param version: The package version string (e.g., ``"1.0.0b1"``).
    :type version: str
    :returns: A formatted version string.
    :rtype: str
    :raises ValueError: If *sdk_name* or *version* is empty.
    """
    if not sdk_name or not sdk_name.strip():
        raise ValueError("sdk_name must not be empty.")
    if not version or not version.strip():
        raise ValueError("version must not be empty.")
    runtime = f"python/{sys.version_info.major}.{sys.version_info.minor}"
    return f"{sdk_name}/{version} ({runtime})"
