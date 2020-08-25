#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import time
from azure.servicebus._common.utils import utc_now

def get_logger(level):
    azure_logger = logging.getLogger("azure")
    if not azure_logger.handlers:
        azure_logger.setLevel(level)
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
        azure_logger.addHandler(handler)

    uamqp_logger = logging.getLogger("uamqp")
    if not uamqp_logger.handlers:
        uamqp_logger.setLevel(logging.INFO)
        uamqp_logger.addHandler(handler)
    return azure_logger


def print_message(_logger, message):
    _logger.info("Receiving: {}".format(message))
    _logger.debug("Time to live: {}".format(message.time_to_live))
    _logger.debug("Sequence number: {}".format(message.sequence_number))
    _logger.debug("Enqueue Sequence numger: {}".format(message.enqueued_sequence_number))
    _logger.debug("Partition Key: {}".format(message.partition_key))
    _logger.debug("Properties: {}".format(message.properties))
    _logger.debug("Delivery count: {}".format(message.delivery_count))
    try:
        _logger.debug("Locked until: {}".format(message.locked_until_utc))
        _logger.debug("Lock Token: {}".format(message.lock_token))
    except (TypeError, AttributeError):
        pass
    _logger.debug("Enqueued time: {}".format(message.enqueued_time_utc))


def sleep_until_expired(entity):
    time.sleep(max(0,(entity.locked_until_utc - utc_now()).total_seconds()+1))