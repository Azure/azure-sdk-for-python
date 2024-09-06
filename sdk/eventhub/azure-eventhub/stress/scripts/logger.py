# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from opencensus.ext.azure.log_exporter import AzureLogHandler



def get_base_logger(log_filename, logger_name, level=logging.ERROR, print_console=False, log_format=None,
                    log_file_max_bytes=20 * 1024 * 1024, log_file_backup_count=3):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    formatter = log_format or logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    if print_console:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        if not logger.handlers:
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
    else:
        file_handler = RotatingFileHandler(log_filename, maxBytes=10000 * 1000, 
                                    backupCount=2000)
        if not logger.handlers:
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


def get_logger(
    log_filename,
    logger_name,
    max_logfile_size=10000,
    logfile_backup_count=2000,
    level=logging.ERROR,
    print_console=False,
    log_format=None,
):
    stress_logger = logging.getLogger(logger_name)
    stress_logger.setLevel(level)
    eventhub_logger = logging.getLogger("azure.eventhub")
    eventhub_logger.setLevel(level)
    uamqp_logger = logging.getLogger("uamqp")
    uamqp_logger.setLevel(level)

    formatter = log_format or logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(funcName)s(%(lineno)d) %(message)s')

    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=max_logfile_size * 1000,
        backupCount=logfile_backup_count
    )
    file_handler.setFormatter(formatter)
    eventhub_logger.addHandler(file_handler)
    uamqp_logger.addHandler(file_handler)
    stress_logger.addHandler(file_handler)

    return stress_logger


def get_azure_logger(logger_name, level=logging.ERROR):
    logger = logging.getLogger("azure_logger_" + logger_name)
    logger.setLevel(level)
    # oc will automatically search for the ENV VAR 'APPLICATIONINSIGHTS_CONNECTION_STRING'
    logger.addHandler(AzureLogHandler())
    return logger
