# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging


def get_logger() -> logging.Logger:
    """Return the library-scoped logger.

    The log level is configured by the ``log_level`` constructor parameter
    of :class:`AgentServer` (or the ``AGENT_LOG_LEVEL`` env var as fallback).
    This function simply returns the named logger without forcing a level so
    that the level already set by the constructor is preserved.

    :return: Logger instance for azure.ai.agentserver.
    :rtype: logging.Logger
    """
    return logging.getLogger("azure.ai.agentserver")
