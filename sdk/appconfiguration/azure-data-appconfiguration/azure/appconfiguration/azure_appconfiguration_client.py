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
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport
from azure.core.exceptions import ResourceNotFoundError, ResourceModifiedError
from ._generated import ConfigurationClient
from ._generated._configuration import ConfigurationClientConfiguration
from ._generated.models import ConfigurationSetting
from .azure_appconfiguration_requests import AppConfigRequestsCredentialsPolicy
from .azure_appconfiguration_client_abstract import AzureAppConfigurationClientAbstract
from .utils import get_endpoint_from_connection_string


class AzureAppConfigurationClient(AzureAppConfigurationClientAbstract):
    """
    Example

    .. code-block:: python

        from azure.appconfiguration import AzureAppConfigurationClient
        connection_str = "<my connection string>"
        client = AzureAppConfigurationClient(connection_str)
    """

    def __init__(self, connection_string):
        super(AzureAppConfigurationClient, self).__init__()
        base_url = "https://" + get_endpoint_from_connection_string(connection_string)
        program_name = os.path.basename(sys.argv[0]) or "noprogram"
        self.config = ConfigurationClientConfiguration(
            connection_string, base_user_agent=program_name, logging_enable=True
        )
        self.config.user_agent_policy.add_user_agent(
            "{}{}".format(platform.python_implementation(), platform.python_version())
        )
        self.config.user_agent_policy.add_user_agent(platform.platform())
        self._impl = ConfigurationClient(
            connection_string,
            base_url,
            pipeline=self._create_azconfig_pipeline(),
        )

    def _create_azconfig_pipeline(self):
        policies = [
            self.config.headers_policy,
            self.config.user_agent_policy,
            self.config.logging_policy,  # HTTP request/response log
            AppConfigRequestsCredentialsPolicy(self.config.credentials),
        ]

        return Pipeline(
            RequestsTransport(configuration=self.config), policies  # Send HTTP request using requests
        )

    def list_configuration_settings(
        self, labels=None, keys=None, accept_date_time=None, fields=None, **kwargs
    ):  # type: (list, list, datetime, list, dict) -> Paged
        """
        Example

        .. code-block:: python

            from datetime import datetime, timedelta

            accept_date_time = datetime.today() + timedelta(days=-1)

            all_listed = client.list_configuration_settings()
            for item in all_listed:
                pass  # do something

            filtered_listed = client.list_configuration_settings(
                labels=["*Labe*"], keys=["*Ke*"], accept_date_time=accept_date_time
            )
            for item in filtered_listed:
                pass  # do something
        """
        return super(AzureAppConfigurationClient, self).list_configuration_settings(
            labels, keys, accept_date_time, fields, **kwargs
        )

    def get_configuration_setting(
        self, key, label=None, accept_date_time=None, **kwargs
    ):  # type: (str, str, datetime, dict) -> Paged
        """
        Example

        .. code-block:: python

            fetched_config_setting = client.get_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """
        return super(AzureAppConfigurationClient, self).get_configuration_setting(
            key, label=label, accept_date_time=accept_date_time, **kwargs
        )

    def add_configuration_setting(self, configuration_setting, **kwargs):
        # type: (ConfigurationSetting, dict) -> ConfigurationSetting
        """
        Example

        .. code-block:: python

            config_setting = ConfigurationSetting(
                key="MyKey",
                label="MyLabel",
                value="my value",
                content_type="my content type",
                tags={"my tag": "my tag value"}
            )
            added_config_setting = client.add_configuration_setting(config_setting)
        """
        return super(AzureAppConfigurationClient, self).add_configuration_setting(configuration_setting, **kwargs)

    def update_configuration_setting(
        self,
        key,
        value=None,
        content_type=None,
        tags=None,
        label=None,
        etag=None,
        **kwargs
    ):  # type: (str, str, str, dict, str, str, dict) -> ConfigurationSetting
        """
        Example

        .. code-block:: python

            updated_kv = client.update_configuration_setting(
                key="MyKey",
                label="MyLabel",
                value="my updated value",
                content_type=None,  # None means not to update it
                tags={"my updated tag": "my updated tag value"}
            )
        """
        custom_headers = AzureAppConfigurationClientAbstract.prep_update_configuration_setting(
            key, etag, **kwargs
        )

        current_configuration_setting = self.get_configuration_setting(key, label)
        if value is not None:
            current_configuration_setting.value = value
        if content_type is not None:
            current_configuration_setting.content_type = content_type
        if tags is not None:
            current_configuration_setting.tags = tags
        return self._impl.create_or_update_configuration_setting(
            configuration_setting=current_configuration_setting,
            key=key,
            label=label,
            headers=custom_headers,
            error_map={404: ResourceNotFoundError, 412: ResourceModifiedError},
        )

    def set_configuration_setting(
        self, configuration_setting, **kwargs
    ):  # type: (ConfigurationSetting, dict) -> ConfigurationSetting
        """
        Example

        .. code-block:: python

            config_setting = ConfigurationSetting(
                key="MyKey",
                label="MyLabel",
                value="my set value",
                content_type="my set content type",
                tags={"my set tag": "my set tag value"}
            )
            returned_config_setting = client.set_configuration_setting(config_setting)
        """
        return super(AzureAppConfigurationClient, self).set_configuration_setting(configuration_setting, **kwargs)

    def delete_configuration_setting(
        self, key, label=None, etag=None, **kwargs
    ):  # type: (str, str, str, dict) -> ConfigurationSetting
        """
        Example

        .. code-block:: python

            deleted_config_setting = client.delete_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """
        return super(AzureAppConfigurationClient, self).delete_configuration_setting(key, label, etag, **kwargs)

    def list_revisions(
        self, labels=None, keys=None, accept_date_time=None, fields=None, **kwargs
    ):  # type: (list, list, datetime, list, dict) -> Paged
        """
        Example

        .. code-block:: python

            from datetime import datetime, timedelta

            accept_date_time = datetime.today() + timedelta(days=-1)

            all_revisions = client.list_revisions()
            for item in all_revisions:
                pass  # do something

            filtered_revisions = client.list_revisions(
                labels=["*Labe*"], keys=["*Ke*"], accept_date_time=accept_date_time
            )
            for item in filtered_revisions:
                pass  # do something
        """
        return super(AzureAppConfigurationClient, self).list_revisions(labels, keys, accept_date_time, fields, **kwargs)


