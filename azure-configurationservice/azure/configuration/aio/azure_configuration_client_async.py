# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
import sys
import platform
from datetime import datetime
from msrest.paging import Paged
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import AsyncioRequestsTransport
from azure.core.exceptions import ResourceModifiedError, ResourceNotFoundError
from ..utils import get_endpoint_from_connection_string
from .._generated.aio import AzureConfigurationClientImp
from .._generated.aio import AzureConfigurationClientImpConfiguration
from ..azure_configuration_requests import AzConfigRequestsCredentialsPolicy
from ..azure_configuration_client_abstract import AzureConfigurationClientAbstract
from .._generated.models import ConfigurationSetting


class AzureConfigurationClient(AzureConfigurationClientAbstract):
    """
    This is the async version of :class:`azure.configuration.ConfigurationClient`

    Example

    .. code-block:: python

        from azure.configuration.aio import AzureConfigurationClient
        connection_str = "<my connection string>"
        async_client = AzureConfigurationClient(connection_str)
    """

    def __init__(self, connection_string, config=None):
        super().__init__()
        base_url = "https://" + get_endpoint_from_connection_string(connection_string)
        program_name = os.path.basename(sys.argv[0]) or "noprogram"
        self._config = config or AzureConfigurationClientImpConfiguration(
            connection_string, base_user_agent=program_name, logging_enable=True
        )
        self._config.user_agent_policy.add_user_agent(
            "{}{}".format(platform.python_implementation(), platform.python_version())
        )
        self._config.user_agent_policy.add_user_agent(platform.platform())
        self._impl = AzureConfigurationClientImp(
            connection_string,
            base_url,
            config=self._config,
            pipeline=self._create_azconfig_pipeline(),
        )

    def _create_azconfig_pipeline(self):
        policies = [
            self._config.headers_policy,
            self._config.user_agent_policy,
            self._config.logging_policy,  # HTTP request/response log
            AzConfigRequestsCredentialsPolicy(self._config.credentials),
        ]

        return AsyncPipeline(
            AsyncioRequestsTransport(self._config),  # Send HTTP request using requests
            policies,
        )

    def list_configuration_settings(
        self, labels=None, keys=None, accept_date_time=None, fields=None, **kwargs
    ):  # type: (list, list, datetime, list, dict) -> Paged
        """
        Example

        .. code-block:: python

            from datetime import datetime, timedelta

            accept_date_time = datetime.today() + timedelta(days=-1)

            all_listed = async_client.list_configuration_settings()
            async for item in all_listed:
                pass  # do something

            filtered_listed = async_client.list_configuration_settings(
                labels=["*Labe*"], keys=["*Ke*"], accept_date_time=accept_date_time
            )
            async for item in filtered_listed:
                pass  # do something
        """
        return super().list_configuration_settings(
            labels, keys, accept_date_time, fields, **kwargs
        )

    async def get_configuration_setting(
        self, key, label=None, accept_date_time=None, **kwargs
    ):
        """
        Example

        .. code-block:: python

            # in async function
            fetched_config_setting = await async_client.get_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """
        return await super().get_configuration_setting(
            key, label=label, accept_date_time=accept_date_time, **kwargs
        )

    async def add_configuration_setting(self, configuration_setting, **kwargs):
        # type: (ConfigurationSetting, dict) -> ConfigurationSetting
        """
        Example

        .. code-block:: python

            # in async fuction
            config_setting = ConfigurationSetting(
                key="MyKey",
                label="MyLabel",
                value="my value",
                content_type="my content type",
                tags={"my tag": "my tag value"}
            )
            added_config_setting = await async_client.add_configuration_setting(config_setting)
        """
        return await super().add_configuration_setting(configuration_setting, **kwargs)

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
        # type: (str, str, str, dict, str, str, dict) -> ConfigurationSetting
        """
        Example

        .. code-block:: python

            # in async function
            updated_kv = await async_client.update_configuration_setting(
                key="MyKey",
                label="MyLabel",
                value="my updated value",
                content_type=None,  # None means not to update it
                tags={"my updated tag": "my updated tag value"}
            )
        """
        custom_headers = AzureConfigurationClientAbstract.prep_update_configuration_setting(
            key, etag, **kwargs
        )
        current_configuration_setting = await self.get_configuration_setting(key, label)
        if value is not None:
            current_configuration_setting.value = value
        if content_type is not None:
            current_configuration_setting.content_type = content_type
        if tags is not None:
            current_configuration_setting.tags = tags
        return await self._impl.create_or_update_configuration_setting(
            configuration_setting=current_configuration_setting,
            key=key,
            label=label,
            headers=custom_headers,
            error_map={404: ResourceNotFoundError, 412: ResourceModifiedError},
        )

    async def set_configuration_setting(
        self, configuration_setting, **kwargs
    ):  # type: (ConfigurationSetting, dict) -> ConfigurationSetting
        """
        Example

        .. code-block:: python

            # in async function
            config_setting = ConfigurationSetting(
                key="MyKey",
                label="MyLabel",
                value="my set value",
                content_type="my set content type",
                tags={"my set tag": "my set tag value"}
            )
            returned_config_setting = await async_client.set_configuration_setting(config_setting)
        """
        return await super().set_configuration_setting(configuration_setting, **kwargs)

    async def delete_configuration_setting(
        self, key, label=None, etag=None, **kwargs
    ):  # type: (str, str, str, dict) -> ConfigurationSetting
        """
        Example

        .. code-block:: python

            # in async function
            deleted_config_setting = await async_client.delete_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """
        return await super().delete_configuration_setting(key, label, etag, **kwargs)

    def list_revisions(
        self, labels=None, keys=None, accept_date_time=None, fields=None, **kwargs
    ):  # type: (list, list, datetime, list, dict) -> Paged
        """
        Example

        .. code-block:: python

            # in async function
            from datetime import datetime, timedelta

            accept_date_time = datetime.today() + timedelta(days=-1)

            all_revisions = async_client.list_revisions()
            async for item in all_revisions:
                pass  # do something

            filtered_revisions = async_client.list_revisions(
                labels=["*Labe*"], keys=["*Ke*"], accept_date_time=accept_date_time
            )
            async for item in filtered_revisions:
                pass  # do something
        """
        return super().list_revisions(labels, keys, accept_date_time, fields, **kwargs)


