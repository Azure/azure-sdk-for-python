# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Logging facade for AgentHost.

Usage::

    from azure.ai.agentserver.core import get_logger

    logger = get_logger()
    logger.info("Processing request")
"""
import logging


def get_logger() -> logging.Logger:
    """Return the library-scoped logger.

    :return: Logger instance for ``azure.ai.agentserver``.
    :rtype: logging.Logger
    """
    return logging.getLogger("azure.ai.agentserver")
