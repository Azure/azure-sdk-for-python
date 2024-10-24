# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
from typing import Any, IO, List, MutableMapping, overload, Union

from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import HttpLoggingPolicy
from azure.core.polling import AsyncLROPoller
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async

from ._client import SecurityDomainClient as _SecurityDomainClient
from .._internal import AsyncChallengeAuthPolicy, AsyncSecurityDomainClientPollingMethod, SecurityDomainClientPolling
from ..models import CertificateInfoObject, SecurityDomainObject
from .._patch import DEFAULT_VERSION, _format_api_version, _SERIALIZER

if sys.version_info < (3, 9):
    from typing import Awaitable
else:
    from collections.abc import Awaitable

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object

__all__: List[str] = []  # Add all objects you want publicly available to users at this package level


class SecurityDomainClient(_SecurityDomainClient):
    """Manages the security domain of a Managed HSM.

    :param str vault_url: URL of the vault on which the client will operate. This is also called the vault's "DNS Name".
        You should validate that this URL references a valid Key Vault or Managed HSM resource.
        See https://aka.ms/azsdk/blog/vault-uri for details.
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential

    :keyword str api_version: The API version to use for this operation. Default value is "7.5". Note that overriding
        this default value may result in unsupported behavior.
    :keyword bool verify_challenge_resource: Whether to verify the authentication challenge resource matches the Key
        Vault or Managed HSM domain. Defaults to True.
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
        Retry-After header is present.
    """

    def __init__(self, vault_url: str, credential: AsyncTokenCredential, **kwargs):
        self.api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        # If API version was provided as an enum value, need to make a plain string for 3.11 compatibility
        if hasattr(self.api_version, "value"):
            self.api_version = self.api_version.value
        self._vault_url = vault_url.strip(" /")

        http_logging_policy = HttpLoggingPolicy(**kwargs)
        http_logging_policy.allowed_header_names.update(
            {"x-ms-keyvault-network-info", "x-ms-keyvault-region", "x-ms-keyvault-service-version"}
        )
        verify_challenge = kwargs.pop("verify_challenge_resource", True)
        super().__init__(
            vault_url,
            credential,
            api_version=self.api_version,
            authentication_policy=AsyncChallengeAuthPolicy(credential, verify_challenge_resource=verify_challenge),
            http_logging_policy=http_logging_policy,
            **kwargs,
        )

    @overload
    async def begin_download(
        self, certificate_info_object: CertificateInfoObject, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[SecurityDomainObject]:
        """Retrieves the Security Domain from the managed HSM. Calling this endpoint can
        be used to activate a provisioned managed HSM resource.

        :param certificate_info_object: The Security Domain download operation requires customer to
         provide N certificates (minimum 3 and maximum 10)
         containing a public key in JWK format. Required.
        :type certificate_info_object: ~azure.keyvault.securitydomain.models.CertificateInfoObject
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns SecurityDomainObject. The
         SecurityDomainObject is compatible with MutableMapping
        :rtype:
         ~azure.core.polling.AsyncLROPoller[~azure.keyvault.securitydomain.models.SecurityDomainObject]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_download(
        self, certificate_info_object: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[SecurityDomainObject]:
        """Retrieves the Security Domain from the managed HSM. Calling this endpoint can
        be used to activate a provisioned managed HSM resource.

        :param certificate_info_object: The Security Domain download operation requires customer to
         provide N certificates (minimum 3 and maximum 10)
         containing a public key in JWK format. Required.
        :type certificate_info_object: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns SecurityDomainObject. The
         SecurityDomainObject is compatible with MutableMapping
        :rtype:
         ~azure.core.polling.AsyncLROPoller[~azure.keyvault.securitydomain.models.SecurityDomainObject]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_download(
        self, certificate_info_object: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AsyncLROPoller[SecurityDomainObject]:
        """Retrieves the Security Domain from the managed HSM. Calling this endpoint can
        be used to activate a provisioned managed HSM resource.

        :param certificate_info_object: The Security Domain download operation requires customer to
         provide N certificates (minimum 3 and maximum 10)
         containing a public key in JWK format. Required.
        :type certificate_info_object: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller that returns SecurityDomainObject. The
         SecurityDomainObject is compatible with MutableMapping
        :rtype:
         ~azure.core.polling.AsyncLROPoller[~azure.keyvault.securitydomain.models.SecurityDomainObject]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_download(
        self, certificate_info_object: Union[CertificateInfoObject, JSON, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[SecurityDomainObject]:
        """Retrieves the Security Domain from the managed HSM. Calling this endpoint can
        be used to activate a provisioned managed HSM resource.

        :param certificate_info_object: The Security Domain download operation requires customer to
         provide N certificates (minimum 3 and maximum 10)
         containing a public key in JWK format. Is one of the following types: CertificateInfoObject,
         JSON, IO[bytes] Required.
        :type certificate_info_object: ~azure.keyvault.securitydomain.models.CertificateInfoObject or
         JSON or IO[bytes]
        :return: An instance of AsyncLROPoller that returns SecurityDomainObject. The
         SecurityDomainObject is compatible with MutableMapping
        :rtype:
         ~azure.core.polling.AsyncLROPoller[~azure.keyvault.securitydomain.models.SecurityDomainObject]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        delay = kwargs.pop("polling_interval", self._config.polling_interval)
        return await super().begin_download(
            certificate_info_object,
            polling=AsyncSecurityDomainClientPollingMethod(
                lro_algorithms=[SecurityDomainClientPolling()], timeout=delay
            ),
            **kwargs,
        )

    @distributed_trace_async
    def send_request(
        self, request: HttpRequest, *, stream: bool = False, **kwargs: Any
    ) -> Awaitable[AsyncHttpResponse]:
        """Runs a network request using the client's existing pipeline.

        The request URL can be relative to the vault URL. The service API version used for the request is the same as
        the client's unless otherwise specified. This method does not raise if the response is an error; to raise an
        exception, call `raise_for_status()` on the returned response object. For more information about how to send
        custom requests with this method, see https://aka.ms/azsdk/dpcodegen/python/send_request.

        :param request: The network request you want to make.
        :type request: ~azure.core.rest.HttpRequest

        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.

        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.AsyncHttpResponse
        """
        request_copy = _format_api_version(request, self.api_version)
        path_format_arguments = {
            "vaultBaseUrl": _SERIALIZER.url("vault_base_url", self._vault_url, "str", skip_quote=True),
        }
        request_copy.url = self._client._client.format_url(request_copy.url, **path_format_arguments)
        return self._client._client.send_request(request_copy, stream=stream, **kwargs)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
