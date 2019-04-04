# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from msrest.pipeline.requests import RequestsPatchSession
from msrest.pipeline import Request, Pipeline
from msrest.universal_http.async_requests import AsyncRequestsHTTPSender
from msrest.pipeline.async_requests import AsyncPipelineRequestsHTTPSender

from ..utils import get_endpoint_from_connection_string
from .._generated.aio import AzureConfigurationClientImp
from ..azure_configuration_requests import AzConfigRequestsCredentialsPolicy
from ..azure_configuration_client_prep import *


class AzureConfigurationClientAsync(object):
    """
    Represents an client that calls restful API of Azure App Configuration service asynchronously
    This is the async version of :class:`azure.configuration.AzureConfigurationService`

    """

    def __init__(self, connection_string):

        base_url = "https://" + get_endpoint_from_connection_string(connection_string)
        self._client = AzureConfigurationClientImp(connection_string, base_url)
        self._client._client.config.pipeline = self._create_azconfig_pipeline()

    def _create_azconfig_pipeline(self):
        policies = [
            self._client.config.user_agent_policy,  # UserAgent policy
            RequestsPatchSession(),  # Support deprecated operation config at the session level
            self._client.config.http_logger_policy,  # HTTP request/response log
            AzConfigRequestsCredentialsPolicy(self._client.config),
        ]

        return Pipeline(
            policies,
            AsyncPipelineRequestsHTTPSender(
                AsyncRequestsHTTPSender(
                    self._client.config
                )  # Send HTTP request using requests
            ),
        )

    def list_configuration_settings(
        self, labels=None, keys=None, accept_date_time=None, fields=None, **kwargs
    ):
        """List configuration settings.

        The async version of :meth:`azure.configuration.AzureConfigurationClient.list_configuration_settings`
        This method is sync. But the returned result is an async iterator.

        """
        return self._client.list_configuration_settings(
            label=labels,
            key=keys,
            accept_date_time=accept_date_time,
            fields=fields,
            custom_headers=kwargs.get("headers"),
        )

    async def get_configuration_setting(
        self, key, label=None, accept_date_time=None, **kwargs
    ):
        """Get a ConfigurationSetting asynchronously.

        The async version of :meth:`azure.configuration.AzureConfigurationClient.get_configuration_setting`

        """
        custom_headers = prep_get_configuration_setting(key)
        return await self._client.get_configuration_setting(
            key=key,
            label=label,
            accept_date_time=accept_date_time,
            custom_headers=custom_headers,
        )

    async def add_configuration_setting(self, configuration_setting, **kwargs):
        """Create a ConfigurationSetting asynchronously.

        The async version of :meth:`azure.configuration.AzureConfigurationClient.add_configuration_setting`
        """
        custom_headers = prep_add_configuration_setting(configuration_setting, **kwargs)
        key = configuration_setting.key
        return await self._client.create_or_update_configuration_setting(
            configuration_setting=configuration_setting,
            key=key,
            label=configuration_setting.label,
            custom_headers=custom_headers,
        )

    async def update_configuration_setting(
        self,
        key,
        value=None,
        content_type=None,
        tags=None,
        label=None,
        etag=None,
        **kwargs
    ):
        """Update a ConfigurationSetting asynchronously.

        The async version of :meth:`azure.configuration.AzureConfigurationClient.update_configuration_setting`

        """
        custom_headers = prep_update_configuration_setting(key, etag, **kwargs)
        current_configuration_setting = await self._client.get_configuration_setting(
            key, label
        )
        if value is not None:
            current_configuration_setting.value = value
        if content_type is not None:
            current_configuration_setting.content_type = content_type
        if tags is not None:
            current_configuration_setting.tags = tags
        return await self._client.create_or_update_configuration_setting(
            configuration_setting=current_configuration_setting,
            key=key,
            label=label,
            custom_headers=custom_headers,
        )

    async def set_configuration_setting(self, configuration_setting, **kwargs):
        """Set a ConfigurationSetting asynchronously.

        The async version of :meth:`azure.configuration.AzureConfigurationClient.set_configuration_setting`

        """
        custom_headers = prep_set_configuration_setting(configuration_setting, **kwargs)
        key = configuration_setting.key
        return await self._client.create_or_update_configuration_setting(
            configuration_setting=configuration_setting,
            key=key,
            label=configuration_setting.label,
            custom_headers=custom_headers,
        )

    async def delete_configuration_setting(self, key, label=None, etag=None, **kwargs):
        """Delete a ConfigurationSetting asynchronously.

        The async version of :meth:`azure.configuration.AzureConfigurationClient.delete_configuration_setting`
        """
        custom_headers = prep_delete_configuration_setting(key, etag, **kwargs)
        return await self._client.delete_configuration_setting(
            key=key, label=label, custom_headers=custom_headers
        )

    async def lock_configuration_setting(self, key, label=None, **kwargs):
        """Lock a ConfigurationSetting asynchronously.

        The async version of :meth:`azure.configuration.AzureConfigurationClient.lock_configuration_setting`
        """
        custom_headers = prep_lock_configuration_setting(key)
        return await self._client.lock_configuration_setting(
            key=key, label=label, custom_headers=custom_headers
        )

    async def unlock_configuration_setting(self, key, label=None, **kwargs):
        """Unlock a ConfigurationSetting asynchronously.

        The async version of :meth:`azure.configuration.AzureConfigurationClient.unlock_configuration_setting`
        """
        custom_headers = prep_unlock_configuration_setting(key)
        return await self._client.unlock_configuration_setting(
            key=key, label=label, custom_headers=custom_headers
        )

    def list_revisions(
        self, labels=None, keys=None, accept_date_time=None, fields=None, **kwargs
    ):
        """List revisions of configuration settings.

        The async version of :meth:`azure.configuration.AzureConfigurationClient.list_revisions`
        This method is sync. But the returned result is an async iterator.
        """
        return self._client.list_revisions(
            label=labels,
            key=keys,
            accept_date_time=accept_date_time,
            fields=fields,
            custom_headers=kwargs.get("headers"),
        )
