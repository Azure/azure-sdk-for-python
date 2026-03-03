# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import logging.config
import os
from typing import Any, Optional

from ._constants import Constants


def _get_default_log_config() -> dict[str, Any]:
    """Build default logging configuration with level from environment.

    :return: A dictionary containing logging configuration.
    :rtype: dict[str, Any]
    """
    log_level = _get_log_level()
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "azure.ai.agentserver": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
        },
        "handlers": {
            "console": {
                "formatter": "std_out",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "level": log_level,
            },
        },
        "formatters": {
            "std_out": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
    }


def _get_log_level() -> str:
    """Read log level from environment, defaulting to INFO.

    :return: A valid Python log level string.
    :rtype: str
    """
    log_level = os.getenv(Constants.AGENT_LOG_LEVEL, "INFO").upper()
    valid_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    if log_level not in valid_levels:
        log_level = "INFO"
    return log_level


def configure_logging(log_config: Optional[dict[str, Any]] = None) -> None:
    """Configure logging for the azure.ai.agentserver namespace.

    :param log_config: Optional logging configuration dict compatible with logging.config.dictConfig.
    :type log_config: Optional[dict[str, Any]]
    """
    try:
        if log_config is None:
            log_config = _get_default_log_config()
        logging.config.dictConfig(log_config)
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Failed to configure logging: %s", exc)


def get_logger() -> logging.Logger:
    """Return the library-scoped logger.

    :return: Configured logger instance for azure.ai.agentserver.
    :rtype: logging.Logger
    """
    return logging.getLogger("azure.ai.agentserver")
