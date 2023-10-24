# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

import logging

from ._ai_client import AIClient
from ._telemetry import initialize_logger_info

module_logger = logging.getLogger(__name__)
initialize_logger_info(module_logger, terminator="\n")

__all__ = [
    "AIClient",
]

VERSION = "0.1.0"
__version__ = VERSION
