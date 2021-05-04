#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import time
from azure.servicebus._common.utils import utc_now

def _get_default_handler():
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
    return handler

def _build_logger(name, level):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = _get_default_handler()
        logger.addHandler(handler)
    return logger

# Note: This was the initial generic logger entry point, kept to allow us to
# move to more fine-grained logging controls incrementally.
def get_logger(level, uamqp_level=logging.INFO):
    _build_logger("uamqp", uamqp_level)
    return _build_logger("azure", level)


def print_message(_logger, message):
    _logger.info("Receiving: {}".format(message))
    _logger.debug("Time to live: {}".format(message.time_to_live))
    _logger.debug("Sequence number: {}".format(message.sequence_number))
    _logger.debug("Enqueue Sequence numger: {}".format(message.enqueued_sequence_number))
    _logger.debug("Partition Key: {}".format(message.partition_key))
    _logger.debug("Application Properties: {}".format(message.application_properties))
    _logger.debug("Delivery count: {}".format(message.delivery_count))
    try:
        _logger.debug("Locked until: {}".format(message.locked_until_utc))
        _logger.debug("Lock Token: {}".format(message.lock_token))
    except (TypeError, AttributeError):
        pass
    _logger.debug("Enqueued time: {}".format(message.enqueued_time_utc))


def sleep_until_expired(entity):
    time.sleep(max(0,(entity.locked_until_utc - utc_now()).total_seconds()+1))