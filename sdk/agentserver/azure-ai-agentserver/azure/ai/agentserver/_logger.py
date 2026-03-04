# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import os

_VALID_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def get_logger() -> logging.Logger:
    """Return the library-scoped logger with level from ``AGENT_LOG_LEVEL``.

    Reads the ``AGENT_LOG_LEVEL`` environment variable (default ``WARNING``)
    and applies it to the ``azure.ai.agentserver`` logger.  No handlers or
    formatters are configured — the caller (or the application root logger)
    controls output format.

    :return: Configured logger instance for azure.ai.agentserver.
    :rtype: logging.Logger
    """
    logger = logging.getLogger("azure.ai.agentserver")
    level = os.getenv("AGENT_LOG_LEVEL", "WARNING").upper()
    if level not in _VALID_LEVELS:
        level = "WARNING"
    logger.setLevel(level)
    return logger
