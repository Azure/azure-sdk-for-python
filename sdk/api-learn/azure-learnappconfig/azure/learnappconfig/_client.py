# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from datetime import datetime

from azure.core.pipeline.policies import BearerTokenCredentialPolicy

from ._generated import AzureAppConfiguration
from ._models import ConfigurationSetting
from ._version import VERSION


class AppConfigurationClient(object):
    """A Client for the AppConfiguration Service.
    
    :param str account_url: The URL for the service.
    :param TokenCredential credential: The credentials to authenticate with the service.
    """

    def __init__(self, account_url, credential, **kwargs):
        # type: (str, TokenCredential) -> None
        try:
            if not account_url.lower().startswith('http'):
                full_url = "https://" + account_url
            else:
                full_url = account_url
        except AttributeError:
            raise ValueError("Base URL must be a string.")

        user_agent_moniker = "learnappconfig/{}".format(VERSION)
        self._client = AzureAppConfiguration(
            credential=credential,
            endpoint=account_url,
            credential_scopes=[account_url.strip("/") + "/.default"],
            sdk_moniker=user_agent_moniker,
            **kwargs)

    @classmethod
    def from_connection_string(cls, connection_string, **kwargs):
        # type: (str) -> AppConfigurationClient
        """Build an AppConfigurationClient from a connection string.

        :param str connection_string: A connection string, as retrieved
         from the Azure portal.
        """
        pass

    def get_configuration_setting(self, key, label=None, **kwargs):
        # type: (str, Optional[str]) -> ConfigurationSetting
        """Get the value of a particular configuration settings.

        :param str key: The key name of the setting.
        :param str label: The label of the setting.
        :keyword datetime accept_datetime: The last modified date filter.
        :keyword select: The specific properties of the setting that should be returned.
        :paramtype select: List[Union[str, ~azure.learnappconfig.SettingFields]]
        :raises ~azure.core.exceptions.ResourceNotFoundError: If no matching configuration setting exists.
        """
        pass

    def close(self):
        # type: () -> None
        self._client.close()

    def __enter__(self):
        # type: () -> AppConfigurationClient
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details):
        # type: (Any) -> None
        self._client.__exit__(*exc_details)
