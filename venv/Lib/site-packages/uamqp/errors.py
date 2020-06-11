#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import six
from uamqp import c_uamqp, constants, utils


def _process_send_error(policy, condition, description=None, info=None):
    try:
        amqp_condition = constants.ErrorCodes(condition)
    except ValueError:
        exception = MessageException(condition, description, info)
        exception.action = policy.on_unrecognized_error(exception)
    else:
        exception = MessageSendFailed(amqp_condition, description, info)
        exception.action = policy.on_message_error(exception)
    return exception


def _process_link_error(policy, condition, description=None, info=None):
    try:
        amqp_condition = constants.ErrorCodes(condition)
    except ValueError:
        exception = VendorLinkDetach(condition, description, info)
        exception.action = policy.on_unrecognized_error(exception)
    else:
        if amqp_condition == constants.ErrorCodes.LinkRedirect:
            exception = LinkRedirect(amqp_condition, description, info)
        else:
            exception = LinkDetach(amqp_condition, description, info)
        exception.action = policy.on_link_error(exception)
    return exception


def _process_connection_error(policy, condition, description=None, info=None):
    try:
        amqp_condition = constants.ErrorCodes(condition)
    except ValueError:
        exception = VendorConnectionClose(condition, description, info)
        exception.action = policy.on_unrecognized_error(exception)
    else:
        exception = ConnectionClose(amqp_condition, description, info)
        exception.action = policy.on_connection_error(exception)
    return exception


class ErrorAction(object):

    retry = True
    fail = False

    def __init__(self, retry, backoff=0, increment_retries=True):
        self.retry = bool(retry)
        self.backoff = backoff
        self.increment_retries = increment_retries


class ErrorPolicy(object):

    no_retry = (
        constants.ErrorCodes.DecodeError,
        constants.ErrorCodes.LinkMessageSizeExceeded,
        constants.ErrorCodes.NotFound,
        constants.ErrorCodes.NotImplemented,
        constants.ErrorCodes.LinkRedirect,
        constants.ErrorCodes.NotAllowed,
        constants.ErrorCodes.UnauthorizedAccess,
        constants.ErrorCodes.LinkStolen,
        constants.ErrorCodes.ResourceLimitExceeded,
        constants.ErrorCodes.ConnectionRedirect,
        constants.ErrorCodes.PreconditionFailed,
        constants.ErrorCodes.InvalidField,
        constants.ErrorCodes.ResourceDeleted,
        constants.ErrorCodes.IllegalState,
        constants.ErrorCodes.FrameSizeTooSmall,
        constants.ErrorCodes.ConnectionFramingError,
        constants.ErrorCodes.SessionUnattachedHandle,
        constants.ErrorCodes.SessionHandleInUse,
        constants.ErrorCodes.SessionErrantLink,
        constants.ErrorCodes.SessionWindowViolation
    )

    def __init__(self, max_retries=3, on_error=None):
        self.max_retries = max_retries
        self._on_error = on_error

    def on_unrecognized_error(self, error):
        if self._on_error:
            return self._on_error(error)
        return ErrorAction(retry=True)

    def on_message_error(self, error):
        if error.condition in self.no_retry:
            return ErrorAction(retry=False)
        return ErrorAction(retry=True, increment_retries=True)

    def on_link_error(self, error):
        if error.condition in self.no_retry:
            return ErrorAction(retry=False)
        return ErrorAction(retry=True)

    def on_connection_error(self, error):
        if error.condition in self.no_retry:
            return ErrorAction(retry=False)
        if error.condition == constants.ErrorCodes.ConnectionCloseForced:
            return ErrorAction(retry=True)
        return ErrorAction(retry=True)


class AMQPError(Exception):
    pass


class AMQPClientShutdown(KeyboardInterrupt):

    def __init__(self):
        message = "Client shutdown with keyboard interrupt."
        super(AMQPClientShutdown, self).__init__(message)


class AMQPConnectionError(AMQPError):
    pass


class MessageHandlerError(AMQPConnectionError):
    pass


class ConnectionClose(AMQPConnectionError):

    def __init__(self, condition, description=None, info=None, encoding="UTF-8"):
        self._encoding = encoding
        self.condition = condition
        self.description = description
        self.info = info
        self.action = None
        message = six.text_type(condition) if isinstance(condition, constants.ErrorCodes) \
            else condition.decode(encoding)
        if self.description:
            if isinstance(self.description, six.text_type):
                message += u": {}".format(self.description)
            else:
                message += u": {}".format(self.description.decode(self._encoding))
        super(ConnectionClose, self).__init__(message)


class VendorConnectionClose(ConnectionClose):
    pass


