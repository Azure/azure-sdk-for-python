# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from opencensus.ext.azure.log_exporter import AzureLogHandler


def get_base_logger(log_filename, logger_name, level=logging.ERROR, print_console=False, log_format=None, rotating_logs=True):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    formatter = log_format or logging.Formatter(
        "%(asctime)s - [%(thread)d.%(threadName)s] - %(name)s - %(levelname)s - %(message)s"
    )

    if print_console:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        if not logger.handlers:
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
    else:
        if rotating_logs:
            if not logger.handlers:
                # 5 MB max file size, 350 files max
                mb = 50
                bytes_in_mb = 1_048_576
                bytes = mb * bytes_in_mb
                file_handler = RotatingFileHandler(log_filename, maxBytes=bytes, backupCount=300)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
        else:
            file_handler = logging.FileHandler(log_filename)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


def get_logger(
    log_filename,
    logger_name,
    level=logging.ERROR,
    print_console=False,
    log_format=None,
    rotating_logs=True,
):
    stress_logger = logging.getLogger(logger_name)
    stress_logger.setLevel(level)
    eventhub_logger = logging.getLogger("azure.eventhub")
    eventhub_logger.setLevel(level)

    formatter = log_format or logging.Formatter(
        "%(asctime)s - [%(thread)d.%(threadName)s] - %(name)-12s %(levelname)-8s %(funcName)s(%(lineno)d) %(message)s"
    )

    if rotating_logs:
        # If any do not have handlers, create a new file handler and add.
        if not eventhub_logger.handlers or not stress_logger.handlers:
            # 5 MB max file size, 350 files max
            mb = 50
            bytes_in_mb = 1_048_576
            bytes = mb * bytes_in_mb
            file_handler = RotatingFileHandler(log_filename, maxBytes=bytes, backupCount=300)
            file_handler.setFormatter(formatter)
            if not eventhub_logger.handlers:
                eventhub_logger.addHandler(file_handler)
            if not stress_logger.handlers:
                stress_logger.addHandler(file_handler)
    else:
        console_handler = logging.FileHandler(log_filename)
        console_handler.setFormatter(formatter)
        eventhub_logger.addHandler(console_handler)
        stress_logger.addHandler(console_handler)

    return stress_logger


def get_azure_logger(logger_name, level=logging.ERROR):
    logger = logging.getLogger("azure_logger_" + logger_name)
    logger.setLevel(level)
    # oc will automatically search for the ENV VAR 'APPLICATIONINSIGHTS_CONNECTION_STRING'
    logger.addHandler(AzureLogHandler())
    return logger
