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


class CompliantLoggerSamples(object):

    def get_shrike_logger(self):
        from shrike.compliant_logging import enable_compliant_logging

        enable_compliant_logging(
            format="%(prefix)s %(asctime)s %(levelname)s:%(name)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        return logging.getLogger(__name__)

    def get_sdkv2_logger(self):
        from azure.ai.ml._logging.compliant_logger import enable_compliant_logging

        enable_compliant_logging(
            format="%(prefix)s %(asctime)s %(levelname)s:%(name)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        return logging.getLogger(__name__)


if __name__ == "__main__":
    sample = CompliantLoggerSamples()
    # Shrike logger
    # OUTPUT WHEN line 48 & 49 are uncomment + 55 & 57 commented
    # SystemLog: 2024-11-20 10:41:44 INFO:__main__:Testing log message.
    #  2024-11-20 10:41:44 INFO:__main__:Testing log message.
    # from shrike.compliant_logging import DataCategory
    # logger = sample.get_shrike_logger()

    # SDK Logger
    # OUTPUT WHEN line 48 & 49 are comment + 55 & 57 uncommented
    # SystemLog: 2024-11-20 10:47:31 INFO:__main__:Testing log message.
    #  2024-11-20 10:41:44 INFO:__main__:Testing log message.
    from azure.ai.ml._logging.compliant_logger import DataCategory

    logger = sample.get_sdkv2_logger()
    message = "Testing log message."
    logger.info(message, category=DataCategory.PUBLIC)
    logger.info(message, category=DataCategory.PRIVATE)