class LinkDetach(AMQPConnectionError):

    def __init__(self, condition, description=None, info=None, encoding="UTF-8"):
        self._encoding = encoding
        self.condition = condition
        self.description = description
        self.info = info
        self.action = None
        message = six.text_type(condition) if isinstance(condition, constants.ErrorCodes) \
            else condition.decode(encoding)
        if self.description:
            if isinstance(self.description, six.text_type):
                message += u": {}".format(self.description)
            else:
                message += u": {}".format(self.description.decode(self._encoding))
        super(LinkDetach, self).__init__(message)


class VendorLinkDetach(LinkDetach):
    pass


class LinkRedirect(LinkDetach):

    def __init__(self, condition, description=None, info=None, encoding="UTF-8"):
        self.hostname = info.get(b'hostname')
        self.network_host = info.get(b'network-host')
        self.port = info.get(b'port')
        self.address = info.get(b'address')
        self.scheme = info.get(b'scheme')
        self.path = info.get(b'path')
        super(LinkRedirect, self).__init__(condition, description, info, encoding)


class ClientTimeout(AMQPError):
    pass


class AuthenticationException(AMQPError):
    pass


class TokenExpired(AuthenticationException):
    pass


class TokenAuthFailure(AuthenticationException):

    def __init__(self, status_code, description, encoding="UTF-8"):
        self._encoding = encoding
        self.status_code = status_code
        self.description = description
        message = "CBS Token authentication failed.\nStatus code: {}".format(self.status_code)
        if self.description:
            if isinstance(self.description, six.text_type):
                message += u"\nDescription: {}".format(self.description)
            else:
                message += u"\nDescription: {}".format(self.description.decode(self._encoding))
        super(TokenAuthFailure, self).__init__(message)


class MessageResponse(AMQPError):

    def __init__(self, message=None):
        response = message or "Sending {} disposition.".format(self.__class__.__name__)
        super(MessageResponse, self).__init__(response)


class MessageException(MessageResponse):

    def __init__(self, condition, description=None, info=None, encoding="UTF-8"):
        self._encoding = encoding
        self.condition = condition
        self.description = description
        self.info = info
        self.action = None
        message = six.text_type(condition) if isinstance(condition, constants.ErrorCodes) \
            else condition.decode(encoding)
        if self.description:
            if isinstance(self.description, six.text_type):
                message += u": {}".format(self.description)
            else:
                message += u": {}".format(self.description.decode(self._encoding))
        super(MessageException, self).__init__(message=message)


class MessageSendFailed(MessageException):
    pass


class ClientMessageError(MessageException):

    def __init__(self, exception, info=None):
        if hasattr(exception, 'condition'):
            condition = exception.condition
            description = exception.description
        else:
            condition = constants.ErrorCodes.ClientError
            description = str(exception)
        super(ClientMessageError, self).__init__(condition, description=description, info=info)


class MessageAlreadySettled(MessageResponse):

    def __init__(self):
        response = "Invalid operation: this message is already settled."
        super(MessageAlreadySettled, self).__init__(response)


class MessageAccepted(MessageResponse):
    pass


class MessageRejected(MessageResponse):

    def __init__(self, condition=None, description=None, encoding='UTF-8', info=None):
        if condition:
            self.error_condition = condition.encode(encoding) if isinstance(condition, six.text_type) else condition
        else:
            self.error_condition = b"amqp:internal-error"
        self.error_description = None
        if description:
            self.error_description = description.encode(encoding) if isinstance(description, six.text_type) \
                else description
        else:
            self.error_description = b""
        if info and not isinstance(info, dict):
            raise TypeError("Disposition error info must be a dictionary.")
        self.error_info = utils.data_factory(info, encoding=encoding) if info else None
        super(MessageRejected, self).__init__()


class MessageReleased(MessageResponse):
    pass


class MessageModified(MessageResponse):

    def __init__(self, failed, undeliverable, annotations=None, encoding='UTF-8'):
        self.failed = failed
        self.undeliverable = undeliverable
        if annotations and not isinstance(annotations, dict):
            raise TypeError("Disposition annotations must be a dictionary.")
        self.annotations = utils.data_factory(annotations, encoding=encoding) if annotations else None
        super(MessageModified, self).__init__()


class ErrorResponse(object):

    def __init__(self, error_info=None, condition=None, description=None, info=None):
        info = None
        self.condition = condition
        self.description = description
        self.info = info
        self.error = error_info
        if isinstance(error_info, c_uamqp.cError):
            self.condition = error_info.condition
            self.description = error_info.description
            info = error_info.info
        elif isinstance(error_info, list) and len(error_info) >= 1:
            if isinstance(error_info[0], list) and len(error_info[0]) >= 1:
                self.condition = error_info[0][0]
                if len(error_info[0]) >= 2:
                    self.description = error_info[0][1]
                if len(error_info[0]) >= 3:
                    info = error_info[0][2]
        try:
            self.info = info.value
        except AttributeError:
            self.info = info


class MessageContentTooLarge(ValueError):
    def __init__(self):
        message = "Data set too large for a single message."
        super(MessageContentTooLarge, self).__init__(message)
