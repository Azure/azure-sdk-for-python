# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import logging
from urllib.parse import urlparse
from logging.handlers import RotatingFileHandler

def get_logger(filename, level=logging.INFO):
    azure_logger = logging.getLogger("azure")
    azure_logger.setLevel(level)
    uamqp_logger = logging.getLogger("uamqp")
    uamqp_logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    file_handler = RotatingFileHandler(filename, maxBytes=5*1024*1024, backupCount=2)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    azure_logger.addHandler(file_handler)
    azure_logger.addHandler(console_handler)
    uamqp_logger.addHandler(console_handler)
    return azure_logger
