#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import time
try:
    import uamqp
    uamqp_available = True
except (ModuleNotFoundError, ImportError):
    uamqp_available = False
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
def get_logger(level, amqp_level=logging.INFO):
    _build_logger("azure.servicebus._pyamqp", amqp_level)
    _build_logger("uamqp", amqp_level)
    return _build_logger("azure", level)


def print_message(_logger, message):
    _logger.info(f"Receiving: {message}")
    _logger.debug(f"Time to live: {message.time_to_live}")
    _logger.debug(f"Sequence number: {message.sequence_number}")
    _logger.debug(f"Enqueue Sequence numger: {message.enqueued_sequence_number}")
    _logger.debug(f"Partition Key: {message.partition_key}")
    _logger.debug(f"Application Properties: {message.application_properties}")
    _logger.debug(f"Delivery count: {message.delivery_count}")
    try:
        _logger.debug(f"Locked until: {message.locked_until_utc}")
        _logger.debug(f"Lock Token: {message.lock_token}")
    except (TypeError, AttributeError):
        pass
    _logger.debug(f"Enqueued time: {message.enqueued_time_utc}")


def sleep_until_expired(entity):
    time.sleep(max(0,(entity.locked_until_utc - utc_now()).total_seconds()+1))


def uamqp_transport(use_uamqp=uamqp_available, use_pyamqp=True):
    uamqp_transport_params = []
    uamqp_transport_ids = []
    if use_uamqp:
        uamqp_transport_params.append(True)
        uamqp_transport_ids.append("uamqp")
    if use_pyamqp:
        uamqp_transport_params.append(False)
        uamqp_transport_ids.append("pyamqp")
    return uamqp_transport_params, uamqp_transport_ids

class ArgPasser:
    def __call__(self, fn):
        def _preparer(test_class, uamqp_transport, **kwargs):
            fn(test_class, uamqp_transport=uamqp_transport, **kwargs)
        return _preparer

class ArgPasserAsync:
    def __call__(self, fn):
        async def _preparer(test_class, uamqp_transport, **kwargs):
            await fn(test_class, uamqp_transport=uamqp_transport, **kwargs)
        return _preparer
    