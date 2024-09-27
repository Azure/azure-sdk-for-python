# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import sys

from opentelemetry import trace

from azure.ai.ml._telemetry.logging_handler import AML_INTERNAL_LOGGER_NAMESPACE


def initialize_logger_info(module_logger: logging.Logger, terminator="\n") -> None:
    module_logger.setLevel(logging.INFO)
    module_logger.propagate = False
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    handler.terminator = terminator
    handler.flush = sys.stderr.flush
    module_logger.addHandler(handler)


tracer = trace.get_tracer(AML_INTERNAL_LOGGER_NAMESPACE)


class OpsLogger:
    def __init__(self, name: str):
        self.package_logger: logging.Logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE).getChild(name)
        self.package_logger.propagate = True
        self.package_tracer = tracer
        self.module_logger = logging.getLogger(name)
        self.custom_dimensions = {}

    def update_filter(self) -> None:
        # Attach filter explicitly as parent logger's filter is not propagated to child logger
        if self.package_logger.parent.filters:
            self.package_logger.addFilter(self.package_logger.parent.filters[0])
