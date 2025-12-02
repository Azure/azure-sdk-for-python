# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Union

from azure.core.credentials_async import AsyncTokenCredential
from azure.core.credentials import AzureKeyCredential

from .._shared.auth_policy_utils import get_authentication_policy
from .._shared.utils import parse_connection_str
from ._client import EmailClient as EmailClientGenerated
from .._version import VERSION
from .._api_versions import DEFAULT_VERSION


class EmailClient(EmailClientGenerated):
    """A client to interact with the AzureCommunicationService Email gateway.

    This client provides operations to send an email and monitor its status.

    :param str endpoint: The endpoint url for Azure Communication Service resource.
    :param credential: The credential we use to authenticate against the service.
    :paramtype credential: ~azure.core.credentials_async.AsyncTokenCredential or
        ~azure.core.credentials.AzureKeyCredential
    :keyword api_version: Azure Communication Email API version.
        Default value is "2025-09-01".
        Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: Union[AsyncTokenCredential, AzureKeyCredential], **kwargs) -> None:
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.") from None
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        authentication_policy = get_authentication_policy(endpoint, credential, decode_url=True, is_async=True)

        super().__init__(
            endpoint=endpoint,
            authentication_policy=authentication_policy,
            sdk_moniker=f"communication-email/{VERSION}",
            api_version=self._api_version,
            **kwargs,
        )

    @classmethod
    def from_connection_string(cls, conn_str: str, **kwargs) -> "EmailClient":
        """Create EmailClient from a Connection String.

        :param str conn_str: A connection string to an Azure Communication Service resource.
        :returns: Instance of EmailClient.
        :rtype: ~azure.communication.email.EmailClient
        """
        endpoint, access_key = parse_connection_str(conn_str)
        return cls(endpoint, AzureKeyCredential(access_key), **kwargs)


__all__: List[str] = ["EmailClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
