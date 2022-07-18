#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#-------------------------------------------------------------------------

import logging
import asyncio
from datetime import datetime

from ._management_link_async import ManagementLink
from ..utils import utc_now, utc_from_timestamp
from ..message import Message, Properties
from ..error import (
    AuthenticationException,
    TokenAuthFailure,
    TokenExpired,
    ErrorCondition
)
from ..constants import (
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
from ..cbs import (
    check_put_timeout_status,
    check_expiration_and_refresh_status
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

    async def _put_token(self, token, token_type, audience, expires_on=None):
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
        await self._mgmt_link.execute_operation(
            message,
            self._on_execute_operation_complete,
            timeout=self._auth_timeout,
            operation=CBS_PUT_TOKEN,
            type=token_type
        )
        self._mgmt_link.next_message_id += 1

    async def _on_amqp_management_open_complete(self, management_open_result):
        if self.state in (CbsState.CLOSED, CbsState.ERROR):
            _LOGGER.debug("Unexpected AMQP management open complete.")
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

    async def _on_amqp_management_error(self):
        # TODO: review the logging information, adjust level/information
        #  this should be applied to overall logging
        if self.state == CbsState.CLOSED:
            _LOGGER.debug("Unexpected AMQP error in CLOSED state.")
        elif self.state == CbsState.OPENING:
            self.state = CbsState.ERROR
            await self._mgmt_link.close()
            _LOGGER.info("CBS for connection %r failed to open with status: %r",
                         self._connection._container_id, ManagementOpenResult.ERROR)
        elif self.state == CbsState.OPEN:
            self.state = CbsState.ERROR
            _LOGGER.info("CBS error occurred on connection %r.", self._connection._container_id)

    async def _on_execute_operation_complete(
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

    async def _update_status(self):
        if self.state == CbsAuthState.OK or self.state == CbsAuthState.REFRESH_REQUIRED:
            is_expired, is_refresh_required = check_expiration_and_refresh_status(self._expires_on, self._refresh_window)
            if is_expired:
                self.state = CbsAuthState.EXPIRED
            elif is_refresh_required:
                self.state = CbsAuthState.REFRESH_REQUIRED
        elif self.state == CbsAuthState.IN_PROGRESS:
            put_timeout = check_put_timeout_status(self._auth_timeout, self._token_put_time)
            if put_timeout:
                self.state = CbsAuthState.TIMEOUT

    async def _cbs_link_ready(self):
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

    async def open(self):
        self.state = CbsState.OPENING
        await self._mgmt_link.open()

    async def close(self):
        await self._mgmt_link.close()
        self.state = CbsState.CLOSED

    async def update_token(self):
        self.auth_state = CbsAuthState.IN_PROGRESS
        access_token = await self._auth.get_token()
        if not access_token.token:
            _LOGGER.debug("update_token received an empty token")
        self._expires_on = access_token.expires_on
        expires_in = self._expires_on - int(utc_now().timestamp())
        self._refresh_window = int(float(expires_in) * 0.1)
        try:
            self._token = access_token.token.decode()
        except AttributeError:
            self._token = access_token.token
        self._token_put_time = int(utc_now().timestamp())
        await self._put_token(self._token, self._auth.token_type, self._auth.audience, utc_from_timestamp(self._expires_on))

    async def handle_token(self):
        if not (await self._cbs_link_ready()):
            return False
        await self._update_status()
        if self.auth_state == CbsAuthState.IDLE:
            await self.update_token()
            return False
        elif self.auth_state == CbsAuthState.IN_PROGRESS:
            return False
        elif self.auth_state == CbsAuthState.OK:
            return True
        elif self.auth_state == CbsAuthState.REFRESH_REQUIRED:
            _LOGGER.info("Token on connection %r will expire soon - attempting to refresh.",
                         self._connection._container_id)
            await self.update_token()
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
