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
        self._expires_in = None
        self._expires_on = None
        self._token = None

        self._refresh_window = None

        self._token_status_code = None
        self._token_status_description = None

        self.state = CbsState.CLOSED
        self.auth_state = CbsAuthState.Idle

    def _put_token(self, token, token_type, audience, expires_on=None):
        # type: (str, str, str, datetime) -> None
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
            _LOGGER.info("Unexpected AMQP management open complete.")
        elif self.state == CbsState.OPEN:
            self.state = CbsState.ERROR
            _LOGGER.info("Unexpected AMQP management open complete in OPEN,"
                         "CBS error occurred on connection %r.", self._connection._container_id)
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
            _LOGGER.info("CBS for connection %r completed opening with status: %r",
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
            self.auth_state = CbsAuthState.Ok
        elif execute_operation_result == ManagementExecuteOperationResult.ERROR:
            self.auth_state = CbsAuthState.Error
            # put-token-message sending failure, rejected
            self._token_status_code = 0
            self._token_status_description = "Auth message has been rejected."
        elif execute_operation_result == ManagementExecuteOperationResult.FAILED_BAD_STATUS:
            self.auth_state = CbsAuthState.Error

    def _update_status(self):
        if self.state == CbsAuthState.Ok or self.state == CbsAuthState.RefreshRequired:
            is_expired, is_refresh_required = self._check_expiration_and_refresh_status()
            if is_expired:
                self.state = CbsAuthState.Expired
            elif is_refresh_required:
                self.state = CbsAuthState.RefreshRequired
        elif self.state == CbsAuthState.InProgress:
            put_timeout = self._check_put_timeout_status()
            if put_timeout:
                self.state = CbsAuthState.Timeout

    def _check_expiration_and_refresh_status(self):
        seconds_since_epoc = int(utc_now().timestamp())
        is_expired = seconds_since_epoc >= self._expires_on
        is_refresh_required = (self._expires_on - seconds_since_epoc) <= self._refresh_window
        return is_expired, is_refresh_required

    def _check_put_timeout_status(self):
        if self._auth_timeout > 0:
            return (int(utc_now().timestamp()) - self._token_put_time) >= self._auth_timeout
        else:
            return False

    def _cbs_link_ready(self):
        if self.state == CbsState.OPEN:
            return True
        if self.state != CbsState.OPEN:
            return False
        if self.state in (CbsState.CLOSED, CbsState.ERROR):
            # TODO: raise proper error type
            raise AuthenticationException("CBS authentication link is in broken status, please recreate the cbs link.")

    def open(self):
        self.state = CbsState.OPENING
        self._mgmt_link.open()

    def close(self):
        self._mgmt_link.close()
        self.state = CbsState.CLOSED

    def update_token(self):
        self.auth_state = CbsAuthState.InProgress
        access_token = self._auth.get_token()
        self._expires_on = access_token.expires_on
        self._expires_in = self._expires_on - int(utc_now().timestamp())
        self._refresh_window = int(float(self._expires_in) * 0.1)
        self._token = access_token.token
        self._token_put_time = int(utc_now().timestamp())
        self._put_token(self._token, self._auth.token_type, self._auth.audience, utc_from_timestamp(self._expires_on))

    def handle_token(self):
        if not self._cbs_link_ready():
            return False
        self._update_status()
        if self.auth_state == CbsAuthState.Idle:
            self.update_token()
            return False
        elif self.auth_state == CbsAuthState.InProgress:
            return False
        elif self.auth_state == CbsAuthState.Ok:
            return True
        elif self.auth_state == CbsAuthState.RefreshRequired:
            _LOGGER.info("Token on connection %r will expire soon - attempting to refresh.",
                         self._connection._container_id)
            self.update_token()
            return False
        elif self.auth_state == CbsAuthState.Failure:
            raise AuthenticationException("Failed to open CBS authentication link.")
        elif self.auth_state == CbsAuthState.Error:
            raise TokenAuthFailure(self._token_status_code, self._token_status_description, self._encoding)
        elif self.auth_state == CbsAuthState.Timeout:
            raise TimeoutError("Authentication attempt timed-out.")  # TODO: compat 2.7 timeout error?
        elif self.auth_state == CbsAuthState.Expired:
            raise TokenExpired("CBS Authentication Expired.")
