# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import binascii
from typing import Dict, Any, Optional, Mapping, Union, TYPE_CHECKING
from requests.structures import CaseInsensitiveDict
from azure.core import MatchConditions
from azure.core.async_paging import AsyncItemPaged
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    AsyncBearerTokenCredentialPolicy,
    ContentDecodePolicy,
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
    prep_if_match,
    prep_if_none_match,
)
from .._generated.aio import AzureAppConfiguration
from .._generated.aio._configuration import AzureAppConfigurationConfiguration
from .._azure_appconfiguration_requests import AppConfigRequestsCredentialsPolicy
from .._azure_appconfiguration_credential import AppConfigConnectionStringCredential
from .._models import ConfigurationSetting
from .._user_agent import USER_AGENT
from ._sync_token_async import AsyncSyncTokenPolicy

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class AzureAppConfigurationClient: # pylint: disable=client-accepts-api-version-keyword
    # pylint:disable=line-too-long
    """Represents a client that calls restful API of Azure App Configuration service.

        :param str base_url: base url of the service
        :param credential: An object which can provide secrets for the app configuration service
        :type credential: :class:`azure.appconfiguration.AppConfigConnectionStringCredential` or :class:`~azure.core.credentials_async.AsyncTokenCredential`

    This is the async version of :class:`azure.appconfiguration.AzureAppConfigurationClient`

    """

    # pylint:disable=protected-access

    def __init__(
        self,
        base_url: str,
        credential: Union[AppConfigConnectionStringCredential, "AsyncTokenCredential"],
        **kwargs: Any
    ) -> None:
        try:
            if not base_url.lower().startswith("http"):
                base_url = "https://" + base_url
        except AttributeError:
            raise ValueError("Base URL must be a string.")

        if not credential:
            raise ValueError("Missing credential")

        self._credential_scopes = base_url.strip("/") + "/.default"

        self._config = AzureAppConfigurationConfiguration(
            credential, base_url, credential_scopes=self._credential_scopes, **kwargs  # type: ignore
        )
        self._config.user_agent_policy = UserAgentPolicy(
            base_user_agent=USER_AGENT, **kwargs
        )

        pipeline = kwargs.get("pipeline")
        self._sync_token_policy = AsyncSyncTokenPolicy()

        if pipeline is None:
            aad_mode = not isinstance(credential, AppConfigConnectionStringCredential)
            pipeline = self._create_appconfig_pipeline(
                credential=credential, aad_mode=aad_mode, base_url=base_url, **kwargs
            )

        self._impl = AzureAppConfiguration(
            credential, base_url, credential_scopes=self._credential_scopes, pipeline=pipeline  # type: ignore
        )

    @classmethod
    def from_connection_string(cls, connection_string: str, **kwargs: Any) -> "AzureAppConfigurationClient":
        """Create AzureAppConfigurationClient from a Connection String.
        This is the async version of :class:`azure.appconfiguration.AzureAppConfigurationClient`

        :param str connection_string: Connection String
            (one of the access keys of the Azure App Configuration resource)
            used to access the Azure App Configuration.
        :return: An AzureAppConfigurationClient authenticated with the connection string
        :rtype: :class:`~azure.appconfiguration.AzureAppConfigurationClient`

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

    def _create_appconfig_pipeline(
        self, credential, base_url=None, aad_mode=False, **kwargs
    ):
        transport = kwargs.get("transport")
        policies = kwargs.get("policies")

        if policies is None:  # [] is a valid policy list
            if aad_mode:
                scope = base_url.strip("/") + "/.default"
                if hasattr(credential, "get_token"):
                    credential_policy = AsyncBearerTokenCredentialPolicy(
                        credential, scope
                    )
                else:
                    raise TypeError(
                        "Please provide an instance from azure-identity "
                        "or a class that implement the 'get_token protocol"
                    )
            else:
                credential_policy = AppConfigRequestsCredentialsPolicy(credential)

            policies = [
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.retry_policy,
                self._sync_token_policy,
                credential_policy,
                self._config.logging_policy,  # HTTP request/response log
                DistributedTracingPolicy(**kwargs),
                HttpLoggingPolicy(**kwargs),
                ContentDecodePolicy(**kwargs),
            ]

        if not transport:
            transport = AsyncioRequestsTransport(**kwargs)

        return AsyncPipeline(
            transport,
            policies,
        )

    @distributed_trace
    def list_configuration_settings(
        self,
        key_filter: Optional[str] = None,
        label_filter: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[ConfigurationSetting]:

        """List the configuration settings stored in the configuration service, optionally filtered by
        label and accept_datetime

        :param key_filter: filter results based on their keys. '*' can be
         used as wildcard in the beginning or end of the filter
        :type key_filter: str
        :param label_filter: filter results based on their label. '*' can be
         used as wildcard in the beginning or end of the filter
        :type label_filter: str
        :keyword datetime accept_datetime: filter out ConfigurationSetting created after this datetime
        :keyword list[str] fields: specify which fields to include in the results. Leave None to include all fields
        :return: An iterator of :class:`ConfigurationSetting`
        :rtype: ~azure.core.async_paging.AsyncItemPaged[ConfigurationSetting]
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`

        Example

        .. code-block:: python

            from datetime import datetime, timedelta

            accept_datetime = datetime.today() + timedelta(days=-1)

            all_listed = async_client.list_configuration_settings()
            async for item in all_listed:
                pass  # do something

            filtered_listed = async_client.list_configuration_settings(
                label_filter="Labe*", key_filter="Ke*", accept_datetime=accept_datetime
            )
            async for item in filtered_listed:
                pass  # do something
        """
        select = kwargs.pop("fields", None)
        if select:
            select = ["locked" if x == "read_only" else x for x in select]
        error_map = {401: ClientAuthenticationError}

        try:
            return self._impl.get_key_values(  # type: ignore
                label=label_filter,
                key=key_filter,
                select=select,
                cls=lambda objs: [
                    ConfigurationSetting._from_generated(x) for x in objs
                ],
                error_map=error_map,
                **kwargs
            )
        except HttpResponseError as error:
            e = error_map[error.status_code]
            raise e(message=error.message, response=error.response)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")

    @distributed_trace_async
    async def get_configuration_setting(
        self,
        key: str,
        label: Optional[str] = None,
        etag: Optional[str] = "*",
        match_condition: Optional[MatchConditions] = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> Union[None, ConfigurationSetting]:

        """Get the matched ConfigurationSetting from Azure App Configuration service

        :param key: key of the ConfigurationSetting
        :type key: str
        :param label: label used to identify the ConfigurationSetting. Default is `None`.
        :type label: str
        :param etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :type etag: str or None
        :param match_condition: The match condition to use upon the etag
        :type match_condition: :class:`~azure.core.MatchConditions`
        :keyword datetime accept_datetime: the retrieved ConfigurationSetting that created no later than this datetime
        :return: The matched ConfigurationSetting object
        :rtype: :class:`~azure.appconfiguration.ConfigurationSetting`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`, \
        :class:`ResourceNotFoundError`, :class:`ResourceModifiedError`, :class:`ResourceExistsError`

        Example

        .. code-block:: python

            # in async function
            fetched_config_setting = await async_client.get_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError}
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
            return ConfigurationSetting._from_generated(key_value)
        except ResourceNotModifiedError:
            return None
        except HttpResponseError as error:
            e = error_map[error.status_code]
            raise e(message=error.message, response=error.response)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")

    @distributed_trace_async
    async def add_configuration_setting(
        self,
        configuration_setting: ConfigurationSetting,
        **kwargs: Any
    ) -> ConfigurationSetting:

        """Add a ConfigurationSetting instance into the Azure App Configuration service.

        :param configuration_setting: the ConfigurationSetting object to be added
        :type configuration_setting: :class:`~azure.appconfiguration.ConfigurationSetting`
        :return: The ConfigurationSetting object returned from the App Configuration service
        :rtype: :class:`~azure.appconfiguration.ConfigurationSetting`
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
        key_value = configuration_setting._to_generated()
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))  # type: Mapping[str, Any]
        error_map = {401: ClientAuthenticationError, 412: ResourceExistsError}

        try:
            key_value_added = await self._impl.put_key_value(
                entity=key_value,
                key=key_value.key,  # type: ignore
                label=key_value.label,
                if_none_match="*",
                headers=custom_headers,
                error_map=error_map,
            )
            return ConfigurationSetting._from_generated(key_value_added)
        except HttpResponseError as error:
            e = error_map[error.status_code]
            raise e(message=error.message, response=error.response)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")

    @distributed_trace_async
    async def set_configuration_setting(
        self,
        configuration_setting: ConfigurationSetting,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> ConfigurationSetting:

        """Add or update a ConfigurationSetting.
        If the configuration setting identified by key and label does not exist, this is a create.
        Otherwise this is an update.

        :param configuration_setting: the ConfigurationSetting to be added (if not exists) \
        or updated (if exists) to the service
        :type configuration_setting: :class:`ConfigurationSetting`
        :param match_condition: The match condition to use upon the etag
        :type match_condition: :class:`~azure.core.MatchConditions`
        :keyword str etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :return: The ConfigurationSetting returned from the service
        :rtype: :class:`~azure.appconfiguration.ConfigurationSetting`
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
        etag = kwargs.get("etag", configuration_setting.etag)

        key_value = configuration_setting._to_generated()
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))  # type: Mapping[str, Any]
        error_map = {401: ClientAuthenticationError, 409: ResourceReadOnlyError}
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
                key=key_value.key,  # type: ignore
                label=key_value.label,
                if_match=prep_if_match(configuration_setting.etag, match_condition),
                if_none_match=prep_if_none_match(
                    etag, match_condition
                ),
                headers=custom_headers,
                error_map=error_map,
            )
            return ConfigurationSetting._from_generated(key_value_set)
        except HttpResponseError as error:
            e = error_map[error.status_code]
            raise e(message=error.message, response=error.response)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")

    @distributed_trace_async
    async def delete_configuration_setting(
        self,
        key: str,
        label: Optional[str] = None,
        **kwargs: Any
    ) -> ConfigurationSetting:
        """Delete a ConfigurationSetting if it exists

        :param key: key used to identify the ConfigurationSetting
        :type key: str
        :param label: label used to identify the ConfigurationSetting. Default is `None`.
        :type label: str
        :keyword str etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: :class:`~azure.core.MatchConditions`
        :return: The deleted ConfigurationSetting returned from the service, or None if it doesn't exist.
        :rtype: :class:`~azure.appconfiguration.ConfigurationSetting`
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
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))  # type: Mapping[str, Any]
        error_map = {401: ClientAuthenticationError, 409: ResourceReadOnlyError}
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
            return ConfigurationSetting._from_generated(key_value_deleted)  # type: ignore
        except HttpResponseError as error:
            e = error_map[error.status_code]
            raise e(message=error.message, response=error.response)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")

    @distributed_trace
    def list_revisions(
        self, key_filter: Optional[str] = None, label_filter: Optional[str] = None, **kwargs: Any
    ) -> AsyncItemPaged[ConfigurationSetting]:

        """
        Find the ConfigurationSetting revision history.

        :param key_filter: filter results based on their keys. '*' can be
         used as wildcard in the beginning or end of the filter
        :type key_filter: str
        :param label_filter: filter results based on their label. '*' can be
         used as wildcard in the beginning or end of the filter
        :type label_filter: str
        :keyword datetime accept_datetime: filter out ConfigurationSetting created after this datetime
        :keyword list[str] fields: specify which fields to include in the results. Leave None to include all fields
        :return: An iterator of :class:`ConfigurationSetting`
        :rtype: ~azure.core.async_paging.AsyncItemPaged[ConfigurationSetting]
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
                label_filter="Labe*", key_filter="Ke*", accept_datetime=accept_datetime
            )
            async for item in filtered_revisions:
                pass  # do something
        """
        select = kwargs.pop("fields", None)
        if select:
            select = ["locked" if x == "read_only" else x for x in select]
        error_map = {401: ClientAuthenticationError}

        try:
            return self._impl.get_revisions(  # type: ignore
                label=label_filter,
                key=key_filter,
                select=select,
                cls=lambda objs: [
                    ConfigurationSetting._from_generated(x) for x in objs
                ],
                error_map=error_map,
                **kwargs
            )
        except HttpResponseError as error:
            e = error_map[error.status_code]
            raise e(message=error.message, response=error.response)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")

    @distributed_trace
    async def set_read_only(
        self, configuration_setting: ConfigurationSetting, read_only: Optional[bool] = True, **kwargs: Any
    ) -> ConfigurationSetting:

        """Set a configuration setting read only

        :param configuration_setting: the ConfigurationSetting to be set read only
        :type configuration_setting: :class:`ConfigurationSetting`
        :param read_only: set the read only setting if true, else clear the read only setting
        :type read_only: bool
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: :class:`~azure.core.MatchConditions`
        :keyword str etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :return: The ConfigurationSetting returned from the service
        :rtype: :class:`~azure.appconfiguration.ConfigurationSetting`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`, :class:`ResourceNotFoundError`

        Example

        .. code-block:: python

            config_setting = await async_client.get_configuration_setting(
                key="MyKey", label="MyLabel"
            )

            read_only_config_setting = await async_client.set_read_only(config_setting)
            read_only_config_setting = await client.set_read_only(config_setting, read_only=False)
        """
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError}

        match_condition = kwargs.pop("match_condition", MatchConditions.Unconditionally)
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[412] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError

        try:
            if read_only:
                key_value = await self._impl.put_lock(
                    key=configuration_setting.key,
                    label=configuration_setting.label,
                    if_match=prep_if_match(configuration_setting.etag, match_condition),
                    if_none_match=prep_if_none_match(
                        configuration_setting.etag, match_condition
                    ),
                    error_map=error_map,
                    **kwargs
                )
            else:
                key_value = await self._impl.delete_lock(
                    key=configuration_setting.key,
                    label=configuration_setting.label,
                    if_match=prep_if_match(configuration_setting.etag, match_condition),
                    if_none_match=prep_if_none_match(
                        configuration_setting.etag, match_condition
                    ),
                    error_map=error_map,
                    **kwargs
                )
            return ConfigurationSetting._from_generated(key_value)
        except HttpResponseError as error:
            e = error_map[error.status_code]
            raise e(message=error.message, response=error.response)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")

    def update_sync_token(self, token: str) -> None:

        """Add a sync token to the internal list of tokens.

        :param str token: The sync token to be added to the internal list of tokens
        """

        self._sync_token_policy.add_token(token)

    async def close(self) -> None:

        """Close all connections made by the client"""
        await self._impl._client.close()

    async def __aenter__(self):
        await self._impl.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self._impl.__aexit__(*args)
