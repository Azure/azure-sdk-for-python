# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from datetime import datetime
from typing import Optional, List, Union

from azure.core import MatchConditions

from .._generated.models import SettingFields
from .._models import ConfigurationSetting

class AppConfigurationClient(object):
    """A Client for the AppConfiguration Service.

    :param str account_url: The URL for the service.
    :param AsyncTokenCredential credential: The credentials to authenticate with the service.
    """

    def __init__(self, account_url: str, credential: "AsyncTokenCredential", **kwargs):
        pass

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
        :paramtype select: List[Union[str, ~azure.appconfiguration.SettingFields]]
        :raises ~azure.core.exceptions.ResourceNotFoundError: If no matching configuration setting exists.
        """
        pass