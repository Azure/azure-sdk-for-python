# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
from logging.handlers import RotatingFileHandler

def init_logger(file, level):
    logging.basicConfig(filename=file, level=level)
    logger = logging.getLogger()
    logger.addHandler(RotatingFileHandler(file, maxBytes=5*1024*1024, backupCount=2))
    return logger
