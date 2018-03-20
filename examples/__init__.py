# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import logging

def get_logger(level):
    azure_logger = logging.getLogger("azure")
    azure_logger.setLevel(level)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
    azure_logger.addHandler(handler)

    uamqp_logger = logging.getLogger("uamqp")
    uamqp_logger.setLevel(level)
    uamqp_logger.addHandler(handler)
    return azure_logger
