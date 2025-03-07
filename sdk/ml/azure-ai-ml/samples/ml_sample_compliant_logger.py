# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_sample_compliant_logger.py

DESCRIPTION:
    These samples demonstrate how to migrate from shrike logger to SDK V2 compliant logger.
    
USAGE:
    python ml_sample_compliant_logger.py

"""

import logging

# from shrike.compliant_logging import (
from azure.ai.ml._logging.compliant_logger import DataCategory, enable_compliant_logging


class CompliantLoggerSamples(object):
    def get_logger(self):
        enable_compliant_logging(
            format="%(prefix)s %(asctime)s %(levelname)s:%(name)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        return logging.getLogger(__name__)


if __name__ == "__main__":
    sample = CompliantLoggerSamples()

    logger = sample.get_logger()
    message = "Testing log message."
    logger.info(message, category=DataCategory.PUBLIC)
    logger.info(message, category=DataCategory.PRIVATE)
