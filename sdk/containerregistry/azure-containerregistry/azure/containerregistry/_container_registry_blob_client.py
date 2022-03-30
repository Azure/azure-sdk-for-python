# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING, Any, Optional

from azure.core.tracing.decorator import distributed_trace

from ._authentication_policy import ContainerRegistryChallengePolicy
from ._generated import ContainerRegistry
from ._helpers import SUPPORTED_API_VERSIONS
from ._user_agent import USER_AGENT

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class ContainerRegistryBlobClient(object):
    def __init__(self, endpoint, credential=None, **kwargs):
        # type: (str, Optional[TokenCredential], **Any) -> None
        """Create a ContainerRegistryClient from an ACR endpoint and a credential.

        :param str endpoint: An ACR endpoint.
        :param credential: The credential with which to authenticate.
        :type credential: ~azure.core.credentials.TokenCredential
        :keyword api_version: API Version. The default value is "2021-07-01". Note that overriding this default value
         may result in unsupported behavior.
        :paramtype api_version: str
        :keyword audience: URL to use for credential authentication with AAD. Its value could be
         "https://management.azure.com", "https://management.chinacloudapi.cn", "https://management.microsoftazure.de"
         or "https://management.usgovcloudapi.net".
        :paramtype audience: str
        :returns: None
        :rtype: None
        :raises ValueError: If the provided api_version keyword-only argument isn't supported or
         audience keyword-only argument isn't provided.

        .. admonition:: Example:

        """
        api_version = kwargs.get("api_version", None)
        if api_version and api_version not in SUPPORTED_API_VERSIONS:
            supported_versions = "\n".join(SUPPORTED_API_VERSIONS)
            raise ValueError(
                "Unsupported API version '{}'. Please select from:\n{}".format(
                    api_version, supported_versions
                )
            )
        audience = kwargs.pop("audience", None)
        if not audience:
            raise ValueError("The argument audience must be set to initialize ContainerRegistryClient.")
        defaultScope = [audience + "/.default"]
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._credential = credential
        self._auth_policy = ContainerRegistryChallengePolicy(credential, endpoint, **kwargs)
        self._client = ContainerRegistry(
            credential=credential,
            url=endpoint,
            sdk_moniker=USER_AGENT,
            authentication_policy=self._auth_policy,
            **kwargs
        )
        
    @distributed_trace
    def delete_repository(self, repository, **kwargs):
        
