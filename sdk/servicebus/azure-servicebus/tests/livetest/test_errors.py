import logging

from uamqp import errors as AMQPErrors, constants as AMQPConstants
from azure.servicebus.exceptions import (
    _create_servicebus_exception,
    ServiceBusConnectionError,
    ServiceBusError
)


def test_link_idle_timeout():
    logger = logging.getLogger("testlogger")
    amqp_error = AMQPErrors.LinkDetach(AMQPConstants.ErrorCodes.LinkDetachForced, description="Details: AmqpMessageConsumer.IdleTimerExpired: Idle timeout: 00:10:00.")
    sb_error = _create_servicebus_exception(logger, amqp_error)
    assert isinstance(sb_error, ServiceBusConnectionError)
    assert sb_error._retryable
    assert sb_error._shutdown_handler


def test_unknown_connection_error():
    logger = logging.getLogger("testlogger")
    amqp_error = AMQPErrors.AMQPConnectionError(AMQPConstants.ErrorCodes.UnknownError)
    sb_error = _create_servicebus_exception(logger, amqp_error)
    assert isinstance(sb_error,ServiceBusConnectionError)
    assert sb_error._retryable
    assert sb_error._shutdown_handler

    amqp_error = AMQPErrors.AMQPError(AMQPConstants.ErrorCodes.UnknownError)
    sb_error = _create_servicebus_exception(logger, amqp_error)
    assert not isinstance(sb_error,ServiceBusConnectionError)
    assert isinstance(sb_error,ServiceBusError)
    assert not sb_error._retryable
    assert sb_error._shutdown_handler

def test_internal_server_error():
    logger = logging.getLogger("testlogger")
    amqp_error = AMQPErrors.LinkDetach(
        description="The service was unable to process the request; please retry the operation.",
        condition=AMQPConstants.ErrorCodes.InternalServerError
    )
    sb_error = _create_servicebus_exception(logger, amqp_error)
    assert isinstance(sb_error, ServiceBusError)
    assert sb_error._retryable
    assert sb_error._shutdown_handler
