# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""State management utilities for Configuration Manager.

This module provides global access functions for the Configuration Manager singleton.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from azure.monitor.opentelemetry.exporter._configuration import _ConfigurationManager

# Global singleton instance for easy access throughout the codebase
_configuration_manager = None

def get_configuration_manager() -> "_ConfigurationManager":
    """Get the global Configuration Manager singleton instance.

    This provides a single access point to the manager and handles lazy initialization.

    :return: The singleton Configuration Manager instance
    :rtype: _ConfigurationManager
    """
    global _configuration_manager  # pylint: disable=global-statement
    if _configuration_manager is None:
        from azure.monitor.opentelemetry.exporter._configuration import _ConfigurationManager
        _configuration_manager = _ConfigurationManager()
    return _configuration_manager
