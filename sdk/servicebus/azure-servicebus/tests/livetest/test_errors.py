import logging

from azure.servicebus.exceptions import (
    _create_servicebus_exception,
    ServiceBusConnectionError,
    ServiceBusError
)
from azure.servicebus._pyamqp import error as AMQPErrors


def test_link_idle_timeout():
    logger = logging.getLogger("testlogger")
    amqp_error = AMQPErrors.AMQPLinkError(AMQPErrors.ErrorCondition.LinkDetachForced, description="Details: AmqpMessageConsumer.IdleTimerExpired: Idle timeout: 00:10:00.")
    sb_error = _create_servicebus_exception(logger, amqp_error)
    assert isinstance(sb_error, ServiceBusConnectionError)
    assert sb_error._retryable
    assert sb_error._shutdown_handler


def test_unknown_connection_error():
    logger = logging.getLogger("testlogger")
    amqp_error = AMQPErrors.AMQPConnectionError(AMQPErrors.ErrorCondition.UnknownError)
    sb_error = _create_servicebus_exception(logger, amqp_error)
    assert isinstance(sb_error,ServiceBusConnectionError)
    assert sb_error._retryable
    assert sb_error._shutdown_handler

    amqp_error = AMQPErrors.AMQPError(AMQPErrors.ErrorCondition.UnknownError)
    sb_error = _create_servicebus_exception(logger, amqp_error)
    assert not isinstance(sb_error,ServiceBusConnectionError)
    assert isinstance(sb_error,ServiceBusError)
    assert not sb_error._retryable
    assert sb_error._shutdown_handler

def test_internal_server_error():
    logger = logging.getLogger("testlogger")
    amqp_error = AMQPErrors.AMQPLinkError(
        description="The service was unable to process the request; please retry the operation.",
        condition=AMQPErrors.ErrorCondition.InternalError
    )
    sb_error = _create_servicebus_exception(logger, amqp_error)
    assert isinstance(sb_error, ServiceBusError)
    assert sb_error._retryable
    assert sb_error._shutdown_handler
