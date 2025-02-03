# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import functools
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, overload, cast
from azure.core import MatchConditions
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.polling import AsyncLROPoller
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import ResourceNotModifiedError
from azure.core.rest import AsyncHttpResponse, HttpRequest
from ._sync_token_async import AsyncSyncTokenPolicy
from .._azure_appconfiguration_error import ResourceReadOnlyError
from .._azure_appconfiguration_requests import AppConfigRequestsCredentialsPolicy
from .._generated.aio import AzureAppConfigurationClient as AzureAppConfigurationClientGenerated
from .._generated.models import (
    SnapshotStatus,
    SnapshotFields,
    SnapshotComposition,
    LabelFields,
    ConfigurationSettingFields,
    SnapshotUpdateParameters,
)
from .._models import (
    ConfigurationSetting,
    ConfigurationSettingPropertiesPagedAsync,
    ConfigurationSettingsFilter,
    ConfigurationSnapshot,
    ConfigurationSettingLabel,
)
from .._utils import (
    get_key_filter,
    get_label_filter,
    parse_connection_string,
)


class AzureAppConfigurationClient:
    """Represents a client that calls restful API of Azure App Configuration service.

    :param str base_url: Base url of the service.
    :param credential: An object which can provide secrets for the app configuration service
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: Api Version. Default value is "2023-11-01". Note that overriding this default
        value may result in unsupported behavior.
    :paramtype api_version: str

    This is the async version of :class:`~azure.appconfiguration.AzureAppConfigurationClient`

    """

    # pylint:disable=protected-access
    def __init__(self, base_url: str, credential: AsyncTokenCredential, **kwargs: Any) -> None:
        try:
            if not base_url.lower().startswith("http"):
                base_url = f"https://{base_url}"
        except AttributeError as exc:
            raise ValueError("Base URL must be a string.") from exc

        if not credential:
            raise ValueError("Missing credential")

        credential_scopes = [f"{base_url.strip('/')}/.default"]
        self._sync_token_policy = AsyncSyncTokenPolicy()

        if isinstance(credential, AzureKeyCredential):
            id_credential = kwargs.pop("id_credential")
            kwargs.update(
                {
                    "authentication_policy": AppConfigRequestsCredentialsPolicy(credential, base_url, id_credential),
                }
            )
        elif hasattr(credential, "get_token"):  # AsyncFakeCredential is not an instance of AsyncTokenCredential
            kwargs.update(
                {
                    "authentication_policy": AsyncBearerTokenCredentialPolicy(credential, *credential_scopes, **kwargs),
                }
            )
        else:
            raise TypeError(
                f"Unsupported credential: {type(credential)}. Use an instance of token credential from azure.identity"
            )
        # mypy doesn't compare the credential type hint with the API surface in patch.py
        self._impl = AzureAppConfigurationClientGenerated(
            base_url, credential, per_call_policies=self._sync_token_policy, **kwargs  # type: ignore[arg-type]
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
        endpoint, id_credential, secret = parse_connection_string(connection_string)
        # AzureKeyCredential type is for internal use, it's not exposed in public API.
        return cls(
            credential=AzureKeyCredential(secret),  # type: ignore[arg-type]
            base_url=endpoint,
            id_credential=id_credential,
            **kwargs,
        )

    @distributed_trace_async
    async def send_request(self, request: HttpRequest, *, stream: bool = False, **kwargs: Any) -> AsyncHttpResponse:
        """Runs a network request using the client's existing pipeline.

        The request URL can be relative to the vault URL. The service API version used for the request is the same as
        the client's unless otherwise specified. This method does not raise if the response is an error; to raise an
        exception, call `raise_for_status()` on the returned response object. For more information about how to send
        custom requests with this method, see https://aka.ms/azsdk/dpcodegen/python/send_request.

        :param request: The network request you want to make.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.AsyncHttpResponse
        """
        return await self._impl.send_request(request, stream=stream, **kwargs)

    @overload
    def list_configuration_settings(
        self,
        *,
        key_filter: Optional[str] = None,
        label_filter: Optional[str] = None,
        tags_filter: Optional[List[str]] = None,
        accept_datetime: Optional[Union[datetime, str]] = None,
        fields: Optional[List[Union[str, ConfigurationSettingFields]]] = None,
        **kwargs: Any,
    ) -> AsyncItemPaged[ConfigurationSetting]:
        """List the configuration settings stored in the configuration service, optionally filtered by
        key, label, tags and accept_datetime. For more information about supported filters, see
        https://learn.microsoft.com/azure/azure-app-configuration/rest-api-key-value?pivots=v23-11#supported-filters.

        :keyword key_filter: Filter results based on their keys. '*' can be used as wildcard in the beginning or end
            of the filter.
        :paramtype key_filter: str or None
        :keyword label_filter: Filter results based on their label. '*' can be used as wildcard in the beginning or end
            of the filter.
        :paramtype label_filter: str or None
        :keyword tags_filter: Filter results based on their tags.
        :paramtype tags_filter: list[str] or None
        :keyword accept_datetime: Retrieve ConfigurationSetting that existed at this datetime
        :paramtype accept_datetime: ~datetime.datetime or str or None
        :keyword fields: Specify which fields to include in the results. If not specified, will include all fields.
            Available fields see :class:`~azure.appconfiguration.ConfigurationSettingFields`.
        :paramtype fields: list[str] or list[~azure.appconfiguration.ConfigurationSettingFields] or None
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
        self,
        *,
        snapshot_name: str,
        fields: Optional[List[Union[str, ConfigurationSettingFields]]] = None,
        **kwargs: Any,
    ) -> AsyncItemPaged[ConfigurationSetting]:
        """List the configuration settings stored under a snapshot in the configuration service, optionally filtered by
        accept_datetime and fields to present in return.

        :keyword str snapshot_name: The snapshot name.
        :keyword fields: Specify which fields to include in the results. If not specified, will include all fields.
            Available fields see :class:`~azure.appconfiguration.ConfigurationSettingFields`.
        :paramtype fields: list[str] or list[~azure.appconfiguration.ConfigurationSettingFields] or None
        :return: An async iterator of :class:`~azure.appconfiguration.ConfigurationSetting`
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.appconfiguration.ConfigurationSetting]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """

    @distributed_trace
    def list_configuration_settings(self, *args: Optional[str], **kwargs: Any) -> AsyncItemPaged[ConfigurationSetting]:
        accept_datetime = kwargs.pop("accept_datetime", None)
        if isinstance(accept_datetime, datetime):
            accept_datetime = str(accept_datetime)

        select = kwargs.pop("fields", None)
        if select:
            select = ["locked" if x == "read_only" else x for x in select]
        snapshot_name = kwargs.pop("snapshot_name", None)

        if snapshot_name is not None:
            return self._impl.get_key_values(  # type: ignore[return-value]
                snapshot=snapshot_name,
                accept_datetime=accept_datetime,
                select=select,
                cls=lambda objs: [ConfigurationSetting._from_generated(x) for x in objs],
                **kwargs,
            )
        tags = kwargs.pop("tags_filter", None)
        key_filter, kwargs = get_key_filter(*args, **kwargs)
        label_filter, kwargs = get_label_filter(*args, **kwargs)
        command = functools.partial(self._impl.get_key_values_in_one_page, **kwargs)  # type: ignore[attr-defined]
        return AsyncItemPaged(
            command,
            key=key_filter,
            label=label_filter,
            accept_datetime=accept_datetime,
            select=select,
            tags=tags,
            page_iterator_class=ConfigurationSettingPropertiesPagedAsync,
        )

    @distributed_trace_async
    async def get_configuration_setting(
        self,
        key: str,
        label: Optional[str] = None,
        etag: Optional[str] = "*",
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        *,
        accept_datetime: Optional[Union[datetime, str]] = None,
        **kwargs: Any,
    ) -> Union[None, ConfigurationSetting]:
        """Get the matched ConfigurationSetting from Azure App Configuration service

        :param key: Key of the ConfigurationSetting
        :type key: str
        :param label: Label used to identify the ConfigurationSetting. Default is `None`.
        :type label: str or None
        :param etag: Check if the ConfigurationSetting is changed. Set None to skip checking etag
        :type etag: str or None
        :param match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions
        :keyword accept_datetime: Retrieve ConfigurationSetting that existed at this datetime
        :paramtype accept_datetime: ~datetime.datetime or str or None
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
        if isinstance(accept_datetime, datetime):
            accept_datetime = str(accept_datetime)
        try:
            key_value = await self._impl.get_key_value(
                key=key,
                label=label,
                accept_datetime=accept_datetime,
                etag=etag,
                match_condition=match_condition,
                **kwargs,
            )
            return ConfigurationSetting._from_generated(key_value)
        except ResourceNotModifiedError:
            return None

    @distributed_trace_async
    async def add_configuration_setting(
        self, configuration_setting: ConfigurationSetting, **kwargs: Any
    ) -> ConfigurationSetting:
        """Add a ConfigurationSetting instance into the Azure App Configuration service.

        :param configuration_setting: The ConfigurationSetting object to be added
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
        key_value_added = await self._impl._put_key_value(
            entity=key_value,
            key=key_value.key,  # type: ignore
            label=key_value.label,
            match_condition=MatchConditions.IfMissing,
            **kwargs,
        )
        return ConfigurationSetting._from_generated(key_value_added)

    @distributed_trace_async
    async def set_configuration_setting(
        self,
        configuration_setting: ConfigurationSetting,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        *,
        etag: Optional[str] = None,
        **kwargs: Any,
    ) -> ConfigurationSetting:
        """Add or update a ConfigurationSetting.
        If the configuration setting identified by key and label does not exist, this is a create.
        Otherwise this is an update.

        :param configuration_setting: The ConfigurationSetting to be added (if not exists)
            or updated (if exists) to the service
        :type configuration_setting: ~azure.appconfiguration.ConfigurationSetting
        :param match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions
        :keyword etag: Check if the ConfigurationSetting is changed. \
            Will use the value from param configuration_setting if not set.
        :paramtype etag: str or None
        :return: The ConfigurationSetting returned from the service
        :rtype: ~azure.appconfiguration.ConfigurationSetting
        :raises: :class:`~azure.appconfiguration.ResourceReadOnlyError`, \
            :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`, \
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
        key_value = configuration_setting._to_generated()
        error_map: Dict[int, Any] = {409: ResourceReadOnlyError}
        key_value_set = await self._impl._put_key_value(
            entity=key_value,
            key=key_value.key,  # type: ignore
            label=key_value.label,
            etag=etag or configuration_setting.etag,
            match_condition=match_condition,
            error_map=error_map,
            **kwargs,
        )
        return ConfigurationSetting._from_generated(key_value_set)

    @distributed_trace_async
    async def delete_configuration_setting(
        self,
        key: str,
        label: Optional[str] = None,
        *,
        etag: Optional[str] = None,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> Union[None, ConfigurationSetting]:
        """Delete a ConfigurationSetting if it exists

        :param key: Key used to identify the ConfigurationSetting
        :type key: str
        :param label: Label used to identify the ConfigurationSetting. Default is `None`.
        :type label: str
        :keyword etag: Check if the ConfigurationSetting is changed. Set None to skip checking etag
        :paramtype etag: str or None
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: The deleted ConfigurationSetting returned from the service, or None if it doesn't exist.
        :rtype: ~azure.appconfiguration.ConfigurationSetting
        :raises: :class:`~azure.appconfiguration.ResourceReadOnlyError`, \
            :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`, \
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
        error_map: Dict[int, Any] = {409: ResourceReadOnlyError}
        key_value_deleted = await self._impl.delete_key_value(
            key=key,
            label=label,
            etag=etag,
            match_condition=match_condition,
            error_map=error_map,
            **kwargs,
        )
        if key_value_deleted:
            return ConfigurationSetting._from_generated(key_value_deleted)
        return None

    @distributed_trace
    def list_revisions(
        self,
        key_filter: Optional[str] = None,
        label_filter: Optional[str] = None,
        *,
        tags_filter: Optional[List[str]] = None,
        accept_datetime: Optional[Union[datetime, str]] = None,
        fields: Optional[List[Union[str, ConfigurationSettingFields]]] = None,
        **kwargs: Any,
    ) -> AsyncItemPaged[ConfigurationSetting]:
        """
        Find the ConfigurationSetting revision history, optionally filtered by key, label, tags and accept_datetime.
        For more information about supported filters, see
        https://learn.microsoft.com/azure/azure-app-configuration/rest-api-revisions?pivots=v23-11#supported-filters.

        :param key_filter: Filter results based on their keys. '*' can be used as wildcard in the beginning or end
            of the filter.
        :type key_filter: str or None
        :param label_filter: Filter results based on their label. '*' can be used as wildcard in the beginning or end
            of the filter.
        :type label_filter: str or None
        :keyword tags_filter: Filter results based on their tags.
        :paramtype tags_filter: list[str] or None
        :keyword accept_datetime: Retrieve ConfigurationSetting that existed at this datetime
        :paramtype accept_datetime: ~datetime.datetime or str or None
        :keyword fields: Specify which fields to include in the results. If not specified, will include all fields.
            Available fields see :class:`~azure.appconfiguration.ConfigurationSettingFields`.
        :paramtype fields: list[str] or list[~azure.appconfiguration.ConfigurationSettingFields] or None
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
        if isinstance(accept_datetime, datetime):
            accept_datetime = str(accept_datetime)
        if fields:
            fields = ["locked" if x == "read_only" else x for x in fields]

        return self._impl.get_revisions(  # type: ignore[return-value]
            label=label_filter,
            key=key_filter,
            accept_datetime=accept_datetime,
            select=fields,
            tags=tags_filter,
            cls=lambda objs: [ConfigurationSetting._from_generated(x) for x in objs],
            **kwargs,
        )

    @distributed_trace_async
    async def set_read_only(
        self,
        configuration_setting: ConfigurationSetting,
        read_only: bool = True,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> ConfigurationSetting:
        """Set a configuration setting read only

        :param configuration_setting: The ConfigurationSetting to be set read only
        :type configuration_setting: ~azure.appconfiguration.ConfigurationSetting
        :param read_only: Set the read only setting if true, else clear the read only setting
        :type read_only: bool
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
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
        if read_only:
            key_value = await self._impl.put_lock(
                key=configuration_setting.key,
                label=configuration_setting.label,
                etag=configuration_setting.etag,
                match_condition=match_condition,
                **kwargs,
            )
        else:
            key_value = await self._impl.delete_lock(
                key=configuration_setting.key,
                label=configuration_setting.label,
                etag=configuration_setting.etag,
                match_condition=match_condition,
                **kwargs,
            )
        return ConfigurationSetting._from_generated(key_value)

    @distributed_trace
    def list_labels(
        self,
        *,
        name: Optional[str] = None,
        after: Optional[str] = None,
        accept_datetime: Optional[Union[datetime, str]] = None,
        fields: Optional[List[Union[str, LabelFields]]] = None,
        **kwargs: Any,
    ) -> AsyncItemPaged[ConfigurationSettingLabel]:
        """Gets a list of labels.

        :keyword name: A filter for the name of the returned labels. '*' can be used as wildcard
            in the beginning or end of the filter. For more information about supported filters, see
            https://learn.microsoft.com/azure/azure-app-configuration/rest-api-labels?pivots=v23-11#supported-filters.
        :paramtype name: str or None
        :keyword after: Instructs the server to return elements that appear after the element referred to
            by the specified token.
        :paramtype after: str or None
        :keyword accept_datetime: Requests the server to respond with the state of the resource at the
            specified time.
        :paramtype accept_datetime: ~datetime.datetime or str or None
        :keyword fields: Specify which fields to include in the results. If not specified, will include all fields.
            Available fields see :class:`~azure.appconfiguration.LabelFields`.
        :paramtype fields: list[str] or list[~azure.appconfiguration.LabelFields] or None
        :return: An async iterator of labels.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.appconfiguration.ConfigurationSettingLabel]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        if isinstance(accept_datetime, datetime):
            accept_datetime = str(accept_datetime)
        return self._impl.get_labels(  # type: ignore[return-value]
            name=name,
            after=after,
            accept_datetime=accept_datetime,
            select=fields,
            cls=lambda objs: [ConfigurationSettingLabel(name=x.name) for x in objs],
            **kwargs,
        )

    @distributed_trace_async
    async def begin_create_snapshot(
        self,
        name: str,
        filters: List[ConfigurationSettingsFilter],
        *,
        composition_type: Optional[Union[str, SnapshotComposition]] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Any,
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
        :paramtype composition_type: str or ~azure.appconfiguration.SnapshotComposition or None
        :keyword retention_period: The amount of time, in seconds, that a configuration snapshot will remain in the
            archived state before expiring. This property is only writable during the creation of a configuration
            snapshot. If not specified, will set to 2592000(30 days). If specified, should be
            in range 3600(1 hour) to 7776000(90 days).
        :paramtype retention_period: int or None
        :keyword tags: The tags of the configuration snapshot.
        :paramtype tags: dict[str, str] or None
        :return: A poller for create configuration snapshot operation. Call `result()` on this object to wait for the
            operation to complete and get the created snapshot.
        :rtype: ~azure.core.polling.LROPoller[~azure.appconfiguration.ConfigurationSnapshot]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        snapshot = ConfigurationSnapshot(
            filters=filters, composition_type=composition_type, retention_period=retention_period, tags=tags
        )
        return cast(
            AsyncLROPoller[ConfigurationSnapshot],
            await self._impl.begin_create_snapshot(
                name=name, entity=snapshot._to_generated(), cls=ConfigurationSnapshot._from_deserialized, **kwargs
            ),
        )

    @distributed_trace_async
    async def archive_snapshot(
        self,
        name: str,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        etag: Optional[str] = None,
        **kwargs: Any,
    ) -> ConfigurationSnapshot:
        """Archive a configuration setting snapshot. It will update the status of a snapshot from "ready" to "archived".
        The retention period will start to count, the snapshot will expire when the entire retention period elapses.

        :param name: The name of the configuration setting snapshot to archive.
        :type name: str
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword etag: Check if the ConfigurationSnapshot is changed. Set None to skip checking etag.
        :paramtype etag: str or None
        :return: The ConfigurationSnapshot returned from the service.
        :rtype: ~azure.appconfiguration.ConfigurationSnapshot
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        generated_snapshot = await self._impl._update_snapshot(
            name=name,
            entity=SnapshotUpdateParameters(status=SnapshotStatus.ARCHIVED),
            etag=etag,
            match_condition=match_condition,
            **kwargs,
        )
        return ConfigurationSnapshot._from_generated(generated_snapshot)

    @distributed_trace_async
    async def recover_snapshot(
        self,
        name: str,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        etag: Optional[str] = None,
        **kwargs: Any,
    ) -> ConfigurationSnapshot:
        """Recover a configuration setting snapshot. It will update the status of a snapshot from "archived" to "ready".

        :param name: The name of the configuration setting snapshot to recover.
        :type name: str
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword etag: Check if the ConfigurationSnapshot is changed. Set None to skip checking etag.
        :paramtype etag: str or None
        :return: The ConfigurationSnapshot returned from the service.
        :rtype: ~azure.appconfiguration.ConfigurationSnapshot
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        generated_snapshot = await self._impl._update_snapshot(
            name=name,
            entity=SnapshotUpdateParameters(status=SnapshotStatus.READY),
            etag=etag,
            match_condition=match_condition,
            **kwargs,
        )
        return ConfigurationSnapshot._from_generated(generated_snapshot)

    @distributed_trace_async
    async def get_snapshot(
        self, name: str, *, fields: Optional[List[Union[str, SnapshotFields]]] = None, **kwargs: Any
    ) -> ConfigurationSnapshot:
        """Get a configuration setting snapshot.

        :param name: The name of the configuration setting snapshot to retrieve.
        :type name: str
        :keyword fields: Specify which fields to include in the results. If not specified, will include all fields.
            Available fields see :class:`~azure.appconfiguration.SnapshotFields`.
        :paramtype fields: list[str] or list[~azure.appconfiguration.SnapshotFields] or None
        :return: The ConfigurationSnapshot returned from the service.
        :rtype: ~azure.appconfiguration.ConfigurationSnapshot
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        generated_snapshot = await self._impl.get_snapshot(name=name, select=fields, **kwargs)
        return ConfigurationSnapshot._from_generated(generated_snapshot)

    @distributed_trace
    def list_snapshots(
        self,
        *,
        name: Optional[str] = None,
        fields: Optional[List[Union[str, SnapshotFields]]] = None,
        status: Optional[List[Union[str, SnapshotStatus]]] = None,
        **kwargs: Any,
    ) -> AsyncItemPaged[ConfigurationSnapshot]:
        """List the configuration setting snapshots stored in the configuration service, optionally filtered by
        snapshot name, snapshot status and fields to present in return.

        :keyword name: Filter results based on snapshot name.
        :paramtype name: str or None
        :keyword fields: Specify which fields to include in the results. If not specified, will include all fields.
            Available fields see :class:`~azure.appconfiguration.SnapshotFields`.
        :paramtype fields: list[str] or list[~azure.appconfiguration.SnapshotFields] or None
        :keyword status: Filter results based on snapshot keys. Available status see
            :class:`~azure.appconfiguration.SnapshotStatus`.
        :paramtype status: list[str] or list[~azure.appconfiguration.SnapshotStatus] or None
        :return: An iterator of :class:`~azure.appconfiguration.ConfigurationSnapshot`
        :rtype: ~azure.core.paging.ItemPaged[~azure.appconfiguration.ConfigurationSnapshot]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        return self._impl.get_snapshots(  # type: ignore[return-value]
            name=name,
            select=fields,
            status=status,
            cls=lambda objs: [ConfigurationSnapshot._from_generated(x) for x in objs],
            **kwargs,
        )

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
