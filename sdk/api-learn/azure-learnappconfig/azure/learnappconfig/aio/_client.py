# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from datetime import datetime
from typing import Optional, List, Union

from msrest import Serializer
from azure.core import MatchConditions
from azure.core.tracing.decorator_async import distributed_trace_async

from .._generated.aio import AzureAppConfiguration
from .._models import ConfigurationSetting, SettingFields
from .._utils import get_match_headers
from .._version import VERSION


class AppConfigurationClient(object):
    """A Client for the AppConfiguration Service.

    :param str account_url: The URL for the service.
    :param AsyncTokenCredential credential: The credentials to authenticate with the service.
    """

    def __init__(self, account_url: str, credential: "AsyncTokenCredential", **kwargs):
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
            endpoint=full_url,
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

    async def __aenter__(self):
        # type: () -> AppConfigurationClient
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details):
        # type: (Any) -> None
        await self._client.__aexit__(*exc_details)

    @distributed_trace_async
    async def get_configuration_setting(
        self,
        key: str,
        *,
        label: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        etag: Optional[str] = None,
        accept_datetime: Optional[datetime] = None,
        select: Optional[List[Union[str, SettingFields]]] = None,
        **kwargs
    ) -> ConfigurationSetting:
        """Get the value of a particular configuration settings.

        :param str key: The key name of the setting.
        :keyword str label: The label of the setting.
        :keyword ~azure.core.MatchConditions match_condition: A condition under which the operation should be completed.
        :keyword str etag: The etag by which the match condition should be assessed.
        :keyword datetime accept_datetime: The last modified date filter.
        :keyword select: The specific properties of the setting that should be returned.
        :paramtype select: List[Union[str, ~azure.learnappconfig.SettingFields]]
        :raises ~azure.core.exceptions.ResourceNotFoundError: If no matching configuration setting exists.
        """
        if_match, if_none_match, errors = get_match_headers(etag, match_condition)
        accept_datetime = kwargs.pop('accept_datetime', None)
        if isinstance(accept_datetime, datetime):
            accept_datetime = Serializer.serialize_rfc(accept_datetime)
        result = await self._client.get_key_value(
            key=key,
            label=label,
            if_match=if_match,
            if_none_match=if_none_match,
            accept_datetime=accept_datetime,
            select=select,
            error_map=errors,
            **kwargs)
        return ConfigurationSetting(
            key=result.key,
            label=result.label,
            value=result.value,
            etag=result.etag,
            last_modified=result.last_modified,
            read_only=result.locked,
            content_type=result.content_type,
            tags=result.tags
        )

    async def close(self):
        # type: () -> None
        await self._client.close()
