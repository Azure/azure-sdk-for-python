# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Optional, Dict, cast, Union
import abc
import time
import logging

import msal
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .msal_client import MsalClient
from .utils import within_credential_chain
from .._internal import _scopes_to_resource
from .._exceptions import CredentialUnavailableError

_LOGGER = logging.getLogger(__name__)


class MsalManagedIdentityClient(abc.ABC):  # pylint:disable=client-accepts-api-version-keyword
    """Base class for managed identity client wrapping MSAL ManagedIdentityClient."""

    # pylint:disable=missing-client-constructor-parameter-credential
    def __init__(self, **kwargs: Any) -> None:
        self._settings = kwargs
        self._client = MsalClient(**kwargs)
        managed_identity = self.get_managed_identity(**kwargs)
        self._msal_client = msal.ManagedIdentityClient(managed_identity, http_client=self._client)

    def __enter__(self) -> "MsalManagedIdentityClient":
        self._client.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.__exit__(*args)

    @abc.abstractmethod
    def get_unavailable_message(self, desc: str = "") -> str:
        pass

    def close(self) -> None:
        self.__exit__()

    def _request_token(self, *scopes: str, **kwargs: Any) -> AccessToken:  # pylint:disable=unused-argument
        if not scopes:
            raise ValueError('"get_token" requires at least one scope')
        resource = _scopes_to_resource(*scopes)
        result = self._msal_client.acquire_token_for_client(resource=resource)
        now = int(time.time())
        if result and "access_token" in result and "expires_in" in result:
            return AccessToken(result["access_token"], now + int(result["expires_in"]))
        if result and "error" in result:
            error_desc = cast(str, result["error"])
        error_message = self.get_unavailable_message(error_desc)
        raise CredentialUnavailableError(error_message)

    def get_managed_identity(
        self, **kwargs: Any
    ) -> Union[msal.UserAssignedManagedIdentity, msal.SystemAssignedManagedIdentity]:
        """
        Get the managed identity configuration.
        :keyword str client_id: The client ID of the user-assigned managed identity.
        :keyword dict identity_config: The identity configuration.

        :rtype: msal.UserAssignedManagedIdentity or msal.SystemAssignedManagedIdentity
        :return: The managed identity configuration.
        """
        if "client_id" in kwargs and kwargs["client_id"]:
            return msal.UserAssignedManagedIdentity(client_id=kwargs["client_id"])
        identity_config = kwargs.pop("identity_config", None) or {}
        if "client_id" in identity_config and identity_config["client_id"]:
            return msal.UserAssignedManagedIdentity(client_id=identity_config["client_id"])
        if "resource_id" in identity_config and identity_config["resource_id"]:
            return msal.UserAssignedManagedIdentity(resource_id=identity_config["resource_id"])
        if "object_id" in identity_config and identity_config["object_id"]:
            return msal.UserAssignedManagedIdentity(object_id=identity_config["object_id"])
        return msal.SystemAssignedManagedIdentity()

    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any
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
        if not scopes:
            raise ValueError('"get_token" requires at least one scope')
        _scopes_to_resource(*scopes)
        token = None
        try:
            token = self._request_token(*scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs)
            if token:
                _LOGGER.log(
                    logging.DEBUG if within_credential_chain.get() else logging.INFO,
                    "%s.get_token succeeded",
                    self.__class__.__name__,
                )
                return token
            _LOGGER.log(
                logging.DEBUG if within_credential_chain.get() else logging.WARNING,
                "%s.get_token failed",
                self.__class__.__name__,
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise CredentialUnavailableError(self.get_unavailable_message())
        except msal.ManagedIdentityError as ex:
            _LOGGER.log(
                logging.DEBUG if within_credential_chain.get() else logging.WARNING,
                "%s.get_token failed: %s",
                self.__class__.__name__,
                ex,
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise ClientAuthenticationError(self.get_unavailable_message(str(ex))) from ex
        except Exception as ex:  # pylint:disable=broad-except
            _LOGGER.log(
                logging.DEBUG if within_credential_chain.get() else logging.WARNING,
                "%s.get_token failed: %s",
                self.__class__.__name__,
                ex,
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise

    def __getstate__(self) -> Dict[str, Any]:  # pylint:disable=client-method-name-no-double-underscore
        state = self.__dict__.copy()
        # Remove the non-picklable entries
        del state["_msal_client"]
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:  # pylint:disable=client-method-name-no-double-underscore
        self.__dict__.update(state)
        # Re-create the unpickable entries
        managed_identity = self.get_managed_identity(**self._settings)
        self._msal_client = msal.ManagedIdentityClient(managed_identity, http_client=self._client)
