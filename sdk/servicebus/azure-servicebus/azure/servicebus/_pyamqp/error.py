#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from enum import Enum
from typing import AnyStr, Dict, List, Optional

from .constants import SECURE_PORT, FIELD
from .types import AMQP_STRUCTURED_TYPES, AMQPTypes, FieldDefinition, Performative


class ErrorCondition(bytes, Enum):
    # Shared error conditions:

    #: An internal error occurred. Operator intervention may be required to resume normaloperation.
    InternalError = b"amqp:internal-error"
    #: A peer attempted to work with a remote entity that does not exist.
    NotFound = b"amqp:not-found"
    #: A peer attempted to work with a remote entity to which it has no access due tosecurity settings.
    UnauthorizedAccess = b"amqp:unauthorized-access"
    #: Data could not be decoded.
    DecodeError = b"amqp:decode-error"
    #: A peer exceeded its resource allocation.
    ResourceLimitExceeded = b"amqp:resource-limit-exceeded"
    #: The peer tried to use a frame in a manner that is inconsistent with the semantics defined in the specification.
    NotAllowed = b"amqp:not-allowed"
    #: An invalid field was passed in a frame body, and the operation could not proceed.
    InvalidField = b"amqp:invalid-field"
    #: The peer tried to use functionality that is not implemented in its partner.
    NotImplemented = b"amqp:not-implemented"
    #: The client attempted to work with a server entity to which it has no access
    #: because another client is working with it.
    ResourceLocked = b"amqp:resource-locked"
    #: The client made a request that was not allowed because some precondition failed.
    PreconditionFailed = b"amqp:precondition-failed"
    #: A server entity the client is working with has been deleted.
    ResourceDeleted = b"amqp:resource-deleted"
    #: The peer sent a frame that is not permitted in the current state of the Session.
    IllegalState = b"amqp:illegal-state"
    #: The peer cannot send a frame because the smallest encoding of the performative with the currently
    #: valid values would be too large to fit within a frame of the agreed maximum frame size.
    FrameSizeTooSmall = b"amqp:frame-size-too-small"

    # Symbols used to indicate connection error conditions:

    #: An operator intervened to close the Connection for some reason. The client may retry at some later date.
    ConnectionCloseForced = b"amqp:connection:forced"
    #: A valid frame header cannot be formed from the incoming byte stream.
    ConnectionFramingError = b"amqp:connection:framing-error"
    #: The container is no longer available on the current connection. The peer should attempt reconnection
    #: to the container using the details provided in the info map.
    ConnectionRedirect = b"amqp:connection:redirect"

    # Symbols used to indicate session error conditions:

    #: The peer violated incoming window for the session.
    SessionWindowViolation = b"amqp:session:window-violation"
    #: Input was received for a link that was detached with an error.
    SessionErrantLink = b"amqp:session:errant-link"
    #: An attach was received using a handle that is already in use for an attached Link.
    SessionHandleInUse = b"amqp:session:handle-in-use"
    #: A frame (other than attach) was received referencing a handle which
    #: is not currently in use of an attached Link.
    SessionUnattachedHandle = b"amqp:session:unattached-handle"

    # Symbols used to indicate link error conditions:

    #: An operator intervened to detach for some reason.
    LinkDetachForced = b"amqp:link:detach-forced"
    #: The peer sent more Message transfers than currently allowed on the link.
    LinkTransferLimitExceeded = b"amqp:link:transfer-limit-exceeded"
    #: The peer sent a larger message than is supported on the link.
    LinkMessageSizeExceeded = b"amqp:link:message-size-exceeded"
    #: The address provided cannot be resolved to a terminus at the current container.
    LinkRedirect = b"amqp:link:redirect"
    #: The link has been attached elsewhere, causing the existing attachment to be forcibly closed.
    LinkStolen = b"amqp:link:stolen"

    # Customized symbols used to indicate client error conditions.
    # TODO: check whether Client/Unknown/Vendor Error are exposed in EH/SB as users might be depending
    #  on the code for error handling
    ClientError = b"amqp:client-error"
    UnknownError = b"amqp:unknown-error"
    VendorError = b"amqp:vendor-error"
    SocketError = b"amqp:socket-error"


