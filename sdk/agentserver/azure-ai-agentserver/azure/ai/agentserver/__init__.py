# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._version import VERSION
from .server._base import AgentServer

__all__ = ["AgentServer"]
__version__ = VERSION
