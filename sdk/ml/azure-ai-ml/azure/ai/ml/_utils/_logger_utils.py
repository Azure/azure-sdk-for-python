# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import sys

from opentelemetry import trace

from azure.ai.ml._telemetry.logging_handler import AML_INTERNAL_LOGGER_NAMESPACE


def initialize_logger_info(module_logger: logging.Logger, terminator="\n") -> None:
    """Initializes the logger with INFO level and adds a StreamHandler to the logger.

    :param module_logger: The logger to be initialized.
    :type module_logger: logging.Logger
    :param terminator: The line terminator for the StreamHandler. Defaults to a newline character.
    :type terminator: str
    :return: None
    """
    module_logger.setLevel(logging.INFO)
    module_logger.propagate = False
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    handler.terminator = terminator
    handler.flush = sys.stderr.flush
    module_logger.addHandler(handler)


tracer = trace.get_tracer(AML_INTERNAL_LOGGER_NAMESPACE)


class OpsLogger:
    """
    A logger class for managing logging and tracing operations within a package.
    This class initializes loggers and tracers for a specified package, and provides methods to update logging filters.
    """

    def __init__(self, name: str):
        """
        This constructor sets up the package logger, module logger, and tracer for the given package name.
        :param name: The name of the package for which the logger is being initialized.
        :type name: str
        """
        self.package_logger: logging.Logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE).getChild(name)
        self.package_logger.propagate = True
        self.package_tracer = tracer
        self.module_logger = logging.getLogger(name)
        self.custom_dimensions = {}

    def update_filter(self) -> None:
        """
        Update the logging filter for the package logger.
        This method attaches the filter from the parent logger to the package logger,
            as the parent's filter is not automatically propagated to the child logger.

        :return: None
        """
        # Attach filter explicitly as parent logger's filter is not propagated to child logger
        if self.package_logger.parent.filters:
            self.package_logger.addFilter(self.package_logger.parent.filters[0])
