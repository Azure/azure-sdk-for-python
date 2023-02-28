# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import logging
from datetime import datetime
from typing import Optional

from ..utils import utc_now, utc_from_timestamp
from ._management_link_async import ManagementLink
from ..message import Message, Properties
from ..error import AuthenticationException, ErrorCondition, TokenAuthFailure, TokenExpired
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
)
from ..cbs import check_put_timeout_status, check_expiration_and_refresh_status

_LOGGER = logging.getLogger(__name__)


class CBSAuthenticator(object):  # pylint:disable=too-many-instance-attributes
    def __init__(self, session, auth, **kwargs):
        self._session = session
        self._connection = self._session._connection
        self._mgmt_link = self._session.create_request_response_link_pair(
            endpoint="$cbs",
            on_amqp_management_open_complete=self._on_amqp_management_open_complete,
            on_amqp_management_error=self._on_amqp_management_error,
            status_code_field=b"status-code",
            status_description_field=b"status-description",
        )  # type: ManagementLink

        # if not auth.get_token or not asyncio.iscoroutinefunction(auth.get_token):
        #    raise ValueError("get_token must be a coroutine object.")

        self._auth = auth
        self._encoding = 'UTF-8'
        self._auth_timeout = kwargs.get('auth_timeout')
        self._token_put_time = None
        self._expires_on = None
        self._token = None
        self._refresh_window = None
        self._network_trace_params = {
            "amqpConnection": self._session._connection._container_id,
            "amqpSession": self._session.name,
            "amqpLink": None
        }

        self._token_status_code = None
        self._token_status_description = None

        self.state = CbsState.CLOSED
        self.auth_state = CbsAuthState.IDLE

    async def _put_token(
        self,
        token: str,
        token_type: str,
        audience: str,
        expires_on: Optional[datetime] = None
    ) -> None:
        message = Message(  # type: ignore # TODO: missing positional args header, etc.
            value=token,
            properties=Properties(message_id=self._mgmt_link.next_message_id),  # type: ignore
            application_properties={
                CBS_NAME: audience,
                CBS_OPERATION: CBS_PUT_TOKEN,
                CBS_TYPE: token_type,
                CBS_EXPIRATION: expires_on,
            },
        )
        await self._mgmt_link.execute_operation(
            message,
            self._on_execute_operation_complete,
            timeout=self._auth_timeout,
            operation=CBS_PUT_TOKEN,
            type=token_type,
        )
        self._mgmt_link.next_message_id += 1

    async def _on_amqp_management_open_complete(self, management_open_result):
        if self.state in (CbsState.CLOSED, CbsState.ERROR):
            _LOGGER.debug(
                "CSB with status: %r encounters unexpected AMQP management open complete.",
                self.state,
                extra=self._network_trace_params
            )
        elif self.state == CbsState.OPEN:
            self.state = CbsState.ERROR
            _LOGGER.info(
                "Unexpected AMQP management open complete in OPEN, CBS error occurred.",
                extra=self._network_trace_params
            )
        elif self.state == CbsState.OPENING:
            self.state = CbsState.OPEN if management_open_result == ManagementOpenResult.OK else CbsState.CLOSED
            _LOGGER.info(
                "CBS completed opening with status: %r",
                management_open_result,
                extra=self._network_trace_params
            )

    async def _on_amqp_management_error(self):
        if self.state == CbsState.CLOSED:
            _LOGGER.debug("Unexpected AMQP error in CLOSED state.", extra=self._network_trace_params)
        elif self.state == CbsState.OPENING:
            self.state = CbsState.ERROR
            await self._mgmt_link.close()
            _LOGGER.info(
                "CBS failed to open with status: %r",
                ManagementOpenResult.ERROR,
                extra=self._network_trace_params
            )
        elif self.state == CbsState.OPEN:
            self.state = CbsState.ERROR
            _LOGGER.info("CBS error occurred.", extra=self._network_trace_params)

    async def _on_execute_operation_complete(
        self, execute_operation_result, status_code, status_description, _, error_condition=None
    ):
        if error_condition:
            _LOGGER.info(
                "CBS Put token error: %r",
                error_condition,
                extra=self._network_trace_params
            )
            self.auth_state = CbsAuthState.ERROR
            return
        _LOGGER.debug(
            "CBS Put token result (%r), status code: %s, status_description: %s.",
            execute_operation_result,
            status_code,
            status_description,
            extra=self._network_trace_params
        )
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
        if self.auth_state == CbsAuthState.OK or self.auth_state == CbsAuthState.REFRESH_REQUIRED:
            is_expired, is_refresh_required = check_expiration_and_refresh_status(
                self._expires_on, self._refresh_window
            )  # pylint:disable=line-too-long
            _LOGGER.debug(
                "CBS status check: state == %r, expired == %r, refresh required == %r",
                self.auth_state,
                is_expired,
                is_refresh_required,
                extra=self._network_trace_params
            )
            if is_expired:
                self.auth_state = CbsAuthState.EXPIRED
            elif is_refresh_required:
                self.auth_state = CbsAuthState.REFRESH_REQUIRED
        elif self.auth_state == CbsAuthState.IN_PROGRESS:
            _LOGGER.debug(
                "CBS update in progress. Token put time: %r",
                self._token_put_time,
                extra=self._network_trace_params
            )
            put_timeout = check_put_timeout_status(self._auth_timeout, self._token_put_time)
            if put_timeout:
                self.auth_state = CbsAuthState.TIMEOUT

    async def _cbs_link_ready(self):
        if self.state == CbsState.OPEN:
            return True
        if self.state != CbsState.OPEN:
            return False
        if self.state in (CbsState.CLOSED, CbsState.ERROR):
            raise TokenAuthFailure(
                status_code=ErrorCondition.ClientError,
                status_description="CBS authentication link is in broken status, please recreate the cbs link.",
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
        if not access_token:
            _LOGGER.info(
                "Token refresh function received an empty token object.",
                extra=self._network_trace_params
            )
        elif not access_token.token:
            _LOGGER.info(
                "Token refresh function received an empty token.",
                extra=self._network_trace_params
            )
        self._expires_on = access_token.expires_on
        expires_in = self._expires_on - int(utc_now().timestamp())
        self._refresh_window = int(float(expires_in) * 0.1)
        try:
            self._token = access_token.token.decode()
        except AttributeError:
            self._token = access_token.token
        try:
            token_type = self._auth.token_type.decode()
        except AttributeError:
            token_type = self._auth.token_type

        self._token_put_time = int(utc_now().timestamp())
        await self._put_token(
            self._token, token_type, self._auth.audience, utc_from_timestamp(self._expires_on)
        )

    async def handle_token(self):
        if not await self._cbs_link_ready():
            return False
        await self._update_status()
        if self.auth_state == CbsAuthState.IDLE:
            await self.update_token()
            return False
        if self.auth_state == CbsAuthState.IN_PROGRESS:
            return False
        if self.auth_state == CbsAuthState.OK:
            return True
        if self.auth_state == CbsAuthState.REFRESH_REQUIRED:
            _LOGGER.info(
                "Token will expire soon - attempting to refresh.",
                extra=self._network_trace_params
            )
            await self.update_token()
            return False
        if self.auth_state == CbsAuthState.FAILURE:
            raise AuthenticationException(
                condition=ErrorCondition.InternalError, description="Failed to open CBS authentication link."
            )
        if self.auth_state == CbsAuthState.ERROR:
            raise TokenAuthFailure(
                self._token_status_code,
                self._token_status_description,
                encoding=self._encoding,  # TODO: drop off all the encodings
            )
        if self.auth_state == CbsAuthState.TIMEOUT:
            raise TimeoutError("Authentication attempt timed-out.")
        if self.auth_state == CbsAuthState.EXPIRED:
            raise TokenExpired(condition=ErrorCondition.InternalError, description="CBS Authentication Expired.")
