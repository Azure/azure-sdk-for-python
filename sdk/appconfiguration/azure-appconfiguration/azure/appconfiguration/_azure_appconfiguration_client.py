# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import binascii
import sys
from typing import Any, Dict, List, Mapping, Optional, Union, cast
from azure.core import MatchConditions
from azure.core.paging import ItemPaged
from azure.core.credentials import TokenCredential
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import (  # pylint:disable=non-abstract-transport-import,no-name-in-module
    RequestsTransport,
)
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    BearerTokenCredentialPolicy,
    ContentDecodePolicy,
    RequestIdPolicy,
)
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceNotModifiedError,
)
from azure.core.utils import CaseInsensitiveDict
from ._azure_appconfiguration_error import ResourceReadOnlyError
from ._azure_appconfiguration_requests import AppConfigRequestsCredentialsPolicy
from ._azure_appconfiguration_credential import AppConfigConnectionStringCredential
from ._generated import AzureAppConfiguration
from ._generated._configuration import AzureAppConfigurationConfiguration
from ._generated.models import SnapshotStatus, SnapshotUpdateParameters
from ._models import ConfigurationSetting, ConfigurationSettingFilter, Snapshot
from ._utils import (
    get_endpoint_from_connection_string,
    prep_if_match,
    prep_if_none_match,
)
from ._sync_token import SyncTokenPolicy
from ._user_agent import USER_AGENT

if sys.version_info >= (3, 8):
    from typing import Literal  # pylint: disable=no-name-in-module, ungrouped-imports
else:
    from typing_extensions import Literal  # type: ignore  # pylint: disable=ungrouped-imports


