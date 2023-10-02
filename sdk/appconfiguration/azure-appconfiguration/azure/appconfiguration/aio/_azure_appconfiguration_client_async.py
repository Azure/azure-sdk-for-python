# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import binascii
from typing import Any, Dict, List, Mapping, Optional, Union, cast, overload
from typing_extensions import Literal
from azure.core import MatchConditions
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    AsyncBearerTokenCredentialPolicy,
)
from azure.core.polling import AsyncLROPoller
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
)
from azure.core.utils import CaseInsensitiveDict
from ._sync_token_async import AsyncSyncTokenPolicy
from .._azure_appconfiguration_error import ResourceReadOnlyError
from .._azure_appconfiguration_requests import AppConfigRequestsCredentialsPolicy
from .._azure_appconfiguration_credential import AppConfigConnectionStringCredential
from .._generated.aio import AzureAppConfiguration
from .._generated.models import SnapshotUpdateParameters, SnapshotStatus
from .._models import ConfigurationSetting, ConfigurationSettingsFilter, ConfigurationSnapshot
from .._user_agent import USER_AGENT
from .._utils import (
    get_endpoint_from_connection_string,
    prep_if_match,
    prep_if_none_match,
)


class AzureAppConfigurationClient:
    """Represents a client that calls restful API of Azure App Configuration service.

        :param str base_url: Base url of the service.
        :param credential: An object which can provide secrets for the app configuration service
        :type credential: ~azure.appconfiguration.AppConfigConnectionStringCredential
            or ~azure.core.credentials_async.AsyncTokenCredential
        :keyword api_version: Api Version. Default value is "2022-11-01-preview". Note that overriding this default
            value may result in unsupported behavior.
        :paramtype api_version: str

    This is the async version of :class:`~azure.appconfiguration.AzureAppConfigurationClient`

    """

    # pylint:disable=protected-access

    def __init__(self, base_url: str, credential: AsyncTokenCredential, **kwargs: Any) -> None:
        try:
            if not base_url.lower().startswith("http"):
                base_url = "https://" + base_url
        except AttributeError as exc:
            raise ValueError("Base URL must be a string.") from exc

        if not credential:
            raise ValueError("Missing credential")

        credential_scopes = base_url.strip("/") + "/.default"

        user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)

        self._sync_token_policy = AsyncSyncTokenPolicy()

        aad_mode = not isinstance(credential, AppConfigConnectionStringCredential)
        if aad_mode:
            if hasattr(credential, "get_token"):
                credential_policy = AsyncBearerTokenCredentialPolicy(
                    credential,
                    credential_scopes,
                )
            else:
                raise TypeError(
                    "Please provide an instance from azure-identity or a class that implements the 'get_token' protocol"
                )
        else:
            credential_policy = AppConfigRequestsCredentialsPolicy(credential)  # type: ignore

        self._impl = AzureAppConfiguration(
            base_url,
            credential_scopes=credential_scopes,
            authentication_policy=credential_policy,
            user_agent_policy=user_agent_policy,
            per_call_policies=self._sync_token_policy,
            **kwargs
        )

    @classmethod
    def from_connection_string(cls, connection_string: str, **kwargs: Any) -> "AzureAppConfigurationClient":
        """Create AzureAppConfigurationClient from a Connection String.
        This is the async version of :class:`~azure.appconfiguration.AzureAppConfigurationClient`

        :param str connection_string: Connection String
            (one of the access keys of the Azure App Configuration resource)
            used to access the Azure App Configuration.
        :return: An AzureAppConfigurationClient authenticated with the connection string
        :rtype: ~azure.appconfiguration.AzureAppConfigurationClient

        Example

        .. code-block:: python

            from azure.appconfiguration.aio import AzureAppConfigurationClient
            connection_str = "<my connection string>"
            async_client = AzureAppConfigurationClient.from_connection_string(connection_str)
        """
        base_url = "https://" + get_endpoint_from_connection_string(connection_string)
        return cls(
            credential=AppConfigConnectionStringCredential(connection_string),  # type: ignore
            base_url=base_url,
            **kwargs
        )

    @overload
    def list_configuration_settings(
        self, *, key_filter: Optional[str] = None, label_filter: Optional[str] = None, **kwargs: Any
    ) -> AsyncItemPaged[ConfigurationSetting]:

        """List the configuration settings stored in the configuration service, optionally filtered by
        key, label and accept_datetime.

        :keyword key_filter: filter results based on their keys. '*' can be
            used as wildcard in the beginning or end of the filter
        :paramtype key_filter: str
        :keyword label_filter: filter results based on their label. '*' can be
            used as wildcard in the beginning or end of the filter
        :paramtype label_filter: str
        :keyword str accept_datetime: retrieve ConfigurationSetting existed at this datetime
        :keyword list[str] fields: specify which fields to include in the results. Leave None to include all fields
        :return: An async iterator of :class:`~azure.appconfiguration.ConfigurationSetting`
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.appconfiguration.ConfigurationSetting]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`

        Example

        .. code-block:: python

            from datetime import datetime, timedelta

            accept_datetime = datetime.utcnow() + timedelta(days=-1)

            all_listed = async_client.list_configuration_settings()
            async for item in all_listed:
                pass  # do something

            filtered_listed = async_client.list_configuration_settings(
                label_filter="Labe*", key_filter="Ke*", accept_datetime=str(accept_datetime)
            )
            async for item in filtered_listed:
                pass  # do something
        """

    @overload
    def list_configuration_settings(
        self, *, snapshot_name: str, fields: Optional[List[str]] = None, **kwargs: Any
    ) -> AsyncItemPaged[ConfigurationSetting]:
        """List the configuration settings stored under a snapshot in the configuration service, optionally filtered by
        accept_datetime and fields to present in return.

        :keyword str snapshot_name: The snapshot name.
        :keyword fields: Specify which fields to include in the results. Leave None to include all fields.
        :type fields: list[str] or None
        :return: An async iterator of :class:`~azure.appconfiguration.ConfigurationSetting`
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.appconfiguration.ConfigurationSetting]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """

    @distributed_trace
    def list_configuration_settings(self, **kwargs) -> AsyncItemPaged[ConfigurationSetting]:
        select = kwargs.pop("fields", None)
        if select:
            select = ["locked" if x == "read_only" else x for x in select]
        snapshot_name = kwargs.pop("snapshot_name", None)

        try:
            if snapshot_name is not None:
                return self._impl.get_key_values(  # type: ignore
                    snapshot=snapshot_name,
                    select=select,
                    cls=lambda objs: [ConfigurationSetting._from_generated(x) for x in objs],
                    **kwargs
                )
            return self._impl.get_key_values(  # type: ignore
                key=kwargs.pop("key_filter", None),
                label=kwargs.pop("label_filter", None),
                select=select,
                cls=lambda objs: [ConfigurationSetting._from_generated(x) for x in objs],
                **kwargs
            )
        except binascii.Error as exc:
            raise binascii.Error("Connection string secret has incorrect padding") from exc

    @distributed_trace_async
    async def get_configuration_setting(
        self,
        key: str,
        label: Optional[str] = None,
        etag: Optional[str] = "*",
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs
    ) -> Union[None, ConfigurationSetting]:

        """Get the matched ConfigurationSetting from Azure App Configuration service

        :param key: key of the ConfigurationSetting
        :type key: str
        :param label: label used to identify the ConfigurationSetting. Default is `None`.
        :type label: str
        :param etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :type etag: str or None
        :param match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions
        :keyword str accept_datetime: retrieve ConfigurationSetting existed at this datetime
        :return: The matched ConfigurationSetting object
        :rtype: ~azure.appconfiguration.ConfigurationSetting or None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`, \
            :class:`~azure.core.exceptions.ResourceNotFoundError`, \
            :class:`~azure.core.exceptions.ResourceModifiedError`, \
            :class:`~azure.core.exceptions.ResourceExistsError`

        Example

        .. code-block:: python

            # in async function
            fetched_config_setting = await async_client.get_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """
        error_map: Dict[int, Any] = {}
        if match_condition == MatchConditions.IfNotModified:
            error_map.update({412: ResourceModifiedError})
        if match_condition == MatchConditions.IfPresent:
            error_map.update({412: ResourceNotFoundError})
        if match_condition == MatchConditions.IfMissing:
            error_map.update({412: ResourceExistsError})

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
        except binascii.Error as exc:
            raise binascii.Error("Connection string secret has incorrect padding") from exc

    @distributed_trace_async
    async def add_configuration_setting(
        self, configuration_setting: ConfigurationSetting, **kwargs
    ) -> ConfigurationSetting:

        """Add a ConfigurationSetting instance into the Azure App Configuration service.

        :param configuration_setting: the ConfigurationSetting object to be added
        :type configuration_setting: ~azure.appconfiguration.ConfigurationSetting
        :return: The ConfigurationSetting object returned from the App Configuration service
        :rtype: ~azure.appconfiguration.ConfigurationSetting
        :raises: :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`, \
            :class:`~azure.core.exceptions.ResourceExistsError`

        Example

        .. code-block:: python

            # in async function
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
        custom_headers: Mapping[str, Any] = CaseInsensitiveDict(kwargs.get("headers"))
        error_map = {412: ResourceExistsError}

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
        except binascii.Error as exc:
            raise binascii.Error("Connection string secret has incorrect padding") from exc

    @distributed_trace_async
    async def set_configuration_setting(
        self,
        configuration_setting: ConfigurationSetting,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs
    ) -> ConfigurationSetting:

        """Add or update a ConfigurationSetting.
        If the configuration setting identified by key and label does not exist, this is a create.
        Otherwise this is an update.

        :param configuration_setting: the ConfigurationSetting to be added (if not exists)
            or updated (if exists) to the service
        :type configuration_setting: ~azure.appconfiguration.ConfigurationSetting
        :param match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions
        :keyword str etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :return: The ConfigurationSetting returned from the service
        :rtype: ~azure.appconfiguration.ConfigurationSetting
        :raises: :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`, \
            :class:`~azure.core.exceptions.ResourceReadOnlyError`, \
            :class:`~azure.core.exceptions.ResourceModifiedError`, \
            :class:`~azure.core.exceptions.ResourceNotModifiedError`, \
            :class:`~azure.core.exceptions.ResourceNotFoundError`, \
            :class:`~azure.core.exceptions.ResourceExistsError`

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
        custom_headers: Mapping[str, Any] = CaseInsensitiveDict(kwargs.get("headers"))
        error_map: Dict[int, Any] = {409: ResourceReadOnlyError}
        if match_condition == MatchConditions.IfNotModified:
            error_map.update({412: ResourceModifiedError})
        if match_condition == MatchConditions.IfModified:
            error_map.update({412: ResourceNotModifiedError})
        if match_condition == MatchConditions.IfPresent:
            error_map.update({412: ResourceNotFoundError})
        if match_condition == MatchConditions.IfMissing:
            error_map.update({412: ResourceExistsError})

        try:
            key_value_set = await self._impl.put_key_value(
                entity=key_value,
                key=key_value.key,  # type: ignore
                label=key_value.label,
                if_match=prep_if_match(configuration_setting.etag, match_condition),
                if_none_match=prep_if_none_match(etag, match_condition),
                headers=custom_headers,
                error_map=error_map,
            )
            return ConfigurationSetting._from_generated(key_value_set)
        except binascii.Error as exc:
            raise binascii.Error("Connection string secret has incorrect padding") from exc

    @distributed_trace_async
    async def delete_configuration_setting(
        self, key: str, label: Optional[str] = None, **kwargs
    ) -> ConfigurationSetting:
        """Delete a ConfigurationSetting if it exists

        :param key: key used to identify the ConfigurationSetting
        :type key: str
        :param label: label used to identify the ConfigurationSetting. Default is `None`.
        :type label: str
        :keyword str etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: The deleted ConfigurationSetting returned from the service, or None if it doesn't exist.
        :rtype: ~azure.appconfiguration.ConfigurationSetting
        :raises: :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`, \
            :class:`~azure.core.exceptions.ResourceReadOnlyError`, \
            :class:`~azure.core.exceptions.ResourceModifiedError`, \
            :class:`~azure.core.exceptions.ResourceNotModifiedError`, \
            :class:`~azure.core.exceptions.ResourceNotFoundError`, \
            :class:`~azure.core.exceptions.ResourceExistsError`

        Example

        .. code-block:: python

            # in async function
            deleted_config_setting = await async_client.delete_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """
        etag = kwargs.pop("etag", None)
        match_condition = kwargs.pop("match_condition", MatchConditions.Unconditionally)
        custom_headers: Mapping[str, Any] = CaseInsensitiveDict(kwargs.get("headers"))
        error_map: Dict[int, Any] = {409: ResourceReadOnlyError}
        if match_condition == MatchConditions.IfNotModified:
            error_map.update({412: ResourceModifiedError})
        if match_condition == MatchConditions.IfModified:
            error_map.update({412: ResourceNotModifiedError})
        if match_condition == MatchConditions.IfPresent:
            error_map.update({412: ResourceNotFoundError})
        if match_condition == MatchConditions.IfMissing:
            error_map.update({412: ResourceExistsError})

        try:
            key_value_deleted = await self._impl.delete_key_value(
                key=key,
                label=label,
                if_match=prep_if_match(etag, match_condition),
                headers=custom_headers,
                error_map=error_map,
            )
            return ConfigurationSetting._from_generated(key_value_deleted)  # type: ignore
        except binascii.Error as exc:
            raise binascii.Error("Connection string secret has incorrect padding") from exc

    @distributed_trace
    def list_revisions(
        self, key_filter: Optional[str] = None, label_filter: Optional[str] = None, **kwargs
    ) -> AsyncItemPaged[ConfigurationSetting]:

        """
        Find the ConfigurationSetting revision history, optionally filtered by key, label and accept_datetime.

        :param key_filter: filter results based on their keys. '*' can be
            used as wildcard in the beginning or end of the filter
        :type key_filter: str
        :param label_filter: filter results based on their label. '*' can be
            used as wildcard in the beginning or end of the filter
        :type label_filter: str
        :keyword str accept_datetime: retrieve ConfigurationSetting existed at this datetime
        :keyword list[str] fields: specify which fields to include in the results. Leave None to include all fields
        :return: An async iterator of :class:`~azure.appconfiguration.ConfigurationSetting`
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.appconfiguration.ConfigurationSetting]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`

        Example

        .. code-block:: python

            # in async function
            from datetime import datetime, timedelta

            accept_datetime = datetime.utcnow() + timedelta(days=-1)

            all_revisions = async_client.list_revisions()
            async for item in all_revisions:
                pass  # do something

            filtered_revisions = async_client.list_revisions(
                label_filter="Labe*", key_filter="Ke*", accept_datetime=str(accept_datetime)
            )
            async for item in filtered_revisions:
                pass  # do something
        """
        select = kwargs.pop("fields", None)
        if select:
            select = ["locked" if x == "read_only" else x for x in select]

        try:
            return self._impl.get_revisions(  # type: ignore
                label=label_filter,
                key=key_filter,
                select=select,
                cls=lambda objs: [ConfigurationSetting._from_generated(x) for x in objs],
                **kwargs
            )
        except binascii.Error as exc:
            raise binascii.Error("Connection string secret has incorrect padding") from exc

    @distributed_trace_async
    async def set_read_only(
        self, configuration_setting: ConfigurationSetting, read_only: bool = True, **kwargs
    ) -> ConfigurationSetting:

        """Set a configuration setting read only

        :param configuration_setting: the ConfigurationSetting to be set read only
        :type configuration_setting: ~azure.appconfiguration.ConfigurationSetting
        :param read_only: set the read only setting if true, else clear the read only setting
        :type read_only: bool
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword str etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :return: The ConfigurationSetting returned from the service
        :rtype: ~azure.appconfiguration.ConfigurationSetting
        :raises: :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`, \
            :class:`~azure.core.exceptions.ResourceNotFoundError`

        Example

        .. code-block:: python

            config_setting = await async_client.get_configuration_setting(
                key="MyKey", label="MyLabel"
            )

            read_only_config_setting = await async_client.set_read_only(config_setting)
            read_only_config_setting = await client.set_read_only(config_setting, read_only=False)
        """
        error_map: Dict[int, Any] = {}
        match_condition = kwargs.pop("match_condition", MatchConditions.Unconditionally)
        if match_condition == MatchConditions.IfNotModified:
            error_map.update({412: ResourceModifiedError})
        if match_condition == MatchConditions.IfModified:
            error_map.update({412: ResourceNotModifiedError})
        if match_condition == MatchConditions.IfPresent:
            error_map.update({412: ResourceNotFoundError})
        if match_condition == MatchConditions.IfMissing:
            error_map.update({412: ResourceExistsError})

        try:
            if read_only:
                key_value = await self._impl.put_lock(
                    key=configuration_setting.key,
                    label=configuration_setting.label,
                    if_match=prep_if_match(configuration_setting.etag, match_condition),
                    if_none_match=prep_if_none_match(configuration_setting.etag, match_condition),
                    error_map=error_map,
                    **kwargs
                )
            else:
                key_value = await self._impl.delete_lock(
                    key=configuration_setting.key,
                    label=configuration_setting.label,
                    if_match=prep_if_match(configuration_setting.etag, match_condition),
                    if_none_match=prep_if_none_match(configuration_setting.etag, match_condition),
                    error_map=error_map,
                    **kwargs
                )
            return ConfigurationSetting._from_generated(key_value)
        except binascii.Error as exc:
            raise binascii.Error("Connection string secret has incorrect padding") from exc

    @distributed_trace_async
    async def begin_create_snapshot(
        self,
        name: str,
        filters: List[ConfigurationSettingsFilter],
        *,
        composition_type: Optional[Literal["key", "key_label"]] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> AsyncLROPoller[ConfigurationSnapshot]:
        """Create a snapshot of the configuration settings.

        :param name: The name of the configuration snapshot to create.
        :type name: str
        :param filters: A list of filters used to filter the configuration settings by key field and label field
            included in the configuration snapshot.
        :type filters: list[~azure.appconfiguration.ConfigurationSettingsFilter]
        :keyword composition_type: The composition type describes how the key-values within the configuration
            snapshot are composed. Known values are: "key" and "key_label". The "key" composition type
            ensures there are no two key-values containing the same key. The 'key_label' composition type ensures
            there are no two key-values containing the same key and label.
        :type composition_type: str or None
        :keyword retention_period: The amount of time, in seconds, that a configuration snapshot will remain in the
            archived state before expiring. This property is only writable during the creation of a configuration
            snapshot. If not specified, will set to 2592000(30 days). If specified, should be
            in range 3600(1 hour) to 7776000(90 days).
        :type retention_period: int or None
        :keyword tags: The tags of the configuration snapshot.
        :type tags: dict[str, str] or None
        :return: A poller for create configuration snapshot operation. Call `result()` on this object to wait for the
            operation to complete and get the created snapshot.
        :rtype: ~azure.core.polling.LROPoller[~azure.appconfiguration.ConfigurationSnapshot]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        snapshot = ConfigurationSnapshot(
            filters=filters, composition_type=composition_type, retention_period=retention_period, tags=tags
        )
        try:
            return cast(
                AsyncLROPoller[ConfigurationSnapshot],
                await self._impl.begin_create_snapshot(
                    name=name, entity=snapshot._to_generated(), cls=ConfigurationSnapshot._from_deserialized, **kwargs
                ),
            )
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")  # pylint: disable=raise-missing-from

    @distributed_trace_async
    async def archive_snapshot(
        self,
        name: str,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        etag: Optional[str] = None,
        **kwargs
    ) -> ConfigurationSnapshot:
        """Archive a configuration setting snapshot. It will update the status of a snapshot from "ready" to "archived".
        The retention period will start to count, the snapshot will expire when the entire retention period elapses.

        :param name: The name of the configuration setting snapshot to archive.
        :type name: str
        :keyword match_condition: The match condition to use upon the etag.
        :type match_condition: ~azure.core.MatchConditions
        :keyword etag: Check if the ConfigurationSnapshot is changed. Set None to skip checking etag.
        :type etag: str or None
        :return: The ConfigurationSnapshot returned from the service.
        :rtype: ~azure.appconfiguration.ConfigurationSnapshot
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        error_map: Dict[int, Any] = {}
        if match_condition == MatchConditions.IfNotModified:
            error_map.update({412: ResourceModifiedError})
        if match_condition == MatchConditions.IfModified:
            error_map.update({412: ResourceNotModifiedError})
        if match_condition == MatchConditions.IfPresent:
            error_map.update({412: ResourceNotFoundError})
        if match_condition == MatchConditions.IfMissing:
            error_map.update({412: ResourceExistsError})
        try:
            generated_snapshot = await self._impl.update_snapshot(
                name=name,
                entity=SnapshotUpdateParameters(status=SnapshotStatus.ARCHIVED),
                if_match=prep_if_match(etag, match_condition),
                if_none_match=prep_if_none_match(etag, match_condition),
                error_map=error_map,
                **kwargs
            )
            return ConfigurationSnapshot._from_generated(generated_snapshot)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")  # pylint: disable=raise-missing-from

    @distributed_trace_async
    async def recover_snapshot(
        self,
        name: str,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        etag: Optional[str] = None,
        **kwargs
    ) -> ConfigurationSnapshot:
        """Recover a configuration setting snapshot. It will update the status of a snapshot from "archived" to "ready".

        :param name: The name of the configuration setting snapshot to recover.
        :type name: str
        :keyword match_condition: The match condition to use upon the etag.
        :type match_condition: ~azure.core.MatchConditions
        :keyword etag: Check if the ConfigurationSnapshot is changed. Set None to skip checking etag.
        :type etag: str or None
        :return: The ConfigurationSnapshot returned from the service.
        :rtype: ~azure.appconfiguration.ConfigurationSnapshot
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        error_map: Dict[int, Any] = {}
        if match_condition == MatchConditions.IfNotModified:
            error_map.update({412: ResourceModifiedError})
        if match_condition == MatchConditions.IfModified:
            error_map.update({412: ResourceNotModifiedError})
        if match_condition == MatchConditions.IfPresent:
            error_map.update({412: ResourceNotFoundError})
        if match_condition == MatchConditions.IfMissing:
            error_map.update({412: ResourceExistsError})
        try:
            generated_snapshot = await self._impl.update_snapshot(
                name=name,
                entity=SnapshotUpdateParameters(status=SnapshotStatus.READY),
                if_match=prep_if_match(etag, match_condition),
                if_none_match=prep_if_none_match(etag, match_condition),
                error_map=error_map,
                **kwargs
            )
            return ConfigurationSnapshot._from_generated(generated_snapshot)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")  # pylint: disable=raise-missing-from

    @distributed_trace_async
    async def get_snapshot(self, name: str, *, fields: Optional[List[str]] = None, **kwargs) -> ConfigurationSnapshot:
        """Get a configuration setting snapshot.

        :param name: The name of the configuration setting snapshot to retrieve.
        :type name: str
        :keyword fields: Specify which fields to include in the results. Leave None to include all fields.
        :type fields: list[str] or None
        :return: The ConfigurationSnapshot returned from the service.
        :rtype: ~azure.appconfiguration.ConfigurationSnapshot
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        try:
            generated_snapshot = await self._impl.get_snapshot(
                name=name, if_match=None, if_none_match=None, select=fields, **kwargs
            )
            return ConfigurationSnapshot._from_generated(generated_snapshot)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")  # pylint: disable=raise-missing-from

    @distributed_trace
    def list_snapshots(
        self,
        *,
        name: Optional[str] = None,
        fields: Optional[List[str]] = None,
        status: Optional[List[Union[str, SnapshotStatus]]] = None,
        **kwargs
    ) -> AsyncItemPaged[ConfigurationSnapshot]:
        """List the configuration setting snapshots stored in the configuration service, optionally filtered by
        snapshot name, snapshot status and fields to present in return.

        :keyword name: Filter results based on snapshot name.
        :type name: str or None
        :keyword fields: Specify which fields to include in the results. Leave None to include all fields.
        :type fields: list[str] or None
        :keyword status: Filter results based on snapshot keys.
        :type status: list[str] or list[~azure.appconfiguration.SnapshotStatus] or None
        :return: An iterator of :class:`~azure.appconfiguration.ConfigurationSnapshot`
        :rtype: ~azure.core.paging.ItemPaged[~azure.appconfiguration.ConfigurationSnapshot]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        try:
            return self._impl.get_snapshots(  # type: ignore
                name=name,
                select=fields,
                status=status,
                cls=lambda objs: [ConfigurationSnapshot._from_generated(x) for x in objs],
                **kwargs
            )
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")  # pylint: disable=raise-missing-from

    async def update_sync_token(self, token: str) -> None:

        """Add a sync token to the internal list of tokens.

        :param str token: The sync token to be added to the internal list of tokens
        """

        await self._sync_token_policy.add_token(token)

    async def close(self) -> None:

        """Close all connections made by the client"""
        await self._impl._client.close()

    async def __aenter__(self) -> "AzureAppConfigurationClient":
        await self._impl.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._impl.__aexit__(*args)