if platform.python_version() > "3.0":
    AzureAppConfigurationClient.__doc__ = (
        AzureAppConfigurationClientAbstract.__doc__ + AzureAppConfigurationClient.__doc__
    )
    AzureAppConfigurationClient.get_configuration_setting.__doc__ = (
        AzureAppConfigurationClientAbstract.get_configuration_setting.__doc__
        + AzureAppConfigurationClient.get_configuration_setting.__doc__
    )
    AzureAppConfigurationClient.add_configuration_setting.__doc__ = (
        AzureAppConfigurationClientAbstract.add_configuration_setting.__doc__
        + AzureAppConfigurationClient.add_configuration_setting.__doc__
    )
    AzureAppConfigurationClient.set_configuration_setting.__doc__ = (
        AzureAppConfigurationClientAbstract.set_configuration_setting.__doc__
        + AzureAppConfigurationClient.set_configuration_setting.__doc__
    )
    AzureAppConfigurationClient.update_configuration_setting.__doc__ = (
        AzureAppConfigurationClientAbstract.update_configuration_setting.__doc__
        + AzureAppConfigurationClient.update_configuration_setting.__doc__
    )
    AzureAppConfigurationClient.delete_configuration_setting.__doc__ = (
        AzureAppConfigurationClientAbstract.delete_configuration_setting.__doc__
        + AzureAppConfigurationClient.delete_configuration_setting.__doc__
    )
    AzureAppConfigurationClient.list_configuration_settings.__doc__ = (
        AzureAppConfigurationClientAbstract.list_configuration_settings.__doc__
        + AzureAppConfigurationClient.list_configuration_settings.__doc__
    )
    AzureAppConfigurationClient.list_revisions.__doc__ = (
        AzureAppConfigurationClientAbstract.list_revisions.__doc__
        + AzureAppConfigurationClient.list_revisions.__doc__
    )
