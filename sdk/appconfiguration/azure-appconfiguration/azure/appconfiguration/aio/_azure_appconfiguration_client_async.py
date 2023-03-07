# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import binascii
from typing import Any, Dict, List, Mapping, Optional, Union
from requests.structures import CaseInsensitiveDict
from azure.core import MatchConditions
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    AsyncBearerTokenCredentialPolicy,
)
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import (
    HttpResponseError,
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
)
from ._sync_token_async import AsyncSyncTokenPolicy
from .._azure_appconfiguration_error import ResourceReadOnlyError
from .._azure_appconfiguration_requests import AppConfigRequestsCredentialsPolicy
from .._azure_appconfiguration_credential import AppConfigConnectionStringCredential
from .._generated.aio import AzureAppConfiguration
from .._generated.models import Snapshot, SnapshotStatus, SnapshotUpdateParameters
from .._models import ConfigurationSetting
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
        :type credential: :class:`azure.appconfiguration.AppConfigConnectionStringCredential`
            or :class:`~azure.core.credentials_async.AsyncTokenCredential`
        :keyword api_version: Api Version. Default value is "1.0". Note that overriding this default
            value may result in unsupported behavior.
        :paramtype api_version: str

    This is the async version of :class:`azure.appconfiguration.AzureAppConfigurationClient`

    """

    # pylint:disable=protected-access

    def __init__(self, base_url: str, credential: AsyncTokenCredential, **kwargs) -> None:
        try:
            if not base_url.lower().startswith("http"):
                base_url = "https://" + base_url
        except AttributeError:
            raise ValueError("Base URL must be a string.")

        if not credential:
            raise ValueError("Missing credential")

        credential_scopes = base_url.strip("/") + "/.default"

        user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)

        self._sync_token_policy = AsyncSyncTokenPolicy()

        aad_mode = not isinstance(credential, AppConfigConnectionStringCredential)
        if aad_mode:
            if hasattr(credential, "get_token"):
                credential_policy = AsyncBearerTokenCredentialPolicy(
                    credential, # type: ignore
                    credential_scopes,
                )
            else:
                raise TypeError(
                    "Please provide an instance from azure-identity "
                    "or a class that implement the 'get_token protocol"
                )
        else:
            credential_policy = AppConfigRequestsCredentialsPolicy(credential) # type: ignore

        self._impl = AzureAppConfiguration(
            base_url,
            credential_scopes=credential_scopes,
            authentication_policy=credential_policy,
            user_agent_policy=user_agent_policy,
            per_call_policies=self._sync_token_policy,
            **kwargs
        )

    @classmethod
    def from_connection_string(cls, connection_string: str, **kwargs) -> "AzureAppConfigurationClient":
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
            credential=AppConfigConnectionStringCredential(connection_string), # type: ignore
            base_url=base_url,
            **kwargs
        )

    @distributed_trace
    def list_configuration_settings(
        self,
        key_filter: Optional[str] = None,
        label_filter: Optional[str] = None,
        *,
        snapshot_name: Optional[str] = None,
        **kwargs
    ) -> AsyncItemPaged[ConfigurationSetting]:

        """List the configuration settings stored in the configuration service, optionally filtered by
        label and accept_datetime

        :param key_filter: filter results based on their keys. '*' can be
            used as wildcard in the beginning or end of the filter
        :type key_filter: str
        :param label_filter: filter results based on their label. '*' can be
            used as wildcard in the beginning or end of the filter
        :type label_filter: str
        :keyword str snapshot_name: A filter used get key-values for a snapshot. Not valid when used with 'key'
            and 'label' filters. Default value is None.
        :keyword datetime accept_datetime: filter out ConfigurationSetting created after this datetime
        :keyword List[str] fields: specify which fields to include in the results. Leave None to include all fields
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
                snapshot=snapshot_name,
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
        **kwargs
    ) -> ConfigurationSetting:

        """Add a ConfigurationSetting instance into the Azure App Configuration service.

        :param configuration_setting: the ConfigurationSetting object to be added
        :type configuration_setting: :class:`~azure.appconfiguration.ConfigurationSetting`
        :return: The ConfigurationSetting object returned from the App Configuration service
        :rtype: :class:`~azure.appconfiguration.ConfigurationSetting`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`, :class:`ResourceExistsError`

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
        **kwargs
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
        **kwargs
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
        self, key_filter: Optional[str] = None, label_filter: Optional[str] = None, **kwargs
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
        :keyword List[str] fields: specify which fields to include in the results. Leave None to include all fields
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
        self, configuration_setting: ConfigurationSetting, read_only: bool = True, **kwargs
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

    @distributed_trace
    async def create_snapshot(
        self,
        name: str,
        filters: List[Dict[str, str]],
        *,
        composition_type: Optional[str] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Snapshot:
        """Create a snapshot of the configuration settings.

        :param name: The name of the snapshot to create.
        :type name: str
        :param filters: A list of filters used to filter the configuration settings by key field and label field
            included in the snapshot. Each filter should be in format {"key": <value>, "label": <value>},
            and key field value is required.
        :type filters: list[dict[str, str]]
        :keyword str composition_type: The composition type describes how the key-values within the
            snapshot are composed. The 'all' composition type includes all key-values. The 'group_by_key'
            composition type ensures there are no two key-values containing the same key. Known values are:
            "all" and "group_by_key".
        :keyword int retention_period: The amount of time, in seconds, that a snapshot will remain in the
            archived state before expiring. This property is only writable during the creation of a
            snapshot. If not specified, will set to 2592000(30 days). If specified, should be
            in range 0 to 7776000(90 days). When set to 0, the snapshot will be deleted when archiving it.
        :keyword dict[str, str] tags: The tags of the snapshot.
        :return: The Snapshot returned from the service.
        :rtype: :class:`~azure.appconfiguration.models.Snapshot`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`, :class:`ResourceExistsError`
        """
        snapshot = Snapshot(
            filters=filters, composition_type=composition_type, retention_period=retention_period, tags=tags
        )
        error_map = {401: ClientAuthenticationError, 412: ResourceExistsError}
        try:
            return await self._impl.create_snapshot(
                name=name,
                entity=snapshot._to_generated(),
                error_map=error_map,
                **kwargs
            )
        except HttpResponseError as error:
            raise error

    @distributed_trace
    async def archive_snapshot(
        self,
        name: str,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        etag: Optional[str] = None,
        **kwargs
    ) -> Snapshot:
        """Archive a configuration setting snapshot. It will update the status of a snapshot from "ready" to "archived".

        :param name: The name of the configuration setting snapshot to archive.
        :type name: str
        :keyword match_condition: The match condition to use upon the etag.
        :type match_condition: :class:`~azure.core.MatchConditions`
        :keyword str etag: Check if the Snapshot is changed. Set None to skip checking etag.
        :return: The Snapshot returned from the service.
        :rtype: :class:`~azure.appconfiguration.models.Snapshot`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`, :class:`ResourceNotFoundError`, \
        :class:`ResourceModifiedError` :class`ResourceNotModifiedError` :class`ResourceExistsError`
        """
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError}
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[412] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError
        try:
            return await self._impl.update_snapshot(
                name=name,
                entity=SnapshotUpdateParameters(status=SnapshotStatus.ARCHIVED),
                if_match=prep_if_match(etag, match_condition),
                if_none_match=prep_if_none_match(etag, match_condition),
                error_map=error_map,
                **kwargs
            )
        except HttpResponseError as error:
            raise error

    @distributed_trace
    async def recover_snapshot(
        self,
        name: str,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        etag: Optional[str] = None,
        **kwargs
    ) -> Snapshot:
        """Recover a configuration setting snapshot. It will update the status of a snapshot from "archived" to "ready".

        :param name: The name of the configuration setting snapshot to recover.
        :type name: str
        :keyword match_condition: The match condition to use upon the etag.
        :type match_condition: :class:`~azure.core.MatchConditions`
        :keyword str etag: Check if the Snapshot is changed. Set None to skip checking etag.
        :return: The Snapshot returned from the service.
        :rtype: :class:`~azure.appconfiguration.models.Snapshot`
        :raises: :class:`HttpResponseError`, :class:`ClientAuthenticationError`, :class:`ResourceNotFoundError`, \
        :class:`ResourceModifiedError` :class`ResourceNotModifiedError` :class`ResourceExistsError`
        """
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError}
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[412] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError
        try:
            return await self._impl.update_snapshot(
                name=name,
                entity=SnapshotUpdateParameters(status=SnapshotStatus.READY),
                if_match=prep_if_match(etag, match_condition),
                if_none_match=prep_if_none_match(etag, match_condition),
                error_map=error_map,
                **kwargs
            )
        except HttpResponseError as error:
            raise error

    @distributed_trace
    async def get_snapshot(
        self,
        name: str,
        *,
        fields: Optional[List[str]] = None,
        **kwargs
    ) -> Snapshot:
        """Get a configuration setting snapshot.

        :param name: The name of the configuration setting snapshot to retrieve.
        :type name: str
        :keyword List[str] fields: Specify which fields to include in the results. Leave None to include all fields.
        :return: The Snapshot returned from the service.
        :rtype: :class:`~azure.appconfiguration.models.Snapshot`
        :raises: :class:`HttpResponseError`
        """
        try:
            return await self._impl.get_snapshot(
                name=name,
                if_match=None,
                if_none_match=None,
                select=fields,
                **kwargs
            )
        except HttpResponseError as error:
            raise error

    @distributed_trace
    def list_snapshots(
        self, *, name: Optional[str] = None, fields: Optional[List[str]] = None, status: Optional[str] = None, **kwargs
    ) -> AsyncItemPaged[Snapshot]:
        """List the configuration setting snapshots stored in the configuration service, optionally filtered by
        snapshot name and status.

        :keyword str name: Filter results based on snapshot name.
        :keyword List[str] fields: Specify which fields to include in the results. Leave None to include all fields.
        :keyword str status: Filter results based on snapshot keys.
        :return: An iterator of :class:`~azure.appconfiguration.models.Snapshot`
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.appconfiguration.models.Snapshot]
        :raises: :class:`HttpResponseError`
        """
        try:
            return self._impl.get_snapshots(  # type: ignore
                name=name,
                select=fields,
                status=status,
                **kwargs
            )
        except HttpResponseError as error:
            raise error

    async def update_sync_token(self, token: str) -> None:

        """Add a sync token to the internal list of tokens.

        :param str token: The sync token to be added to the internal list of tokens
        """

        await self._sync_token_policy.add_token(token)

    async def close(self) -> None:

        """Close all connections made by the client"""
        await self._impl._client.close()

    async def __aenter__(self):
        await self._impl.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self._impl.__aexit__(*args)
