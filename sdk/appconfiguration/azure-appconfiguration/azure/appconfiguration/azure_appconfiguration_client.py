# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from requests.structures import CaseInsensitiveDict
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import UserAgentPolicy
from azure.core.pipeline.policies.distributed_tracing import DistributedTracingPolicy
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline.transport import RequestsTransport
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceModifiedError,
)
from ._generated import ConfigurationClient
from ._generated._configuration import ConfigurationClientConfiguration
from ._generated.models import ConfigurationSetting
from .azure_appconfiguration_requests import AppConfigRequestsCredentialsPolicy
from .azure_appconfiguration_credential import AppConfigConnectionStringCredential
from .utils import (
    get_endpoint_from_connection_string,
    escape_and_tolist,
    prep_update_configuration_setting,
    quote_etag,
)
from ._user_agent import USER_AGENT


class AzureAppConfigurationClient:
    """Represents an client that calls restful API of Azure App Configuration service.

        :param str base_url: base url of the service
        :param credential: An object which can provide secrets for the app configuration service
        :type credential: azure.AppConfigConnectionStringCredential

    """
    def __init__(self, base_url, credential, **kwargs):
        # type: (str, AppConfigConnectionStringCredential, Any) -> None
        self.config = ConfigurationClientConfiguration(credential, **kwargs)
        self.config.user_agent_policy = UserAgentPolicy(
            base_user_agent=USER_AGENT, **kwargs
        )

        pipeline = kwargs.get("pipeline")

        if pipeline is None:
            pipeline = self._create_appconfig_pipeline(**kwargs)

        self._impl = ConfigurationClient(
            credential, base_url, pipeline=pipeline
        )

    @classmethod
    def from_connection_string(
        cls,
        connection_string,  # type: str
        **kwargs
    ):
        # type: (...) -> AzureAppConfigurationClient
        """Create AzureAppConfigurationClient from a Connection String.

                :param connection_string: Connection String
                    (one of the access keys of the Azure App Configuration resource)
                    used to access the Azure App Configuration.
                :type connection_string: str

            Example

            .. code-block:: python

                from azure.appconfiguration import AzureAppConfigurationClient
                connection_str = "<my connection string>"
                client = AzureAppConfigurationClient.from_connection_string(connection_str)
            """
        base_url = "https://" + get_endpoint_from_connection_string(connection_string)
        return cls(
            credential=AppConfigConnectionStringCredential(connection_string),
            base_url=base_url,
            **kwargs
        )

    def _create_appconfig_pipeline(self, **kwargs):
        transport = kwargs.get('transport')
        policies = kwargs.get('policies')

        if policies is None:  # [] is a valid policy list
            policies = [
                self.config.headers_policy,
                self.config.user_agent_policy,
                AppConfigRequestsCredentialsPolicy(self.config.credentials),
                self.config.retry_policy,
                self.config.logging_policy,  # HTTP request/response log
                DistributedTracingPolicy(),
            ]

        if not transport:
            transport = RequestsTransport(**kwargs)

        return Pipeline(transport, policies)

    @distributed_trace
    def list_configuration_settings(
        self, labels=None, keys=None, **kwargs
    ):  # type: (list, list, dict) -> azure.core.paging.ItemPaged[ConfigurationSetting]

        """List the configuration settings stored in the configuration service, optionally filtered by
        label and accept_date_time

        :param labels: filter results based on their label. '*' can be
         used as wildcard in the beginning or end of the filter
        :type labels: list[str]
        :param keys: filter results based on their keys. '*' can be
         used as wildcard in the beginning or end of the filter
        :type keys: list[str]
        :param accept_date_time: filter out ConfigurationSetting created after this datetime
        :type accept_date_time: datetime
        :param fields: specify which fields to include in the results. Leave None to include all fields
        :type fields: list[str]
        :param dict kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :return: An iterator of :class:`ConfigurationSetting`
        :rtype: :class:`azure.core.paging.ItemPaged[ConfigurationSetting]`
        :raises: :class:`HttpRequestError`

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
        labels = escape_and_tolist(labels)
        keys = escape_and_tolist(keys)
        return self._impl.list_configuration_settings(label=labels, key=keys, **kwargs)

    @distributed_trace
    def get_configuration_setting(
        self, key, label=None, **kwargs
    ):  # type: (str, str, dict) -> ConfigurationSetting

        """Get the matched ConfigurationSetting from Azure App Configuration service

        :param key: key of the ConfigurationSetting
        :type key: str
        :param label: label of the ConfigurationSetting
        :type label: str
        :param accept_date_time: The retrieved ConfigurationSetting must be created no later than this datetime
        :type accept_date_time: datetime
        :param dict kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :return: The matched ConfigurationSetting object
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`ResourceNotFoundError`, :class:`HttpRequestError`

        Example

        .. code-block:: python

            fetched_config_setting = client.get_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """
        error_map = {404: ResourceNotFoundError}
        return self._impl.get_configuration_setting(
            key=key,
            label=label,
            accept_date_time=kwargs.get("accept_date_time"),
            headers=kwargs.get("headers"),
            error_map=error_map,
        )

    @distributed_trace
    def add_configuration_setting(self, configuration_setting, **kwargs):
        # type: (ConfigurationSetting, dict) -> ConfigurationSetting

        """Add a ConfigurationSetting into the Azure App Configuration service.

        :param configuration_setting: the ConfigurationSetting object to be added
        :type configuration_setting: :class:`ConfigurationSetting<azure.appconfiguration.ConfigurationSetting>`
        :param dict kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :return: The ConfigurationSetting object returned from the App Configuration service
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`ResourceExistsError`, :class:`HttpRequestError`

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
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
        custom_headers["if-none-match"] = "*"
        return self._impl.create_or_update_configuration_setting(
            configuration_setting=configuration_setting,
            key=configuration_setting.key,
            label=configuration_setting.label,
            headers=custom_headers,
            error_map={412: ResourceExistsError},
        )

    @distributed_trace
    def update_configuration_setting(
        self, key, value=None, label=None, etag=None, **kwargs
    ):  # type: (str, str, str, str, dict) -> ConfigurationSetting
        """Update specified attributes of the ConfigurationSetting

        :param key: key used to identify the ConfigurationSetting
        :param value: the value to be updated to the ConfigurationSetting. None means unchanged.
        :param content_type: the content type to be updated to the ConfigurationSetting. None means unchanged.
        :param tags: tags to be updated to the ConfigurationSetting. None means unchanged.
        :param label: lable used together with key to identify the ConfigurationSetting.
        :param etag: the ETag (http entity tag) of the ConfigurationSetting.
            Used to check if the configuration setting has changed. Leave None to skip the check.
        :param kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`ResourceNotFoundError`, :class:`ResourceModifiedError`, :class:`HttpRequestError`

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
        custom_headers = prep_update_configuration_setting(key, etag, **kwargs)

        current_configuration_setting = self.get_configuration_setting(key, label)
        if value is not None:
            current_configuration_setting.value = value
        content_type = kwargs.get("content_type")
        if content_type is not None:
            current_configuration_setting.content_type = content_type
        tags = kwargs.get("tags")
        if tags is not None:
            current_configuration_setting.tags = tags
        return self._impl.create_or_update_configuration_setting(
            configuration_setting=current_configuration_setting,
            key=key,
            label=label,
            headers=custom_headers,
            error_map={404: ResourceNotFoundError, 412: ResourceModifiedError},
        )

    @distributed_trace
    def set_configuration_setting(
        self, configuration_setting, **kwargs
    ):  # type: (ConfigurationSetting, dict) -> ConfigurationSetting

        """Add or update a ConfigurationSetting.
        If the configuration setting identified by key and label does not exist, this is a create.
        Otherwise this is an update.

        :param configuration_setting: the ConfigurationSetting to be added (if not exists)
        or updated (if exists) to the service
        :type configuration_setting: :class:`ConfigurationSetting`
        :param kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :type kwargs: dict
        :return: The ConfigurationSetting returned from the service
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`ResourceModifiedError`, :class:`HttpRequestError`

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
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
        etag = configuration_setting.etag
        if etag:
            custom_headers["if-match"] = quote_etag(etag)
        return self._impl.create_or_update_configuration_setting(
            configuration_setting=configuration_setting,
            key=configuration_setting.key,
            label=configuration_setting.label,
            headers=custom_headers,
            error_map={412: ResourceModifiedError},
        )

    @distributed_trace
    def delete_configuration_setting(
        self, key, label=None, etag=None, **kwargs
    ):  # type: (str, str, str, dict) -> ConfigurationSetting

        """Delete a ConfigurationSetting if it exists

        :param key: key used to identify the ConfigurationSetting
        :type key: str
        :param label: label used to identify the ConfigurationSetting
        :type label: str
        :param etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :type etag: str
        :param kwargs: if "headers" exists, its value (a dict) will be added to the http request
        :type kwargs: dict
        :return: The deleted ConfigurationSetting returned from the service, or None if it doesn't exist.
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`ResourceModifiedError`, :class:`HttpRequestError`

        Example

        .. code-block:: python

            deleted_config_setting = client.delete_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
        if etag:
            custom_headers["if-match"] = quote_etag(etag)
        return self._impl.delete_configuration_setting(
            key=key,
            label=label,
            headers=custom_headers,
            error_map={
                404: ResourceNotFoundError,  # 404 doesn't happen actually. return None if no match
                412: ResourceModifiedError,
            },
        )

    @distributed_trace
    def list_revisions(
        self, labels=None, keys=None, **kwargs
    ):  # type: (list, list, dict) -> azure.core.paging.ItemPaged[ConfigurationSetting]

        """
        Find the ConfigurationSetting revision history.

        :param labels: filter results based on their label. '*' can be
         used as wildcard in the beginning or end of the filter
        :type labels: list[str]
        :param keys: filter results based on their keys. '*' can be
         used as wildcard in the beginning or end of the filter
        :type keys: list[str]
        :param accept_date_time: filter out ConfigurationSetting created after this datetime
        :type accept_date_time: datetime
        :param fields: specify which fields to include in the results. Leave None to include all fields
        :type fields: list[str]
        :param dict kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :return: An iterator of :class:`ConfigurationSetting`
        :rtype: :class:`azure.core.paging.ItemPaged[ConfigurationSetting]`
        :raises: :class:`HttpRequestError`

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
        labels = escape_and_tolist(labels)
        keys = escape_and_tolist(keys)
        return self._impl.list_revisions(label=labels, key=keys, **kwargs)