AzureConfigurationClient.__doc__ = (
    AzureConfigurationClientAbstract.__doc__ + AzureConfigurationClient.__doc__
)
AzureConfigurationClient.get_configuration_setting.__doc__ = (
    AzureConfigurationClientAbstract.get_configuration_setting.__doc__
    + AzureConfigurationClient.get_configuration_setting.__doc__
)
AzureConfigurationClient.add_configuration_setting.__doc__ = (
    AzureConfigurationClientAbstract.add_configuration_setting.__doc__
    + AzureConfigurationClient.add_configuration_setting.__doc__
)
AzureConfigurationClient.set_configuration_setting.__doc__ = (
    AzureConfigurationClientAbstract.set_configuration_setting.__doc__
    + AzureConfigurationClient.set_configuration_setting.__doc__
)
AzureConfigurationClient.update_configuration_setting.__doc__ = (
    AzureConfigurationClientAbstract.update_configuration_setting.__doc__
    + AzureConfigurationClient.update_configuration_setting.__doc__
)
AzureConfigurationClient.delete_configuration_setting.__doc__ = (
    AzureConfigurationClientAbstract.delete_configuration_setting.__doc__
    + AzureConfigurationClient.delete_configuration_setting.__doc__
)
AzureConfigurationClient.list_configuration_settings.__doc__ = (
    AzureConfigurationClientAbstract.list_configuration_settings.__doc__
    + AzureConfigurationClient.list_configuration_settings.__doc__
)
AzureConfigurationClient.list_revisions.__doc__ = (
    AzureConfigurationClientAbstract.list_revisions.__doc__
    + AzureConfigurationClient.list_revisions.__doc__
)