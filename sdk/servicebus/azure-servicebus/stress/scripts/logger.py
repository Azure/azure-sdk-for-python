# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler

from opencensus.ext.azure.log_exporter import AzureLogHandler


def get_base_logger(log_filename, logger_name, level=logging.ERROR, print_console=False, log_format=None):
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
        # rotated hourly if small file, o/w rotated bi-hourly
        if level == logging.DEBUG or level == logging.INFO:
            time = 30
        else:
            time = 60
        file_handler = TimedRotatingFileHandler(log_filename, when="M", interval=time, utc=True)
        if not logger.handlers:
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


def get_logger(log_filename, logger_name, level=logging.ERROR, print_console=False, log_format=None):
    stress_logger = logging.getLogger(logger_name)
    stress_logger.setLevel(level)
    servicebus_logger = logging.getLogger("azure.servicebus")
    servicebus_logger.setLevel(level)
    pyamqp_logger = logging.getLogger("azure.servicebus._pyamqp")
    pyamqp_logger.setLevel(level)

    formatter = log_format or logging.Formatter(
        "%(asctime)s - [%(thread)d.%(threadName)s] - %(name)-12s %(levelname)-8s %(funcName)s(%(lineno)d) %(message)s"
    )
    # rotated hourly if small file, o/w rotated bi-hourly
    if level == logging.DEBUG or level == logging.INFO:
        time = 30
    else:
        time = 60
    file_handler = TimedRotatingFileHandler(log_filename, when="M", interval=time, utc=True)
    file_handler.setFormatter(formatter)
    servicebus_logger.addHandler(file_handler)
    pyamqp_logger.addHandler(file_handler)
    stress_logger.addHandler(file_handler)

    return stress_logger


def get_azure_logger(logger_name, level=logging.ERROR):
    logger = logging.getLogger("azure_logger_" + logger_name)
    logger.setLevel(level)
    # oc will automatically search for the ENV VAR 'APPLICATIONINSIGHTS_CONNECTION_STRING'
    logger.addHandler(AzureLogHandler())
    return logger
