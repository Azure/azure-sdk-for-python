# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import sys
from typing import Dict

from azure.ai.ml._telemetry.logging_handler import AML_INTERNAL_LOGGER_NAMESPACE


def initialize_logger_info(module_logger: logging.Logger, terminator="\n") -> None:
    module_logger.setLevel(logging.INFO)
    module_logger.propagate = False
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    handler.terminator = terminator
    handler.flush = sys.stderr.flush
    module_logger.addHandler(handler)


class OpsLogger:
    def __init__(self, name: str):
        self.package_logger: logging.Logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + name)
        self.package_logger.propagate = False
        self.package_tracer = None
        self.module_logger = logging.getLogger(name)
        self.custom_dimensions = {}

    def update_info(self, data: Dict) -> None:
        if "app_insights_handler" in data:
            logger, tracer = data.pop("app_insights_handler")
            self.package_logger.addHandler(logger)
            self.package_tracer = tracer