class AzureAppConfigurationClient:
    """Represents a client that calls restful API of Azure App Configuration service.

    :param str base_url: Base url of the service.
    :param credential: An object which can provide secrets for the app configuration service
    :type credential: ~azure.appconfiguration.AppConfigConnectionStringCredential
        or ~azure.core.credentials.TokenCredential
    :keyword api_version: Api Version. Default value is "2022-11-01-preview". Note that overriding this default
        value may result in unsupported behavior.
    :paramtype api_version: str

    """

    # pylint:disable=protected-access
    def __init__(self, base_url: str, credential: TokenCredential, **kwargs) -> None:
        try:
            if not base_url.lower().startswith("http"):
                base_url = "https://" + base_url
        except AttributeError as exc:
            raise ValueError("Base URL must be a string.") from exc

        if not credential:
            raise ValueError("Missing credential")

        self._credential_scopes = base_url.strip("/") + "/.default"

        self._config = AzureAppConfigurationConfiguration(base_url, credential_scopes=self._credential_scopes, **kwargs)
        self._config.user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)
        self._sync_token_policy = SyncTokenPolicy()

        pipeline = kwargs.get("pipeline")

        if pipeline is None:
            aad_mode = not isinstance(credential, AppConfigConnectionStringCredential)
            pipeline = self._create_appconfig_pipeline(
                credential=credential, aad_mode=aad_mode, base_url=base_url, **kwargs
            )

        self._impl = AzureAppConfiguration(
            base_url, pipeline=pipeline, credential_scopes=self._credential_scopes, **kwargs
        )

    @classmethod
    def from_connection_string(cls, connection_string: str, **kwargs) -> "AzureAppConfigurationClient":
        """Create AzureAppConfigurationClient from a Connection String.

        :param str connection_string: Connection String
            (one of the access keys of the Azure App Configuration resource)
            used to access the Azure App Configuration.
        :return: An AzureAppConfigurationClient authenticated with the connection string
        :rtype: ~azure.appconfiguration.AzureAppConfigurationClient

        Example

        .. code-block:: python

            from azure.appconfiguration import AzureAppConfigurationClient
            connection_str = "<my connection string>"
            client = AzureAppConfigurationClient.from_connection_string(connection_str)
        """
        base_url = "https://" + get_endpoint_from_connection_string(connection_string)
        return cls(
            credential=AppConfigConnectionStringCredential(connection_string),  # type: ignore
            base_url=base_url,
            **kwargs
        )

    def _create_appconfig_pipeline(self, credential, base_url=None, aad_mode=False, **kwargs):
        transport = kwargs.get("transport")
        policies = kwargs.get("policies")

        if policies is None:  # [] is a valid policy list
            if aad_mode:
                scope = base_url.strip("/") + "/.default"
                if hasattr(credential, "get_token"):
                    credential_policy = BearerTokenCredentialPolicy(credential, scope)
                else:
                    raise TypeError(
                        "Please provide an instance from azure-identity "
                        "or a class that implements the 'get_token protocol"
                    )
            else:
                credential_policy = AppConfigRequestsCredentialsPolicy(credential)
            policies = [
                RequestIdPolicy(**kwargs),
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
            transport = RequestsTransport(**kwargs)

        return Pipeline(transport, policies)

    @distributed_trace
    def list_configuration_settings(
        self, key_filter: Optional[str] = None, label_filter: Optional[str] = None, **kwargs
    ) -> ItemPaged[ConfigurationSetting]:
        """List the configuration settings stored in the configuration service, optionally filtered by
        key, label and accept_datetime.

        :param key_filter: filter results based on their keys. '*' can be
            used as wildcard in the beginning or end of the filter
        :type key_filter: str
        :param label_filter: filter results based on their label. '*' can be
            used as wildcard in the beginning or end of the filter
        :type label_filter: str
        :keyword str accept_datetime: retrieve ConfigurationSetting existed at this datetime
        :keyword list[str] fields: specify which fields to include in the results. Leave None to include all fields
        :return: An iterator of :class:`~azure.appconfiguration.ConfigurationSetting`
        :rtype: ~azure.core.paging.ItemPaged[~azure.appconfiguration.ConfigurationSetting]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`

        Example

        .. code-block:: python

            from datetime import datetime, timedelta

            accept_datetime = datetime.utcnow() + timedelta(days=-1)

            all_listed = client.list_configuration_settings()
            for item in all_listed:
                pass  # do something

            filtered_listed = client.list_configuration_settings(
                label_filter="Labe*", key_filter="Ke*", accept_datetime=str(accept_datetime)
            )
            for item in filtered_listed:
                pass  # do something
        """
        select = kwargs.pop("fields", None)
        if select:
            select = ["locked" if x == "read_only" else x for x in select]

        try:
            return self._impl.get_key_values(  # type: ignore
                label=label_filter,
                key=key_filter,
                select=select,
                cls=lambda objs: [ConfigurationSetting._from_generated(x) for x in objs],
                **kwargs
            )
        except binascii.Error as exc:
            raise binascii.Error("Connection string secret has incorrect padding") from exc

    @distributed_trace
    def get_configuration_setting(
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

            fetched_config_setting = client.get_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """
        error_map = {}  # type: Dict[int, Any]
        if match_condition == MatchConditions.IfNotModified:
            error_map.update({412: ResourceModifiedError})
        if match_condition == MatchConditions.IfPresent:
            error_map.update({412: ResourceNotFoundError})
        if match_condition == MatchConditions.IfMissing:
            error_map.update({412: ResourceExistsError})

        try:
            key_value = self._impl.get_key_value(
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

    @distributed_trace
    def add_configuration_setting(self, configuration_setting: ConfigurationSetting, **kwargs) -> ConfigurationSetting:
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

            config_setting = ConfigurationSetting(
                key="MyKey",
                label="MyLabel",
                value="my value",
                content_type="my content type",
                tags={"my tag": "my tag value"}
            )
            added_config_setting = client.add_configuration_setting(config_setting)
        """
        key_value = configuration_setting._to_generated()
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))  # type: Mapping[str, Any]
        error_map = {412: ResourceExistsError}
        try:
            key_value_added = self._impl.put_key_value(
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

    @distributed_trace
    def set_configuration_setting(
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

            config_setting = ConfigurationSetting(
                key="MyKey",
                label="MyLabel",
                value="my set value",
                content_type="my set content type",
                tags={"my set tag": "my set tag value"}
            )
            returned_config_setting = client.set_configuration_setting(config_setting)
        """
        key_value = configuration_setting._to_generated()
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))  # type: Mapping[str, Any]
        error_map = {409: ResourceReadOnlyError}  # type: Dict[int, Any]
        if match_condition == MatchConditions.IfNotModified:
            error_map.update({412: ResourceModifiedError})
        if match_condition == MatchConditions.IfModified:
            error_map.update({412: ResourceNotModifiedError})
        if match_condition == MatchConditions.IfPresent:
            error_map.update({412: ResourceNotFoundError})
        if match_condition == MatchConditions.IfMissing:
            error_map.update({412: ResourceExistsError})

        try:
            key_value_set = self._impl.put_key_value(
                entity=key_value,
                key=key_value.key,  # type: ignore
                label=key_value.label,
                if_match=prep_if_match(configuration_setting.etag, match_condition),
                if_none_match=prep_if_none_match(configuration_setting.etag, match_condition),
                headers=custom_headers,
                error_map=error_map,
            )
            return ConfigurationSetting._from_generated(key_value_set)
        except binascii.Error as exc:
            raise binascii.Error("Connection string secret has incorrect padding") from exc

    @distributed_trace
    def delete_configuration_setting(  # pylint:disable=delete-operation-wrong-return-type
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

            deleted_config_setting = client.delete_configuration_setting(
                key="MyKey", label="MyLabel"
            )
        """
        etag = kwargs.pop("etag", None)
        match_condition = kwargs.pop("match_condition", MatchConditions.Unconditionally)
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))  # type: Mapping[str, Any]
        error_map = {409: ResourceReadOnlyError}  # type: Dict[int, Any]
        if match_condition == MatchConditions.IfNotModified:
            error_map.update({412: ResourceModifiedError})
        if match_condition == MatchConditions.IfModified:
            error_map.update({412: ResourceNotModifiedError})
        if match_condition == MatchConditions.IfPresent:
            error_map.update({412: ResourceNotFoundError})
        if match_condition == MatchConditions.IfMissing:
            error_map.update({412: ResourceExistsError})

        try:
            key_value_deleted = self._impl.delete_key_value(
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
    ) -> ItemPaged[ConfigurationSetting]:
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
        :return: An iterator of :class:`~azure.appconfiguration.ConfigurationSetting`
        :rtype: ~azure.core.paging.ItemPaged[~azure.appconfiguration.ConfigurationSetting]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`, \
            :class:`~azure.core.exceptions.ClientAuthenticationError`

        Example

        .. code-block:: python

            from datetime import datetime, timedelta

            accept_datetime = datetime.utcnow() + timedelta(days=-1)

            all_revisions = client.list_revisions()
            for item in all_revisions:
                pass  # do something

            filtered_revisions = client.list_revisions(
                label_filter="Labe*", key_filter="Ke*", accept_datetime=str(accept_datetime)
            )
            for item in filtered_revisions:
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

    @distributed_trace
    def set_read_only(
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

            config_setting = client.get_configuration_setting(
                key="MyKey", label="MyLabel"
            )

            read_only_config_setting = client.set_read_only(config_setting)
            read_only_config_setting = client.set_read_only(config_setting, read_only=False)
        """
        error_map = {}  # type: Dict[int, Any]
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
                key_value = self._impl.put_lock(
                    key=configuration_setting.key,
                    label=configuration_setting.label,
                    if_match=prep_if_match(configuration_setting.etag, match_condition),
                    if_none_match=prep_if_none_match(configuration_setting.etag, match_condition),
                    error_map=error_map,
                    **kwargs
                )
            else:
                key_value = self._impl.delete_lock(
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

    @distributed_trace
    def begin_create_snapshot(
        self,
        name: str,
        filters: List[ConfigurationSettingFilter],
        *,
        composition_type: Optional[Literal["key", "key_label"]] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> LROPoller[Snapshot]:
        """Create a snapshot of the configuration settings.

        :param name: The name of the snapshot to create.
        :type name: str
        :param filters: A list of filters used to filter the configuration settings by key field and label field
            included in the snapshot.
        :type filters: list[~azure.appconfiguration.ConfigurationSettingFilter]
        :keyword str composition_type: The composition type describes how the key-values
            within the snapshot are composed. Known values are: "key" and "key_label". The "key" composition type
            ensures there are no two key-values containing the same key. The 'key_label' composition type ensures
            there are no two key-values containing the same key and label.
        :keyword int retention_period: The amount of time, in seconds, that a snapshot will remain in the
            archived state before expiring. This property is only writable during the creation of a
            snapshot. If not specified, will set to 2592000(30 days). If specified, should be
            in range 3600(1 hour) to 7776000(90 days).
        :keyword dict[str, str] tags: The tags of the snapshot.
        :return: A poller for create snapshot operation. Call `result()` on this object to wait for the
            operation to complete and get the created snapshot.
        :rtype: ~azure.core.polling.LROPoller[~azure.appconfiguration.Snapshot]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        snapshot = Snapshot(
            filters=filters, composition_type=composition_type, retention_period=retention_period, tags=tags
        )
        try:
            return cast(
                LROPoller[Snapshot],
                self._impl.begin_create_snapshot(
                    name=name, entity=snapshot._to_generated(), cls=Snapshot._from_deserialized, **kwargs
                ),
            )
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")  # pylint: disable=raise-missing-from

    @distributed_trace
    def archive_snapshot(
        self,
        name: str,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        etag: Optional[str] = None,
        **kwargs
    ) -> Snapshot:
        """Archive a configuration setting snapshot. It will update the status of a snapshot from "ready" to "archived".
        The retention period will start to count, the snapshot will expire when the entire retention period elapses.

        :param name: The name of the configuration setting snapshot to archive.
        :type name: str
        :keyword match_condition: The match condition to use upon the etag.
        :type match_condition: ~azure.core.MatchConditions
        :keyword str etag: Check if the Snapshot is changed. Set None to skip checking etag.
        :return: The Snapshot returned from the service.
        :rtype: ~azure.appconfiguration.Snapshot
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        error_map = {}  # type: Dict[int, Any]
        if match_condition == MatchConditions.IfNotModified:
            error_map.update({412: ResourceModifiedError})
        if match_condition == MatchConditions.IfModified:
            error_map.update({412: ResourceNotModifiedError})
        if match_condition == MatchConditions.IfPresent:
            error_map.update({412: ResourceNotFoundError})
        if match_condition == MatchConditions.IfMissing:
            error_map.update({412: ResourceExistsError})
        try:
            generated_snapshot = self._impl.update_snapshot(
                name=name,
                entity=SnapshotUpdateParameters(status=SnapshotStatus.ARCHIVED),
                if_match=prep_if_match(etag, match_condition),
                if_none_match=prep_if_none_match(etag, match_condition),
                error_map=error_map,
                **kwargs
            )
            return Snapshot._from_generated(generated_snapshot)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")  # pylint: disable=raise-missing-from

    @distributed_trace
    def recover_snapshot(
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
        :type match_condition: ~azure.core.MatchConditions
        :keyword str etag: Check if the Snapshot is changed. Set None to skip checking etag.
        :return: The Snapshot returned from the service.
        :rtype: ~azure.appconfiguration.Snapshot
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        error_map = {}  # type: Dict[int, Any]
        if match_condition == MatchConditions.IfNotModified:
            error_map.update({412: ResourceModifiedError})
        if match_condition == MatchConditions.IfModified:
            error_map.update({412: ResourceNotModifiedError})
        if match_condition == MatchConditions.IfPresent:
            error_map.update({412: ResourceNotFoundError})
        if match_condition == MatchConditions.IfMissing:
            error_map.update({412: ResourceExistsError})
        try:
            generated_snapshot = self._impl.update_snapshot(
                name=name,
                entity=SnapshotUpdateParameters(status=SnapshotStatus.READY),
                if_match=prep_if_match(etag, match_condition),
                if_none_match=prep_if_none_match(etag, match_condition),
                error_map=error_map,
                **kwargs
            )
            return Snapshot._from_generated(generated_snapshot)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")  # pylint: disable=raise-missing-from

    @distributed_trace
    def get_snapshot(self, name: str, *, fields: Optional[List[str]] = None, **kwargs) -> Snapshot:
        """Get a configuration setting snapshot.

        :param name: The name of the configuration setting snapshot to retrieve.
        :type name: str
        :keyword list[str] fields: Specify which fields to include in the results. Leave None to include all fields.
        :return: The Snapshot returned from the service.
        :rtype: ~azure.appconfiguration.Snapshot
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        try:
            generated_snapshot = self._impl.get_snapshot(
                name=name, if_match=None, if_none_match=None, select=fields, **kwargs
            )
            return Snapshot._from_generated(generated_snapshot)
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")  # pylint: disable=raise-missing-from

    @distributed_trace
    def list_snapshots(
        self,
        *,
        name: Optional[str] = None,
        fields: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        **kwargs
    ) -> ItemPaged[Snapshot]:
        """List the configuration setting snapshots stored in the configuration service, optionally filtered by
        snapshot name, snapshot status and fields to present in return.

        :keyword str name: Filter results based on snapshot name.
        :keyword list[str] fields: Specify which fields to include in the results. Leave None to include all fields.
        :keyword list[str] status: Filter results based on snapshot keys.
        :return: An iterator of :class:`~azure.appconfiguration.Snapshot`
        :rtype: ~azure.core.paging.ItemPaged[~azure.appconfiguration.Snapshot]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        try:
            return self._impl.get_snapshots(  # type: ignore
                name=name,
                select=fields,
                status=status,
                cls=lambda objs: [Snapshot._from_generated(x) for x in objs],
                **kwargs
            )
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")  # pylint: disable=raise-missing-from

    @distributed_trace
    def list_snapshot_configuration_settings(
        self, name: str, *, accept_datetime: Optional[str] = None, fields: Optional[List[str]] = None, **kwargs
    ) -> ItemPaged[ConfigurationSetting]:
        """List the configuration settings stored under a snapshot in the configuration service, optionally filtered by
        accept_datetime and fields to present in return.

        :param str name: The snapshot name.
        :keyword str accept_datetime: Filter out ConfigurationSetting created after this datetime
        :keyword list[str] fields: Specify which fields to include in the results. Leave None to include all fields
        :return: An iterator of :class:`~azure.appconfiguration.ConfigurationSetting`
        :rtype: ~azure.core.paging.ItemPaged[~azure.appconfiguration.ConfigurationSetting]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        if fields:
            fields = ["locked" if x == "read_only" else x for x in fields]

        try:
            return self._impl.get_key_values(  # type: ignore
                select=fields,
                snapshot=name,
                accept_datetime=accept_datetime,
                cls=lambda objs: [ConfigurationSetting._from_generated(x) for x in objs],
                **kwargs
            )
        except binascii.Error:
            raise binascii.Error("Connection string secret has incorrect padding")  # pylint: disable=raise-missing-from

    def update_sync_token(self, token: str) -> None:
        """Add a sync token to the internal list of tokens.

        :param str token: The sync token to be added to the internal list of tokens
        """
        if not self._sync_token_policy:
            raise AttributeError(
                "Client has no sync token policy, possibly because it was not provided during instantiation."
            )
        self._sync_token_policy.add_token(token)

    def close(self) -> None:
        """Close all connections made by the client"""
        self._impl._client.close()

    def __enter__(self):
        self._impl.__enter__()
        return self

    def __exit__(self, *args):
        self._impl.__exit__(*args)
