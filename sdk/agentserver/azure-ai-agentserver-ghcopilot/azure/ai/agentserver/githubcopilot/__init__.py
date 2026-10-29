# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

"""DEPRECATED: azure-ai-agentserver-ghcopilot is no longer maintained.

This package has been deprecated. Please use azure-ai-agentserver-core
and azure-ai-agentserver-responses directly.
"""

import warnings

from ._version import VERSION

warnings.warn(
    "azure-ai-agentserver-ghcopilot is deprecated and will not receive further updates. "
    "Migrate to azure-ai-agentserver-core and azure-ai-agentserver-responses.",
    DeprecationWarning,
    stacklevel=2,
)

__all__: list[str] = []
__version__ = VERSION
