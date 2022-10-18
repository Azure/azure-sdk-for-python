# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import sys

from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE


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
        self.logger: logging.Logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + name)
        self.logger.propagate = False
        self.module_logger = logging.getLogger(name)
        self.custom_dimensions = {}

    def update_info(self, data: dict) -> None:
        if "app_insights_handler" in data:
            self.logger.addHandler(data.pop("app_insights_handler"))


def in_jupyter_notebook() -> bool:
    """
    Checks if user is using a Jupyter Notebook. This is necessary because logging is not allowed in 
    non-Jupyter contexts.

    Adapted from https://stackoverflow.com/a/22424821
    """
    try:
        from IPython import get_ipython
        if 'IPKernelApp' not in get_ipython().config:
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True
