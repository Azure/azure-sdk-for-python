#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#-------------------------------------------------------------------------

import logging
from datetime import datetime

from .utils import utc_now, utc_from_timestamp
from .management_link import ManagementLink
from .message import Message, Properties
from .error import (
    AuthenticationException,
    ErrorCondition,
    TokenAuthFailure,
    TokenExpired
)
from .constants import (
    CbsState,
    CbsAuthState,
    CBS_PUT_TOKEN,
    CBS_EXPIRATION,
    CBS_NAME,
    CBS_TYPE,
    CBS_OPERATION,
    ManagementExecuteOperationResult,
    ManagementOpenResult,
    DEFAULT_AUTH_TIMEOUT
)

_LOGGER = logging.getLogger(__name__)


def check_expiration_and_refresh_status(expires_on, refresh_window):
    seconds_since_epoc = int(utc_now().timestamp())
    is_expired = seconds_since_epoc >= expires_on
    is_refresh_required = (expires_on - seconds_since_epoc) <= refresh_window
    return is_expired, is_refresh_required


def check_put_timeout_status(auth_timeout, token_put_time):
    if auth_timeout > 0:
        return (int(utc_now().timestamp()) - token_put_time) >= auth_timeout
    else:
        return False


class CBSAuthenticator(object):
    def __init__(
        self,
        session,
        auth,
        **kwargs
    ):
        self._session = session
        self._connection = self._session._connection
        self._mgmt_link = self._session.create_request_response_link_pair(
            endpoint='$cbs',
            on_amqp_management_open_complete=self._on_amqp_management_open_complete,
            on_amqp_management_error=self._on_amqp_management_error,
            status_code_field=b'status-code',
            status_description_field=b'status-description'
        )  # type: ManagementLink

        if not auth.get_token or not callable(auth.get_token):
            raise ValueError("get_token must be a callable object.")

        self._auth = auth
        self._encoding = 'UTF-8'
        self._auth_timeout = kwargs.pop('auth_timeout', DEFAULT_AUTH_TIMEOUT)
        self._token_put_time = None
        self._expires_on = None
        self._token = None
        self._refresh_window = None

        self._token_status_code = None
        self._token_status_description = None

        self.state = CbsState.CLOSED
        self.auth_state = CbsAuthState.IDLE

    def _put_token(self, token, token_type, audience, expires_on=None):
        # type: (str, str, str, datetime) -> None
        _LOGGER.debug('In put token, token_type: %r', token_type)
        message = Message(
            value=token,
            properties=Properties(message_id=self._mgmt_link.next_message_id),
            application_properties={
                CBS_NAME: audience,
                CBS_OPERATION: CBS_PUT_TOKEN,
                CBS_TYPE: token_type,
                CBS_EXPIRATION: expires_on
            }
        )
        _LOGGER.debug(
            'put token properties: %r \n put token app props: %r',
            message.properties,
            message.application_properties
        )
        self._mgmt_link.execute_operation(
            message,
            self._on_execute_operation_complete,
            timeout=self._auth_timeout,
            operation=CBS_PUT_TOKEN,
            type=token_type
        )
        self._mgmt_link.next_message_id += 1

    def _on_amqp_management_open_complete(self, management_open_result):
        if self.state in (CbsState.CLOSED, CbsState.ERROR):
            _LOGGER.debug("CSB with status: %r encounters unexpected AMQP management open complete.", self.state)
        elif self.state == CbsState.OPEN:
            self.state = CbsState.ERROR
            _LOGGER.info(
                "Unexpected AMQP management open complete in OPEN, CBS error occurred on connection %r.",
                self._connection._container_id
            )
        elif self.state == CbsState.OPENING:
            self.state = CbsState.OPEN if management_open_result == ManagementOpenResult.OK else CbsState.CLOSED
            _LOGGER.info("CBS for connection %r completed opening with status: %r",
                         self._connection._container_id, management_open_result)

    def _on_amqp_management_error(self):
        if self.state == CbsState.CLOSED:
            _LOGGER.info("Unexpected AMQP error in CLOSED state.")
        elif self.state == CbsState.OPENING:
            self.state = CbsState.ERROR
            self._mgmt_link.close()
            _LOGGER.info("CBS for connection %r failed to open with status: %r",
                         self._connection._container_id, ManagementOpenResult.ERROR)
        elif self.state == CbsState.OPEN:
            self.state = CbsState.ERROR
            _LOGGER.info("CBS error occurred on connection %r.", self._connection._container_id)

    def _on_execute_operation_complete(
            self,
            execute_operation_result,
            status_code,
            status_description,
            message,
            error_condition=None
    ):
        _LOGGER.info("CBS Put token result (%r), status code: %s, status_description: %s.",
                     execute_operation_result, status_code, status_description)
        self._token_status_code = status_code
        self._token_status_description = status_description

        if execute_operation_result == ManagementExecuteOperationResult.OK:
            self.auth_state = CbsAuthState.OK
        elif execute_operation_result == ManagementExecuteOperationResult.ERROR:
            self.auth_state = CbsAuthState.ERROR
            # put-token-message sending failure, rejected
            self._token_status_code = 0
            self._token_status_description = "Auth message has been rejected."
        elif execute_operation_result == ManagementExecuteOperationResult.FAILED_BAD_STATUS:
            self.auth_state = CbsAuthState.ERROR

    def _update_status(self):
        _LOGGER.debug('In update status.')
        if self.state == CbsAuthState.OK or self.state == CbsAuthState.REFRESH_REQUIRED:
            _LOGGER.debug('In refresh required or OK.')
            is_expired, is_refresh_required = check_expiration_and_refresh_status(self._expires_on, self._refresh_window)
            _LOGGER.debug('is expired == %r, is refresh required == %r', is_expired, is_refresh_required)
            if is_expired:
                self.state = CbsAuthState.EXPIRED
            elif is_refresh_required:
                self.state = CbsAuthState.REFRESH_REQUIRED
        elif self.state == CbsAuthState.IN_PROGRESS:
            _LOGGER.debug('In update status, in progress. token put time: %r', self._token_put_time)
            put_timeout = check_put_timeout_status(self._auth_timeout, self._token_put_time)
            if put_timeout:
                self.state = CbsAuthState.TIMEOUT

    def _cbs_link_ready(self):
        if self.state == CbsState.OPEN:
            return True
        if self.state != CbsState.OPEN:
            return False
        if self.state in (CbsState.CLOSED, CbsState.ERROR):
            # TODO: raise proper error type also should this be a ClientError?
            #  Think how upper layer handle this exception + condition code
            raise AuthenticationException(
                condition=ErrorCondition.ClientError,
                description="CBS authentication link is in broken status, please recreate the cbs link."
            )

    def open(self):
        self.state = CbsState.OPENING
        self._mgmt_link.open()

    def close(self):
        self._mgmt_link.close()
        self.state = CbsState.CLOSED

    def update_token(self):
        _LOGGER.debug('updating token...')
        _LOGGER.debug('auth state: %r', self.auth_state)
        _LOGGER.debug('state: %r', self.state)
        self.auth_state = CbsAuthState.IN_PROGRESS
        access_token = self._auth.get_token()
        self._expires_on = access_token.expires_on
        _LOGGER.debug('after token has been updated')
        _LOGGER.debug('current time: %r', datetime.now())
        _LOGGER.debug('token expiry: %r', datetime.fromtimestamp(self._expires_on))
        expires_in = self._expires_on - int(utc_now().timestamp())
        self._refresh_window = int(float(expires_in) * 0.1)
        _LOGGER.debug('refresh window: %r', self._refresh_window)
        try:
            self._token = access_token.token.decode()
        except AttributeError:
            self._token = access_token.token
        self._token_put_time = int(utc_now().timestamp())
        self._put_token(self._token, self._auth.token_type, self._auth.audience, utc_from_timestamp(self._expires_on))
        _LOGGER.debug('update token, after put token')

    def handle_token(self):
        _LOGGER.debug('Handling token. Auth state == %r', self.auth_state)
        if not self._cbs_link_ready():
            return False
        self._update_status()
        if self.auth_state == CbsAuthState.IDLE:
            self.update_token()
            return False
        elif self.auth_state == CbsAuthState.IN_PROGRESS:
            return False
        elif self.auth_state == CbsAuthState.OK:
            return True
        elif self.auth_state == CbsAuthState.REFRESH_REQUIRED:
            _LOGGER.info("Token on connection %r will expire soon - attempting to refresh.",
                         self._connection._container_id)
            self.update_token()
            return False
        elif self.auth_state == CbsAuthState.FAILURE:
            raise AuthenticationException(
                condition=ErrorCondition.InternalError,
                description="Failed to open CBS authentication link."
            )
        elif self.auth_state == CbsAuthState.ERROR:
            raise TokenAuthFailure(
                self._token_status_code,
                self._token_status_description,
                encoding=self._encoding  # TODO: drop off all the encodings
            )
        elif self.auth_state == CbsAuthState.TIMEOUT:
            raise TimeoutError("Authentication attempt timed-out.")
        elif self.auth_state == CbsAuthState.EXPIRED:
            raise TokenExpired(
                condition=ErrorCondition.InternalError,
                description="CBS Authentication Expired."
            )
