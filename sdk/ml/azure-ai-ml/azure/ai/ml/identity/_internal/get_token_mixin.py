# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import abc
import logging
import time
from typing import Any, Optional

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

from .._constants import DEFAULT_REFRESH_OFFSET, DEFAULT_TOKEN_REFRESH_RETRY_DELAY

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

_LOGGER = logging.getLogger(__name__)


class GetTokenMixin(ABC):
    from azure.core.credentials import AccessToken

    def __init__(self, *args: Any, **kwargs: Any):
        self._last_request_time = 0

        # https://github.com/python/mypy/issues/5887
        super(GetTokenMixin, self).__init__(*args, **kwargs)

    @abc.abstractmethod
    # pylint: disable-next=docstring-missing-param
    def _acquire_token_silently(self, *scopes: str, **kwargs: Any) -> Optional[AccessToken]:
        """Attempt to acquire an access token from a cache or by redeeming a refresh token."""

    @abc.abstractmethod
    # pylint: disable-next=docstring-missing-param
    def _request_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        """Request an access token from the STS."""

    def _should_refresh(self, token: AccessToken) -> bool:
        now = int(time.time())
        if token.expires_on - now > DEFAULT_REFRESH_OFFSET:
            return False
        if now - self._last_request_time < DEFAULT_TOKEN_REFRESH_RETRY_DELAY:
            return False
        return True

    # pylint: disable-next=docstring-missing-return
    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param scopes: The desired scopes for the access token. This method requires at least one scope.
        :type scopes: str
        :return: The access token
        :rtype: ~azure.core.credentials.AccessToken
        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
            required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
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
            token = self._acquire_token_silently(*scopes, **kwargs)
            if not token:
                self._last_request_time = int(time.time())
                token = self._request_token(*scopes, **kwargs)
            elif self._should_refresh(token):
                try:
                    self._last_request_time = int(time.time())
                    token = self._request_token(*scopes, **kwargs)
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
