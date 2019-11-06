# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from requests.structures import CaseInsensitiveDict
from azure.core import MatchConditions
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy
)
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.pipeline.transport import AsyncioRequestsTransport
from azure.core.exceptions import (
    HttpResponseError,
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
)
from .._azure_appconfiguration_error import ResourceReadOnlyError
from .._utils import (
    get_endpoint_from_connection_string,
    escape_and_tostr,
    prep_if_match,
    prep_if_none_match,
)
from .._generated.aio import AzureAppConfiguration
from .._generated.models import ErrorException
from .._generated.aio._configuration_async import AzureAppConfigurationConfiguration
from .._azure_appconfiguration_requests import AppConfigRequestsCredentialsPolicy
from .._azure_appconfiguration_credential import AppConfigConnectionStringCredential
from .._generated.models import KeyValue
from .._models import ConfigurationSetting
from .._user_agent import USER_AGENT


class AzureAppConfigurationClient:
    """Represents an client that calls restful API of Azure App Configuration service.

        :param str base_url: base url of the service
        :param credential: An object which can provide secrets for the app configuration service
        :type credential: azure.AppConfigConnectionStringCredential
        :keyword Pipeline pipeline: If omitted, the standard pipeline is used.
        :keyword HttpTransport transport: If omitted, the standard pipeline is used.
        :keyword list[HTTPPolicy] policies: If omitted, the standard pipeline is used.

    This is the async version of :class:`azure.appconfiguration.AzureAppConfigurationClient`

    """

    # pylint:disable=protected-access

    def __init__(self, base_url, credential, **kwargs):
        # type: (str, AppConfigConnectionStringCredential, dict) -> None
        self._config = AzureAppConfigurationConfiguration(credential, **kwargs)
        self._config.user_agent_policy = UserAgentPolicy(
            base_user_agent=USER_AGENT, **kwargs
        )

        pipeline = kwargs.get("pipeline")

        if pipeline is None:
            pipeline = self._create_appconfig_pipeline(**kwargs)

        self._impl = AzureAppConfiguration(
            credentials=credential, base_url=base_url, pipeline=pipeline
        )


    @classmethod
    def from_connection_string(
        cls,
        connection_string,
        **kwargs
    ):
        # type: (string, dict) -> AzureAppConfigurationClient
        """Create AzureAppConfigurationClient from a Connection String.

                :param connection_string: Connection String
                    (one of the access keys of the Azure App Configuration resource)
                    used to access the Azure App Configuration.
                :type connection_string: str

            This is the async version of :class:`azure.appconfiguration.AzureAppConfigurationClient`

            Example

            .. code-block:: python

                from azure.appconfiguration.aio import AzureAppConfigurationClient
                connection_str = "<my connection string>"
                async_client = AzureAppConfigurationClient.from_connection_string(connection_str)
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
                self._config.headers_policy,
                self._config.user_agent_policy,
                AppConfigRequestsCredentialsPolicy(self._config.credentials),
                self._config.retry_policy,
                self._config.logging_policy,  # HTTP request/response log
                DistributedTracingPolicy(**kwargs),
                HttpLoggingPolicy(**kwargs),
            ]

        if not transport:
            transport = AsyncioRequestsTransport(**kwargs)

        return AsyncPipeline(
            transport,
            policies,
        )

    @distributed_trace
    def list_configuration_settings(
        self, keys=None, labels=None, **kwargs
    ):  # type: (list, list, dict) -> azure.core.paging.ItemPaged[ConfigurationSetting]

        """List the configuration settings stored in the configuration service, optionally filtered by
        label and accept_datetime

        :param keys: filter results based on their keys. '*' can be
         used as wildcard in the beginning or end of the filter
        :type keys: list[str]
        :param labels: filter results based on their label. '*' can be
         used as wildcard in the beginning or end of the filter
        :type labels: list[str]
        :keyword datetime accept_datetime: filter out ConfigurationSetting created after this datetime
        :keyword list[str] fields: specify which fields to include in the results. Leave None to include all fields
        :keyword dict headers: if "headers" exists, its value (a dict) will be added to the http request header
        :return: An iterator of :class:`ConfigurationSetting`
        :rtype: :class:`azure.core.paging.ItemPaged[ConfigurationSetting]`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`

        Example

        .. code-block:: python

            from datetime import datetime, timedelta

            accept_datetime = datetime.today() + timedelta(days=-1)

            all_listed = async_client.list_configuration_settings()
            async for item in all_listed:
                pass  # do something

            filtered_listed = async_client.list_configuration_settings(
                labels=["*Labe*"], keys=["*Ke*"], accept_datetime=accept_datetime
            )
            async for item in filtered_listed:
                pass  # do something
        """
        select = kwargs.pop("fields", None)
        if select:
            select = ['locked' if x == 'read_only' else x for x in select]
        encoded_labels = escape_and_tostr(labels)
        encoded_keys = escape_and_tostr(keys)
        error_map = {
            401: ClientAuthenticationError
        }

        try:
            return self._impl.get_key_values(
                label=encoded_labels,
                key=encoded_keys,
                select=select,
                cls=lambda objs: [ConfigurationSetting._from_key_value(x) for x in objs],
                error_map=error_map,
                **kwargs
            )
        except ErrorException as error:
            raise HttpResponseError(message=error.message, response=error.response)

    @distributed_trace_async
    async def get_configuration_setting(
            self, key, label=None, etag='*', match_condition=MatchConditions.Unconditionally, **kwargs):
        # type: (str, Optional[str], Optional[str], Optional[MatchConditions], dict) -> ConfigurationSetting

        """Get the matched ConfigurationSetting from Azure App Configuration service

        :param key: key of the ConfigurationSetting
        :type key: str
        :param label: label of the ConfigurationSetting
        :type label: str
        :param etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :type etag: str or None
        :param ~azure.core.MatchConditions match_condition: the match condition to use upon the etag
        :keyword datetime accept_datetime: the retrieved ConfigurationSetting that created no later than this datetime
        :keyword dict headers: if "headers" exists, its value (a dict) will be added to the http request header
        :return: The matched ConfigurationSetting object
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`, \
        :class:`ResourceNotFoundError`, :class:`ResourceModifiedError`, :class:`ResourceExistsError`

        Example

        .. code-block:: python

            # in async function
            fetched_config_setting = await async_client.get_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError
        }
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[304] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError

        try:
            key_value = await self._impl.get_key_value(
                key=key,
                label=label,
                if_match=prep_if_match(etag, match_condition),
                if_none_match=prep_if_none_match(etag, match_condition),
                error_map=error_map,
                **kwargs
            )
            return ConfigurationSetting._from_key_value(key_value)
        except ResourceNotModifiedError:
            return None
        except ErrorException as error:
            raise HttpResponseError(message=error.message, response=error.response)

    @distributed_trace_async
    async def add_configuration_setting(self, configuration_setting, **kwargs):
        # type: (ConfigurationSetting, dict) -> ConfigurationSetting

        """Add a ConfigurationSetting into the Azure App Configuration service.

        :param configuration_setting: the ConfigurationSetting object to be added
        :type configuration_setting: :class:`ConfigurationSetting<azure.appconfiguration.ConfigurationSetting>`
        :keyword dict headers: if "headers" exists, its value (a dict) will be added to the http request header
        :return: The ConfigurationSetting object returned from the App Configuration service
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`, :class:`ResourceExistsError`

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
        key_value = KeyValue(
            key=configuration_setting.key,
            label=configuration_setting.label,
            content_type=configuration_setting.content_type,
            value=configuration_setting.value,
            tags=configuration_setting.tags
        )
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
        error_map = {
            401: ClientAuthenticationError,
            412: ResourceExistsError
        }

        try:
            key_value_added = await self._impl.put_key_value(
                entity=key_value,
                key=key_value.key,
                label=key_value.label,
                if_none_match="*",
                headers=custom_headers,
                error_map=error_map,
            )
            return ConfigurationSetting._from_key_value(key_value_added)
        except ErrorException as error:
            raise HttpResponseError(message=error.message, response=error.response)

    @distributed_trace_async
    async def set_configuration_setting(
        self, configuration_setting, match_condition=MatchConditions.Unconditionally, **kwargs
    ):  # type: (ConfigurationSetting, Optional[MatchConditions], dict) -> ConfigurationSetting

        """Add or update a ConfigurationSetting.
        If the configuration setting identified by key and label does not exist, this is a create.
        Otherwise this is an update.

        :param configuration_setting: the ConfigurationSetting to be added (if not exists) \
        or updated (if exists) to the service
        :type configuration_setting: :class:`ConfigurationSetting`
        :param ~azure.core.MatchConditions match_condition: the match condition to use upon the etag
        :keyword dict headers: if "headers" exists, its value (a dict) will be added to the http request header
        :return: The ConfigurationSetting returned from the service
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`, \
        :class:`ResourceReadOnlyError`, :class:`ResourceModifiedError`, :class:`ResourceNotModifiedError`, \
        :class:`ResourceNotFoundError`, :class:`ResourceExistsError`

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
        key_value = KeyValue(
            key=configuration_setting.key,
            label=configuration_setting.label,
            content_type=configuration_setting.content_type,
            value=configuration_setting.value,
            tags=configuration_setting.tags
        )
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
        error_map = {
            401: ClientAuthenticationError,
            409: ResourceReadOnlyError
        }
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[412] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError

        try:
            key_value_set = await self._impl.put_key_value(
                entity=key_value,
                key=key_value.key,
                label=key_value.label,
                if_match=prep_if_match(configuration_setting.etag, match_condition),
                if_none_match=prep_if_none_match(configuration_setting.etag, match_condition),
                headers=custom_headers,
                error_map=error_map,
            )
            return ConfigurationSetting._from_key_value(key_value_set)
        except ErrorException as error:
            raise HttpResponseError(message=error.message, response=error.response)

    @distributed_trace_async
    async def delete_configuration_setting(
        self, key, label=None, **kwargs
    ):  # type: (str, Optional[str], dict) -> ConfigurationSetting

        """Delete a ConfigurationSetting if it exists

        :param key: key used to identify the ConfigurationSetting
        :type key: str
        :param label: label used to identify the ConfigurationSetting
        :type label: str
        :keyword str etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :keyword ~azure.core.MatchConditions match_condition: the match condition to use upon the etag
        :keyword dict headers: if "headers" exists, its value (a dict) will be added to the http request
        :return: The deleted ConfigurationSetting returned from the service, or None if it doesn't exist.
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`, \
        :class:`ResourceReadOnlyError`, :class:`ResourceModifiedError`, :class:`ResourceNotModifiedError`, \
        :class:`ResourceNotFoundError`, :class:`ResourceExistsError`

        Example

        .. code-block:: python

            # in async function
            deleted_config_setting = await async_client.delete_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """

        etag = kwargs.pop("etag", None)
        match_condition = kwargs.pop("match_condition", MatchConditions.Unconditionally)
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
        error_map = {
            401: ClientAuthenticationError,
            409: ResourceReadOnlyError
        }
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[412] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError

        try:
            key_value_deleted = await self._impl.delete_key_value(
                key=key,
                label=label,
                if_match=prep_if_match(etag, match_condition),
                headers=custom_headers,
                error_map=error_map,
            )
            return ConfigurationSetting._from_key_value(key_value_deleted)
        except ErrorException as error:
            raise HttpResponseError(message=error.message, response=error.response)

    @distributed_trace
    def list_revisions(
        self, keys=None, labels=None, **kwargs
    ):  # type: (Optional[list], Optional[list], dict) -> azure.core.paging.AsyncItemPaged[ConfigurationSetting]

        """
        Find the ConfigurationSetting revision history.

        :param keys: filter results based on their keys. '*' can be
         used as wildcard in the beginning or end of the filter
        :type keys: list[str]
        :param labels: filter results based on their label. '*' can be
         used as wildcard in the beginning or end of the filter
        :type labels: list[str]
        :keyword datetime accept_datetime: filter out ConfigurationSetting created after this datetime
        :keyword list[str] fields: specify which fields to include in the results. Leave None to include all fields
        :keyword dict headers: if "headers" exists, its value (a dict) will be added to the http request header
        :return: An iterator of :class:`ConfigurationSetting`
        :rtype: :class:`azure.core.paging.ItemPaged[ConfigurationSetting]`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`

        Example

        .. code-block:: python

            # in async function
            from datetime import datetime, timedelta

            accept_datetime = datetime.today() + timedelta(days=-1)

            all_revisions = async_client.list_revisions()
            async for item in all_revisions:
                pass  # do something

            filtered_revisions = async_client.list_revisions(
                labels=["*Labe*"], keys=["*Ke*"], accept_datetime=accept_datetime
            )
            async for item in filtered_revisions:
                pass  # do something
        """
        select = kwargs.pop("fields", None)
        if select:
            select = ['locked' if x == 'read_only' else x for x in select]
        encoded_labels = escape_and_tostr(labels)
        encoded_keys = escape_and_tostr(keys)
        error_map = {
            401: ClientAuthenticationError
        }

        try:
            return self._impl.get_revisions(
                label=encoded_labels,
                key=encoded_keys,
                select=select,
                cls=lambda objs: [ConfigurationSetting._from_key_value(x) for x in objs],
                error_map=error_map,
                **kwargs
            )
        except ErrorException as error:
            raise HttpResponseError(message=error.message, response=error.response)

    @distributed_trace
    async def set_read_only(
            self, configuration_setting, read_only = True, **kwargs
    ):  # type: (ConfigurationSetting, Optional[bool], dict) -> ConfigurationSetting

        """Set a configuration setting read only

        :param configuration_setting: the ConfigurationSetting to be set read only
        :type configuration_setting: :class:`ConfigurationSetting`
        :param read_only: set the read only setting if true, else clear the read only setting
        :type read_only: bool
        :keyword dict headers: if "headers" exists, its value (a dict) will be added to the http request header
        :return: The ConfigurationSetting returned from the service
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`, :class:`ResourceNotFoundError`

        Example

        .. code-block:: python

            config_setting = await async_client.get_configuration_setting(
                key="MyKey", label="MyLabel"
            )

            read_only_config_setting = await async_client.set_read_only(config_setting)
            read_only_config_setting = await client.set_read_only(config_setting, read_only=False)
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError
        }

        try:
            if read_only:
                key_value = await self._impl.put_lock(
                    key=configuration_setting.key,
                    label=configuration_setting.label,
                    error_map=error_map,
                    **kwargs
                )
            else:
                key_value = await self._impl.delete_lock(
                    key=configuration_setting.key,
                    label=configuration_setting.label,
                    error_map=error_map,
                    **kwargs
                )
            return ConfigurationSetting._from_key_value(key_value)
        except ErrorException as error:
            raise HttpResponseError(message=error.message, response=error.response)
