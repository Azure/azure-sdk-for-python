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
    logger.setLevel(logging.DEBUG)
    formatter = log_format or logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

def get_logger(log_filename, logger_name, level=logging.INFO, print_console=False, log_format=None,
               log_file_max_bytes=20 * 1024 * 1024, log_file_backup_count=3):
    stress_logger = logging.getLogger(logger_name)
    stress_logger.setLevel(logging.DEBUG)
    servicebus_logger = logging.getLogger("azure.servicebus")
    servicebus_logger.setLevel(logging.DEBUG)
    pyamqp_logger = logging.getLogger("azure.servicebus._pyamqp")
    pyamqp_logger.setLevel(logging.DEBUG)

    formatter = log_format or logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    console_handler = logging.FileHandler(log_filename)
    console_handler.setFormatter(formatter)
    servicebus_logger.addHandler(console_handler)
    pyamqp_logger.addHandler(console_handler)
    stress_logger.addHandler(console_handler)

    return stress_logger


def get_azure_logger(logger_name, level=logging.INFO):
    logger = logging.getLogger("azure_logger_" + logger_name)
    logger.setLevel(logging.DEBUG)
    # oc will automatically search for the ENV VAR 'APPLICATIONINSIGHTS_CONNECTION_STRING'
    logger.addHandler(AzureLogHandler())
    return logger
