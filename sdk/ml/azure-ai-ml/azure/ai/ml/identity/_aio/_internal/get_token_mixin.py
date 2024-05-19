# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import abc
import logging
import time
from typing import TYPE_CHECKING, Any, Optional

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

from ..._constants import DEFAULT_REFRESH_OFFSET, DEFAULT_TOKEN_REFRESH_RETRY_DELAY

if TYPE_CHECKING:
    from azure.core.credentials import AccessToken

_LOGGER = logging.getLogger(__name__)


class GetTokenMixin(abc.ABC):
    def __init__(self, *args: "Any", **kwargs: "Any") -> None:
        self._last_request_time = 0

        # https://github.com/python/mypy/issues/5887
        super(GetTokenMixin, self).__init__(*args, **kwargs)

    @abc.abstractmethod
    # pylint: disable-next=docstring-missing-param
    async def _acquire_token_silently(self, *scopes: str, **kwargs: "Any") -> "Optional[AccessToken]":
        """Attempt to acquire an access token from a cache or by redeeming a refresh token."""

    @abc.abstractmethod
    # pylint: disable-next=docstring-missing-param
    async def _request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        """Request an access token from the STS."""

    def _should_refresh(self, token: "AccessToken") -> bool:
        now = int(time.time())
        if token.expires_on - now > DEFAULT_REFRESH_OFFSET:
            return False
        if now - self._last_request_time < DEFAULT_TOKEN_REFRESH_RETRY_DELAY:
            return False
        return True

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param scopes: Scopes to request access for
        :type: str
        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
            required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
        :return: The access token
        :rtype: ~azure.core.credentials.AccessToken
        """
        if not scopes:
            msg = '"get_token" requires at least one scope'
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.IDENTITY,
                error_category=ErrorCategory.USER_ERROR,
            )

        try:
            token = await self._acquire_token_silently(*scopes, **kwargs)
            if not token:
                self._last_request_time = int(time.time())
                token = await self._request_token(*scopes, **kwargs)
            elif self._should_refresh(token):
                try:
                    self._last_request_time = int(time.time())
                    token = await self._request_token(*scopes, **kwargs)
                except Exception:  # pylint:disable=broad-except
                    pass
            _LOGGER.log(
                logging.INFO,
                "%s.get_token succeeded",
                self.__class__.__name__,
            )
            return token

        except Exception as ex:
            _LOGGER.log(
                logging.WARNING,
                "%s.get_token failed: %s",
                self.__class__.__name__,
                ex,
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise
