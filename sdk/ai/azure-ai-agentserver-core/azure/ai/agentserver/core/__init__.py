# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._version import VERSION
from .logger import configure as config_logging
from .server import FoundryCBAgent
from .server.common.agent_run_context import AgentRunContext

config_logging()

__all__ = ["FoundryCBAgent", "AgentRunContext"]
__version__ = VERSION

# temporarily add build info here, remove it after public release
try:
    from . import _buildinfo

    __commit__ = _buildinfo.commit
    __build_time__ = _buildinfo.build_time
except Exception:  # pragma: no cover
    __commit__ = "unknown"
    __build_time__ = "unknown"
