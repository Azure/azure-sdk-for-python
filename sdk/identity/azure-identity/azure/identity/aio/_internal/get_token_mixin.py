# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import asyncio  # pylint: disable=do-not-import-asyncio
import logging
import random
import threading
import time
import weakref
from typing import Any, Dict, Optional, Tuple

from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from ..._constants import (
    DEFAULT_REFRESH_OFFSET,
    DEFAULT_TOKEN_REFRESH_RETRY_DELAY,
    DEFAULT_TOKEN_LOCK_TIMEOUT,
    DEFAULT_TOKEN_LOCK_TIMEOUT_VARIANCE,
)
from ..._internal import within_credential_chain

_LOGGER = logging.getLogger(__name__)


class GetTokenMixin(abc.ABC):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._last_request_time = 0
        # Outer WeakKeyDictionary: keyed by event loop, auto-removed when a loop is GC'd.
        # Inner WeakValueDictionary: locks are removed when no caller holds a strong reference,
        # preventing unbounded growth from arbitrary scope combinations.
        self._locks: weakref.WeakKeyDictionary[
            asyncio.AbstractEventLoop, weakref.WeakValueDictionary[Tuple, asyncio.Lock]
        ] = weakref.WeakKeyDictionary()
        self._lock_guard = threading.Lock()

        # https://github.com/python/mypy/issues/5887
        super(GetTokenMixin, self).__init__(*args, **kwargs)  # type: ignore

    @abc.abstractmethod
    async def _acquire_token_silently(self, *scopes: str, **kwargs) -> Optional[AccessTokenInfo]:
        """Attempt to acquire an access token from a cache or by redeeming a refresh token.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.

        :return: An access token with the desired scopes if successful; otherwise, None.
        :rtype: ~azure.core.credentials.AccessTokenInfo or None
        """

    @abc.abstractmethod
    async def _request_token(self, *scopes: str, **kwargs) -> AccessTokenInfo:
        """Request an access token from the STS.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessTokenInfo
        """

    def _should_refresh(self, token: AccessTokenInfo) -> bool:
        now = int(time.time())
        if token.refresh_on is not None and now >= token.refresh_on:
            return True
        if token.expires_on - now > DEFAULT_REFRESH_OFFSET:
            return False
        if now - self._last_request_time < DEFAULT_TOKEN_REFRESH_RETRY_DELAY:
            return False
        return True

    def _get_request_lock(
        self,
        scopes: Tuple[str, ...],
        claims: Optional[str],
        tenant_id: Optional[str],
        enable_cae: bool,
    ) -> Optional[asyncio.Lock]:
        # Only use locking in asyncio contexts. If we can't get a running loop
        # (e.g., trio), fall through to existing behavior without locking.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return None
        key = (scopes, claims, tenant_id, enable_cae)
        with self._lock_guard:
            if loop not in self._locks:
                self._locks[loop] = weakref.WeakValueDictionary()
            loop_locks = self._locks[loop]
            lock = loop_locks.get(key)
            if lock is None:
                lock = asyncio.Lock()
                loop_locks[key] = lock
            return lock

    async def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword str claims: additional claims required in the token, such as those returned in a resource provider's
            claims challenge following an authorization failure.
        :keyword str tenant_id: optional tenant to include in the token request.
        :keyword bool enable_cae: indicates whether to enable Continuous Access Evaluation (CAE) for the requested
            token. Defaults to False.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken
        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
            required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
        """
        options: TokenRequestOptions = {}
        if claims:
            options["claims"] = claims
        if tenant_id:
            options["tenant_id"] = tenant_id
        options["enable_cae"] = enable_cae

        token_info = await self._get_token_base(*scopes, options=options, base_method_name="get_token", **kwargs)
        return AccessToken(token_info.token, token_info.expires_on)

    async def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request an access token for `scopes`.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token. This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: ~azure.core.credentials.AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.
        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
            required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
        """
        return await self._get_token_base(*scopes, options=options, base_method_name="get_token_info")

    async def _get_token_base(
        self,
        *scopes: str,
        options: Optional[TokenRequestOptions] = None,
        base_method_name: str = "get_token_info",
        **kwargs: Any,
    ) -> AccessTokenInfo:
        if not scopes:
            raise ValueError(f'"{base_method_name}" requires at least one scope')

        options = options or {}
        claims = options.get("claims")
        tenant_id = options.get("tenant_id")
        enable_cae = options.get("enable_cae", False)

        lock = self._get_request_lock(tuple(sorted(scopes)), claims, tenant_id, enable_cae)
        lock_acquired = False

        if lock is not None:
            jitter = DEFAULT_TOKEN_LOCK_TIMEOUT * DEFAULT_TOKEN_LOCK_TIMEOUT_VARIANCE
            timeout = max(0.0, random.uniform(DEFAULT_TOKEN_LOCK_TIMEOUT - jitter, DEFAULT_TOKEN_LOCK_TIMEOUT + jitter))
            try:
                await asyncio.wait_for(lock.acquire(), timeout=timeout)
                lock_acquired = True
            except asyncio.TimeoutError:
                _LOGGER.warning(
                    "%s.%s lock acquisition timed out after %s seconds; proceeding with token request",
                    self.__class__.__name__,
                    base_method_name,
                    timeout,
                )

        try:
            token = await self._acquire_token_silently(
                *scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs
            )
            if not token:
                self._last_request_time = int(time.time())
                token = await self._request_token(
                    *scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs
                )
            elif self._should_refresh(token):
                try:
                    self._last_request_time = int(time.time())
                    token = await self._request_token(
                        *scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs
                    )
                except Exception:  # pylint:disable=broad-except
                    pass
            _LOGGER.log(
                logging.DEBUG if within_credential_chain.get() else logging.INFO,
                "%s.%s succeeded",
                self.__class__.__name__,
                base_method_name,
            )
            return token

        except Exception as ex:
            _LOGGER.log(
                logging.DEBUG if within_credential_chain.get() else logging.WARNING,
                "%s.%s failed: %s",
                self.__class__.__name__,
                base_method_name,
                ex,
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise

        finally:
            if lock is not None and lock_acquired:
                lock.release()

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        # asyncio.Lock and threading.Lock are not picklable; exclude them.
        state.pop("_locks", None)
        state.pop("_lock_guard", None)
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)  # type: ignore
        self._locks = weakref.WeakKeyDictionary()
        self._lock_guard = threading.Lock()
