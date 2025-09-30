# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""State management utilities for Configuration Manager.

This module provides global access functions for the Configuration Manager singleton.
"""
import os
from typing import Optional, TYPE_CHECKING

from azure.monitor.opentelemetry.exporter._constants import _APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED

if TYPE_CHECKING:
    from azure.monitor.opentelemetry.exporter._configuration import _ConfigurationManager

# Global singleton instance for easy access throughout the codebase
_configuration_manager = None

def get_configuration_manager() -> Optional["_ConfigurationManager"]:
    """Get the global Configuration Manager singleton instance.

    This provides a single access point to the manager and handles lazy initialization.
    Returns None if control plane functionality is disabled via environment variable.

    :return: The singleton Configuration Manager instance, or None if disabled
    :rtype: Optional[_ConfigurationManager]
    """
    disabled = os.environ.get(_APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED)
    if disabled is not None and disabled.lower() == "true":
        return None
    global _configuration_manager  # pylint: disable=global-statement
    if _configuration_manager is None:
        from azure.monitor.opentelemetry.exporter._configuration import _ConfigurationManager
        _configuration_manager = _ConfigurationManager()
    return _configuration_manager
