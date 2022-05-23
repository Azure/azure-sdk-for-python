# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List

__all__: List[str] = []  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


# class ConfidentialLedgerClientConfiguration(Configuration):  # pylint: disable=too-many-instance-attributes
#     """Configuration for ConfidentialLedgerClient.

#     Note that all parameters used to create this instance are saved as instance
#     attributes.

#     :param ledger_uri: The Confidential Ledger URL, for example
#      https://contoso.confidentialledger.azure.com.
#     :type ledger_uri: str
#     :param credential: Credential needed for the client to connect to Azure.
#     :type credential: ~azure.core.credentials.TokenCredential
#     :keyword api_version: Api Version. Default value is "2022-05-13". Note that overriding this
#      default value may result in unsupported behavior.
#     :paramtype api_version: str
#     """

#     def __init__(
#         self,
#         ledger_uri: str,
#         credential: "TokenCredential",
#         **kwargs: Any
#     ) -> None:
#         super(ConfidentialLedgerClientConfiguration, self).__init__(**kwargs)
#         api_version = kwargs.pop('api_version', "2022-05-13")  # type: str

#         if ledger_uri is None:
#             raise ValueError("Parameter 'ledger_uri' must not be None.")
#         if credential is None:
#             raise ValueError("Parameter 'credential' must not be None.")

#         self.ledger_uri = ledger_uri
#         self.credential = credential
#         self.api_version = api_version
#         self.credential_scopes = kwargs.pop('credential_scopes', ['https://confidential-ledger.azure.com/.default'])
#         kwargs.setdefault('sdk_moniker', 'confidentialledger/{}'.format(VERSION))
#         self._configure(**kwargs)

#     def _configure(
#         self,
#         **kwargs  # type: Any
#     ):
#         # type: (...) -> None
#         self.user_agent_policy = kwargs.get('user_agent_policy') or policies.UserAgentPolicy(**kwargs)
#         self.headers_policy = kwargs.get('headers_policy') or policies.HeadersPolicy(**kwargs)
#         self.proxy_policy = kwargs.get('proxy_policy') or policies.ProxyPolicy(**kwargs)
#         self.logging_policy = kwargs.get('logging_policy') or policies.NetworkTraceLoggingPolicy(**kwargs)
#         self.http_logging_policy = kwargs.get('http_logging_policy') or policies.HttpLoggingPolicy(**kwargs)
#         self.retry_policy = kwargs.get('retry_policy') or policies.RetryPolicy(**kwargs)
#         self.custom_hook_policy = kwargs.get('custom_hook_policy') or policies.CustomHookPolicy(**kwargs)
#         self.redirect_policy = kwargs.get('redirect_policy') or policies.RedirectPolicy(**kwargs)
#         self.authentication_policy = kwargs.get('authentication_policy')
#         if self.credential and not self.authentication_policy:
#             self.authentication_policy = policies.BearerTokenCredentialPolicy(self.credential, *self.credential_scopes, **kwargs)