class RetryMode(str, Enum):
    EXPONENTIAL = 'exponential'
    FIXED = 'fixed'


class RetryPolicy:

    no_retry = [
        ErrorCondition.DecodeError,
        ErrorCondition.LinkMessageSizeExceeded,
        ErrorCondition.NotFound,
        ErrorCondition.NotImplemented,
        ErrorCondition.LinkRedirect,
        ErrorCondition.NotAllowed,
        ErrorCondition.UnauthorizedAccess,
        ErrorCondition.LinkStolen,
        ErrorCondition.ResourceLimitExceeded,
        ErrorCondition.ConnectionRedirect,
        ErrorCondition.PreconditionFailed,
        ErrorCondition.InvalidField,
        ErrorCondition.ResourceDeleted,
        ErrorCondition.IllegalState,
        ErrorCondition.FrameSizeTooSmall,
        ErrorCondition.ConnectionFramingError,
        ErrorCondition.SessionUnattachedHandle,
        ErrorCondition.SessionHandleInUse,
        ErrorCondition.SessionErrantLink,
        ErrorCondition.SessionWindowViolation
    ]

    def __init__(
        self,
        **kwargs
    ):
        """
        keyword int retry_total:
        keyword float retry_backoff_factor:
        keyword float retry_backoff_max:
        keyword RetryMode retry_mode:
        keyword list no_retry:
        keyword dict custom_retry_policy:
        """
        self.total_retries = kwargs.pop('retry_total', 3)
        # TODO: A. consider letting retry_backoff_factor be either a float or a callback obj which returns a float
        #  to give more extensibility on customization of retry backoff time, the callback could take the exception
        #  as input.
        self.backoff_factor = kwargs.pop('retry_backoff_factor', 0.8)
        self.backoff_max = kwargs.pop('retry_backoff_max', 120)
        self.retry_mode = kwargs.pop('retry_mode', RetryMode.EXPONENTIAL)
        self.no_retry.extend(kwargs.get('no_retry', []))
        self.custom_condition_backoff = kwargs.pop("custom_condition_backoff", None)
        # TODO: B. As an alternative of option A, we could have a new kwarg serve the goal

    def configure_retries(self, **kwargs):
        return {
            'total': kwargs.pop("retry_total", self.total_retries),
            'backoff': kwargs.pop("retry_backoff_factor", self.backoff_factor),
            'max_backoff': kwargs.pop("retry_backoff_max", self.backoff_max),
            'retry_mode': kwargs.pop("retry_mode", self.retry_mode),
            'history': []
        }

    def increment(self, settings, error):
        settings['total'] -= 1
        settings['history'].append(error)
        if settings['total'] < 0:
            return False
        return True

    def is_retryable(self, error):
        try:
            if error.condition in self.no_retry:
                return False
        except TypeError:
            pass
        return True

    def get_backoff_time(self, settings, error):
        try:
            return self.custom_condition_backoff[error.condition]
        except (KeyError, TypeError):
            pass

        consecutive_errors_len = len(settings['history'])
        if consecutive_errors_len <= 1:
            return 0

        if self.retry_mode == RetryMode.FIXED:
            backoff_value = settings['backoff']
        else:
            backoff_value = settings['backoff'] * (2 ** (consecutive_errors_len - 1))
        return min(settings['max_backoff'], backoff_value)


class AMQPError(Performative):
    _code: int = 0x0000001d
    _definition: List[FIELD] = [
        FIELD(AMQPTypes.symbol, False),
        FIELD(AMQPTypes.string, False),
        FIELD(FieldDefinition.fields, False),
    ]
    condition: AnyStr
    description: Optional[AnyStr] = None
    into: Optional[Dict[AnyStr, AMQP_STRUCTURED_TYPES]] = None


