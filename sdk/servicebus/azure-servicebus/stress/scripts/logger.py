# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from opencensus.ext.azure.log_exporter import AzureLogHandler


def get_base_logger(log_filename, logger_name, level=logging.INFO, print_console=False, log_format=None,
                    log_file_max_bytes=20 * 1024 * 1024, log_file_backup_count=3):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    formatter = log_format or logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    if print_console:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        if not logger.handlers:
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    if log_filename:
        logger_file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=log_file_max_bytes,
            backupCount=log_file_backup_count
        )
        logger_file_handler.setFormatter(formatter)
        logger.addHandler(logger_file_handler)

    return logger


def get_logger(log_filename, logger_name, level=logging.INFO, print_console=False, log_format=None,
               log_file_max_bytes=20 * 1024 * 1024, log_file_backup_count=3):
    stress_logger = logging.getLogger(logger_name)
    stress_logger.setLevel(level)
    eventhub_logger = logging.getLogger("azure.eventhub")
    eventhub_logger.setLevel(level)
    uamqp_logger = logging.getLogger("uamqp")
    uamqp_logger.setLevel(level)

    formatter = log_format or logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    if print_console:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(formatter)
        if not eventhub_logger.handlers:
            eventhub_logger.addHandler(console_handler)
        if not uamqp_logger.handlers:
            uamqp_logger.addHandler(console_handler)
        if not stress_logger.handlers:
            stress_logger.addHandler(console_handler)

    if log_filename:
        eventhub_file_handler = RotatingFileHandler(
            "eventhub_" + log_filename,
            maxBytes=log_file_max_bytes,
            backupCount=log_file_backup_count
        )
        uamqp_file_handler = RotatingFileHandler(
            "uamqp_" + log_filename,
            maxBytes=log_file_max_bytes,
            backupCount=log_file_backup_count
        )
        stress_file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=log_file_max_bytes,
            backupCount=log_file_backup_count
        )
        eventhub_file_handler.setFormatter(formatter)
        uamqp_file_handler.setFormatter(formatter)
        stress_file_handler.setFormatter(formatter)
        eventhub_logger.addHandler(eventhub_file_handler)
        uamqp_logger.addHandler(uamqp_file_handler)
        stress_logger.addHandler(stress_file_handler)

    return stress_logger


def get_azure_logger(logger_name, level=logging.INFO):
    logger = logging.getLogger("azure_logger_" + logger_name)
    logger.setLevel(level)
    # oc will automatically search for the ENV VAR 'APPLICATIONINSIGHTS_CONNECTION_STRING'
    logger.addHandler(AzureLogHandler())
    return logger
