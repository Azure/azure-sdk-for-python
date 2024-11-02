import logging
import pytest

from azure.servicebus.exceptions import ServiceBusConnectionError, ServiceBusError

try:
    from uamqp import errors as uamqp_AMQPErrors, constants as uamqp_AMQPConstants
    from azure.servicebus._transport._uamqp_transport import UamqpTransport
except ImportError:
    pass
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus._pyamqp import error as AMQPErrors

from utilities import uamqp_transport as get_uamqp_transport

uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()


@pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
def test_link_idle_timeout(uamqp_transport):
    if uamqp_transport:
        amqp_transport = UamqpTransport
        amqp_err_cls = uamqp_AMQPErrors.LinkDetach
        amqp_err_condition = uamqp_AMQPConstants.ErrorCodes.LinkDetachForced
    else:
        amqp_transport = PyamqpTransport
        amqp_err_cls = AMQPErrors.AMQPLinkError
        amqp_err_condition = AMQPErrors.ErrorCondition.LinkDetachForced
    amqp_error = amqp_err_cls(
        amqp_err_condition, description="Details: AmqpMessageConsumer.IdleTimerExpired: Idle timeout: 00:10:00."
    )
    logger = logging.getLogger("testlogger")
    sb_error = amqp_transport.create_servicebus_exception(logger, amqp_error)
    assert isinstance(sb_error, ServiceBusConnectionError)
    assert sb_error._retryable
    assert sb_error._shutdown_handler


@pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
def test_unknown_connection_error(uamqp_transport):
    if uamqp_transport:
        amqp_transport = UamqpTransport
        amqp_conn_err_cls = uamqp_AMQPErrors.AMQPConnectionError
        amqp_err_cls = uamqp_AMQPErrors.AMQPError
        amqp_unknown_err_condition = uamqp_AMQPConstants.ErrorCodes.UnknownError
    else:
        amqp_transport = PyamqpTransport
        amqp_conn_err_cls = AMQPErrors.AMQPConnectionError
        amqp_err_cls = AMQPErrors.AMQPError
        amqp_unknown_err_condition = AMQPErrors.ErrorCondition.UnknownError
    logger = logging.getLogger("testlogger")
    amqp_error = amqp_conn_err_cls(amqp_unknown_err_condition)
    sb_error = amqp_transport.create_servicebus_exception(logger, amqp_error)
    assert isinstance(sb_error, ServiceBusConnectionError)
    assert sb_error._retryable
    assert sb_error._shutdown_handler

    amqp_error = amqp_err_cls(amqp_unknown_err_condition)
    sb_error = amqp_transport.create_servicebus_exception(logger, amqp_error)
    assert not isinstance(sb_error, ServiceBusConnectionError)
    assert isinstance(sb_error, ServiceBusError)
    assert not sb_error._retryable
    assert sb_error._shutdown_handler


@pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
def test_internal_server_error(uamqp_transport):
    if uamqp_transport:
        amqp_transport = UamqpTransport
        amqp_err_cls = uamqp_AMQPErrors.LinkDetach
        err_condition = uamqp_AMQPConstants.ErrorCodes.InternalServerError
    else:
        amqp_transport = PyamqpTransport
        amqp_err_cls = AMQPErrors.AMQPLinkError
        err_condition = AMQPErrors.ErrorCondition.InternalError
    logger = logging.getLogger("testlogger")
    amqp_error = amqp_err_cls(
        description="The service was unable to process the request; please retry the operation.",
        condition=err_condition,
    )
    sb_error = amqp_transport.create_servicebus_exception(logger, amqp_error)
    assert isinstance(sb_error, ServiceBusError)
    assert sb_error._retryable
    assert sb_error._shutdown_handler