class AMQPException(Exception):
    """Base exception for all errors.

    :param bytes condition: The error code.
    :keyword str description: A description of the error.
    :keyword dict info: A dictionary of additional data associated with the error.
    """
    def __init__(self, condition, **kwargs):
        self.condition = condition or ErrorCondition.UnknownError
        self.description = kwargs.get("description", None)
        self.info = kwargs.get("info", None)
        self.message = kwargs.get("message", None)
        self.inner_error = kwargs.get("error", None)
        message = self.message or "Error condition: {}".format(
            str(condition) if isinstance(condition, ErrorCondition) else condition.decode()
        )
        if self.description:
            try:
                message += "\n Error Description: {}".format(self.description.decode())
            except (TypeError, AttributeError):
                message += "\n Error Description: {}".format(self.description)
        super(AMQPException, self).__init__(message)


class AMQPDecodeError(AMQPException):
    """An error occurred while decoding an incoming frame.

    """


class AMQPConnectionError(AMQPException):
    """Details of a Connection-level error.

    """


class AMQPConnectionRedirect(AMQPConnectionError):
    """Details of a Connection-level redirect response.

    The container is no longer available on the current connection.
    The peer should attempt reconnection to the container using the details provided.

    :param bytes condition: The error code.
    :keyword str description: A description of the error.
    :keyword dict info: A dictionary of additional data associated with the error.
    """
    def __init__(self, condition, description=None, info=None):
        self.hostname = info.get(b'hostname', b'').decode('utf-8')
        self.network_host = info.get(b'network-host', b'').decode('utf-8')
        self.port = int(info.get(b'port', SECURE_PORT))
        super(AMQPConnectionRedirect, self).__init__(condition, description=description, info=info)


class AMQPSessionError(AMQPException):
    """Details of a Session-level error.

    :param bytes condition: The error code.
    :keyword str description: A description of the error.
    :keyword dict info: A dictionary of additional data associated with the error.
    """


class AMQPLinkError(AMQPException):
    """

    """


class AMQPLinkRedirect(AMQPLinkError):
    """Details of a Link-level redirect response.

    The address provided cannot be resolved to a terminus at the current container.
    The supplied information may allow the client to locate and attach to the terminus.

    :param bytes condition: The error code.
    :keyword str description: A description of the error.
    :keyword dict info: A dictionary of additional data associated with the error.
    """

    def __init__(self, condition, description=None, info=None):
        self.hostname = info.get(b'hostname', b'').decode('utf-8')
        self.network_host = info.get(b'network-host', b'').decode('utf-8')
        self.port = int(info.get(b'port', SECURE_PORT))
        self.address = info.get(b'address', b'').decode('utf-8')
        super(AMQPLinkError, self).__init__(condition, description=description, info=info)


class AuthenticationException(AMQPException):
    """

    """


class TokenExpired(AuthenticationException):
    """

    """


class TokenAuthFailure(AuthenticationException):
    """

    """
    def __init__(self, status_code, status_description, **kwargs):
        encoding = kwargs.get("encoding", 'utf-8')
        self.status_code = status_code
        self.status_description = status_description
        message = "CBS Token authentication failed.\nStatus code: {}".format(self.status_code)
        if self.status_description:
            try:
                message += "\nDescription: {}".format(self.status_description.decode(encoding))
            except (TypeError, AttributeError):
                message += "\nDescription: {}".format(self.status_description)
        super(TokenAuthFailure, self).__init__(condition=ErrorCondition.ClientError, message=message)


class MessageException(AMQPException):
    """

    """


class MessageSendFailed(MessageException):
    """

    """


class ErrorResponse(object):
    """
    """
    def __init__(self, **kwargs):
        self.condition = kwargs.get("condition")
        self.description = kwargs.get("description")

        info = kwargs.get("info")
        error_info = kwargs.get("error_info")
        if isinstance(error_info, list) and len(error_info) >= 1:
            if isinstance(error_info[0], list) and len(error_info[0]) >= 1:
                self.condition = error_info[0][0]
                if len(error_info[0]) >= 2:
                    self.description = error_info[0][1]
                if len(error_info[0]) >= 3:
                    info = error_info[0][2]

        self.info = info
        self.error = error_info
