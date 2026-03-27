# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Logging facade for AgentServer.

Usage::

    from azure.ai.agentserver.hosting import AgentLogger

    logger = AgentLogger.get()
    logger.info("Processing request")
"""
import logging


class AgentLogger:
    """Logging facade for AgentServer.

    Provides library-scoped logger access under the
    ``azure.ai.agentserver`` namespace.

    All methods are static — no instantiation required.
    """

    @staticmethod
    def get() -> logging.Logger:
        """Return the library-scoped logger.

        :return: Logger instance for ``azure.ai.agentserver``.
        :rtype: logging.Logger
        """
        return logging.getLogger("azure.ai.agentserver")
